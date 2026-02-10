#!/usr/bin/env python3
"""
File System Inventory Scanner

Crawls specified directories and produces a CSV manifest of every file with:
- Full path, filename, extension
- File size, created date, modified date
- SHA-256 hash (for deduplication)
- MIME type
"""

import argparse
import csv
import hashlib
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import magic
except ImportError:
    magic = None
    print("Warning: python-magic not installed. MIME detection will use extension only.")

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


def sha256_hash(filepath: str, block_size: int = 65536) -> str:
    """Compute SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for block in iter(lambda: f.read(block_size), b""):
                hasher.update(block)
        return hasher.hexdigest()
    except (PermissionError, OSError) as e:
        print(f"  Warning: Cannot read {filepath}: {e}", file=sys.stderr)
        return "ERROR"


def get_mime_type(filepath: str) -> str:
    """Detect MIME type of a file."""
    if magic:
        try:
            return magic.from_file(filepath, mime=True)
        except Exception:
            pass
    # Fallback: guess from extension
    import mimetypes
    mime, _ = mimetypes.guess_type(filepath)
    return mime or "application/octet-stream"


def get_file_dates(filepath: str) -> tuple:
    """Return (created_date, modified_date) as ISO strings."""
    stat = os.stat(filepath)
    modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
    # st_birthtime not available on all platforms; fall back to ctime
    try:
        created = datetime.fromtimestamp(stat.st_birthtime).isoformat()
    except AttributeError:
        created = datetime.fromtimestamp(stat.st_ctime).isoformat()
    return created, modified


def scan_directories(source_dirs: list, output_path: str, skip_hidden: bool = True):
    """Scan directories and write inventory CSV."""

    # First pass: count files for progress bar
    print("Counting files...")
    all_files = []
    for source_dir in source_dirs:
        source = Path(source_dir)
        if not source.exists():
            print(f"Warning: {source_dir} does not exist, skipping.", file=sys.stderr)
            continue
        for root, dirs, files in os.walk(source):
            if skip_hidden:
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                files = [f for f in files if not f.startswith(".")]
            for filename in files:
                all_files.append(os.path.join(root, filename))

    total = len(all_files)
    print(f"Found {total:,} files to inventory.")

    # Second pass: gather metadata
    fieldnames = [
        "filepath",
        "filename",
        "extension",
        "size_bytes",
        "created_date",
        "modified_date",
        "sha256",
        "mime_type",
    ]

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    iterator = tqdm(all_files, desc="Scanning") if tqdm else all_files

    with open(output, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for filepath in iterator:
            try:
                stat = os.stat(filepath)
                created, modified = get_file_dates(filepath)
                ext = Path(filepath).suffix.lower()

                row = {
                    "filepath": filepath,
                    "filename": os.path.basename(filepath),
                    "extension": ext,
                    "size_bytes": stat.st_size,
                    "created_date": created,
                    "modified_date": modified,
                    "sha256": sha256_hash(filepath),
                    "mime_type": get_mime_type(filepath),
                }
                writer.writerow(row)
            except (PermissionError, OSError) as e:
                print(f"  Skipping {filepath}: {e}", file=sys.stderr)

    print(f"\nInventory written to {output} ({total:,} files)")


def main():
    parser = argparse.ArgumentParser(description="Scan file system and create inventory CSV")
    parser.add_argument(
        "--source-dirs",
        nargs="+",
        required=True,
        help="One or more directories to scan",
    )
    parser.add_argument(
        "--output",
        default="inventory.csv",
        help="Output CSV file path (default: inventory.csv)",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and directories",
    )
    args = parser.parse_args()

    scan_directories(args.source_dirs, args.output, skip_hidden=not args.include_hidden)


if __name__ == "__main__":
    main()
