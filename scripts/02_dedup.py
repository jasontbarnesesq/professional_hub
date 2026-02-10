#!/usr/bin/env python3
"""
Exact Duplicate Detection and Removal

Reads the inventory CSV, groups files by SHA-256 hash, identifies duplicates,
keeps the best candidate, and moves duplicates to a staging directory.
"""

import argparse
import csv
import os
import shutil
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


def load_inventory(inventory_path: str) -> list:
    """Load inventory CSV into list of dicts."""
    with open(inventory_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def find_exact_duplicates(records: list) -> dict:
    """Group records by SHA-256 hash. Return only groups with >1 file."""
    hash_groups = defaultdict(list)
    for record in records:
        h = record["sha256"]
        if h and h != "ERROR":
            hash_groups[h].append(record)
    return {h: files for h, files in hash_groups.items() if len(files) > 1}


def select_keeper(file_group: list) -> tuple:
    """
    Select the file to keep from a group of duplicates.

    Priority:
    1. Most recently modified
    2. Shortest path (likely more organized location)
    """
    sorted_group = sorted(
        file_group,
        key=lambda r: (r["modified_date"], -len(r["filepath"])),
        reverse=True,
    )
    keeper = sorted_group[0]
    duplicates = sorted_group[1:]
    return keeper, duplicates


def move_duplicates(
    duplicate_groups: dict,
    duplicates_dir: str,
    report_path: str,
    dry_run: bool = False,
):
    """Move duplicate files to staging directory and write report."""
    dup_dir = Path(duplicates_dir)
    dup_dir.mkdir(parents=True, exist_ok=True)

    report_rows = []
    total_saved = 0
    total_dupes = 0

    groups = duplicate_groups.items()
    iterator = tqdm(groups, desc="Processing duplicates") if tqdm else groups

    for sha_hash, file_group in iterator:
        keeper, duplicates = select_keeper(file_group)

        for dup in duplicates:
            total_dupes += 1
            size = int(dup["size_bytes"])
            total_saved += size

            # Create unique destination path preserving some context
            rel_path = dup["filepath"].lstrip("/").replace("/", "__")
            dest = dup_dir / rel_path

            report_rows.append(
                {
                    "sha256": sha_hash,
                    "kept_file": keeper["filepath"],
                    "duplicate_file": dup["filepath"],
                    "duplicate_size_bytes": size,
                    "moved_to": str(dest) if not dry_run else "(dry run)",
                    "action": "MOVE" if not dry_run else "DRY_RUN",
                }
            )

            if not dry_run:
                try:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(dup["filepath"], str(dest))
                except (PermissionError, OSError) as e:
                    print(f"  Error moving {dup['filepath']}: {e}", file=sys.stderr)
                    report_rows[-1]["action"] = f"ERROR: {e}"

    # Write report
    report = Path(report_path)
    report.parent.mkdir(parents=True, exist_ok=True)
    with open(report, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "sha256",
                "kept_file",
                "duplicate_file",
                "duplicate_size_bytes",
                "moved_to",
                "action",
            ],
        )
        writer.writeheader()
        writer.writerows(report_rows)

    saved_mb = total_saved / (1024 * 1024)
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{prefix}Deduplication Summary:")
    print(f"  Duplicate groups found: {len(duplicate_groups):,}")
    print(f"  Duplicate files: {total_dupes:,}")
    print(f"  Space recoverable: {saved_mb:,.1f} MB")
    print(f"  Report written to: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="Find and remove exact duplicate files")
    parser.add_argument("--inventory", required=True, help="Path to inventory CSV")
    parser.add_argument(
        "--duplicates-dir",
        default="_duplicates",
        help="Directory to move duplicates to (default: _duplicates)",
    )
    parser.add_argument(
        "--report",
        default="reports/dedup_report.csv",
        help="Path for deduplication report CSV",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without moving files",
    )
    args = parser.parse_args()

    print("Loading inventory...")
    records = load_inventory(args.inventory)
    print(f"  Loaded {len(records):,} records")

    print("Finding exact duplicates...")
    duplicates = find_exact_duplicates(records)
    print(f"  Found {len(duplicates):,} duplicate groups")

    if not duplicates:
        print("No duplicates found. Exiting.")
        return

    move_duplicates(duplicates, args.duplicates_dir, args.report, args.dry_run)


if __name__ == "__main__":
    main()
