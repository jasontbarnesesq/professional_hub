#!/usr/bin/env python3
"""
File Migration Script

Reads the categorization plan and moves/copies files to their designated
folders. Includes checksum verification and full audit logging.
"""

import argparse
import csv
import hashlib
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


def sha256_hash(filepath: str) -> str:
    """Compute SHA-256 hash for verification."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            hasher.update(block)
    return hasher.hexdigest()


def safe_destination(dest_dir: Path, filename: str) -> Path:
    """
    Generate a safe destination path, handling filename collisions
    by appending sequential suffixes.
    """
    dest = dest_dir / filename
    if not dest.exists():
        return dest

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    while True:
        new_name = f"{stem}_{counter:03d}{suffix}"
        dest = dest_dir / new_name
        if not dest.exists():
            return dest
        counter += 1


def migrate_files(
    plan_path: str,
    root_dir: str,
    log_path: str,
    dry_run: bool = False,
    skip_review: bool = False,
    copy_mode: bool = True,
):
    """Execute file migration based on the categorization plan."""

    print("Loading categorization plan...")
    with open(plan_path, "r", encoding="utf-8") as f:
        plan = list(csv.DictReader(f))
    print(f"  {len(plan):,} files in plan")

    # Filter out files that need review (unless --skip-review)
    if not skip_review:
        actionable = [r for r in plan if r["needs_review"] == "No"]
        review_count = len(plan) - len(actionable)
        if review_count:
            print(f"  Skipping {review_count:,} files marked for review")
    else:
        actionable = plan

    root = Path(root_dir)
    log_rows = []
    success_count = 0
    error_count = 0
    total_bytes = 0

    iterator = tqdm(actionable, desc="Migrating") if tqdm else actionable

    for record in iterator:
        source = record["source_path"]
        dest_folder = root / record["proposed_destination"]
        filename = record["filename"]
        timestamp = datetime.now().isoformat()

        log_entry = {
            "timestamp": timestamp,
            "source_path": source,
            "destination_path": "",
            "action": "",
            "status": "",
            "checksum_verified": "",
            "error": "",
        }

        if not os.path.exists(source):
            log_entry["status"] = "SKIPPED"
            log_entry["error"] = "Source file not found"
            log_rows.append(log_entry)
            continue

        dest_path = safe_destination(dest_folder, filename)
        log_entry["destination_path"] = str(dest_path)

        if dry_run:
            log_entry["action"] = "DRY_RUN"
            log_entry["status"] = "OK"
            log_rows.append(log_entry)
            success_count += 1
            continue

        try:
            # Create destination directory
            dest_folder.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(source, str(dest_path))
            log_entry["action"] = "COPIED"

            # Verify checksum
            src_hash = sha256_hash(source)
            dst_hash = sha256_hash(str(dest_path))

            if src_hash == dst_hash:
                log_entry["checksum_verified"] = "YES"
                log_entry["status"] = "OK"
                success_count += 1
                total_bytes += int(record.get("size_bytes", 0))

                # If not copy_mode, remove original after verified copy
                if not copy_mode:
                    os.remove(source)
                    log_entry["action"] = "MOVED"
            else:
                log_entry["checksum_verified"] = "FAILED"
                log_entry["status"] = "ERROR"
                log_entry["error"] = "Checksum mismatch after copy"
                error_count += 1
                # Remove bad copy
                os.remove(str(dest_path))

        except Exception as e:
            log_entry["status"] = "ERROR"
            log_entry["error"] = str(e)
            error_count += 1

        log_rows.append(log_entry)

    # Write log
    log = Path(log_path)
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp", "source_path", "destination_path",
                "action", "status", "checksum_verified", "error",
            ],
        )
        writer.writeheader()
        writer.writerows(log_rows)

    # Summary
    total_mb = total_bytes / (1024 * 1024)
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{prefix}Migration Summary:")
    print(f"  Files processed: {len(actionable):,}")
    print(f"  Successful: {success_count:,}")
    print(f"  Errors: {error_count:,}")
    if not dry_run:
        print(f"  Data transferred: {total_mb:,.1f} MB")
    print(f"  Log written to: {log_path}")


def main():
    parser = argparse.ArgumentParser(description="Migrate files to organized folder structure")
    parser.add_argument("--plan", required=True, help="Path to categorization plan CSV")
    parser.add_argument(
        "--root",
        default="Practice_Root",
        help="Root directory for organized structure",
    )
    parser.add_argument(
        "--log",
        default="reports/migration_log.csv",
        help="Path for migration log CSV",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview migration without moving files",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform the migration",
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Move files instead of copying (deletes originals after verification)",
    )
    parser.add_argument(
        "--include-review",
        action="store_true",
        help="Include files marked 'needs_review' in migration",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("Error: Must specify either --dry-run or --execute")
        sys.exit(1)

    migrate_files(
        args.plan,
        args.root,
        args.log,
        dry_run=args.dry_run,
        skip_review=args.include_review,
        copy_mode=not args.move,
    )


if __name__ == "__main__":
    main()
