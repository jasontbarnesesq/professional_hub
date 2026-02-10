#!/usr/bin/env python3
"""
Hot Folder Watcher

Monitors a designated "drop" folder for new files and automatically
classifies and routes them using the categorization engine.
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    Observer = None

try:
    import yaml
except ImportError:
    yaml = None


class FileRouter(FileSystemEventHandler):
    """Watches for new files and routes them to the correct folder."""

    def __init__(self, rules_path: str, taxonomy_path: str, root_dir: str, audit_path: str):
        super().__init__()
        self.root = Path(root_dir)
        self.audit_path = audit_path

        # Import the categorization module
        sys.path.insert(0, os.path.dirname(__file__))
        from categorize_lib import classify_single_file, load_rules_from_yaml

        self.classify = classify_single_file
        self.rules = load_rules_from_yaml(rules_path)

        # Debounce: track recently processed files
        self._processed = {}

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path

        # Debounce: skip if processed in last 5 seconds
        now = time.time()
        if filepath in self._processed and now - self._processed[filepath] < 5:
            return
        self._processed[filepath] = now

        # Wait for file to finish writing
        time.sleep(2)

        if not os.path.exists(filepath):
            return

        print(f"\nNew file detected: {os.path.basename(filepath)}")

        try:
            result = self.classify(filepath, self.rules)
            dest_folder = self.root / result["target"]
            dest_folder.mkdir(parents=True, exist_ok=True)

            filename = os.path.basename(filepath)
            dest_path = dest_folder / filename

            # Handle collision
            if dest_path.exists():
                stem = Path(filename).stem
                suffix = Path(filename).suffix
                counter = 1
                while dest_path.exists():
                    dest_path = dest_folder / f"{stem}_{counter:03d}{suffix}"
                    counter += 1

            import shutil
            shutil.move(filepath, str(dest_path))

            status = "filed" if result["confidence"] >= 0.70 else "pending_review"

            # Audit trail
            entry = {
                "timestamp": datetime.now().isoformat(),
                "action": "file_routed",
                "source": "hot_folder_watcher",
                "file": filename,
                "original_path": filepath,
                "destination": str(dest_path),
                "rule_matched": result["rule_name"],
                "confidence": result["confidence"],
                "status": status,
            }
            with open(self.audit_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

            print(f"  -> Routed to: {result['target']} (conf: {result['confidence']:.2f})")
            if status == "pending_review":
                print(f"  ** LOW CONFIDENCE — needs manual review **")

        except Exception as e:
            print(f"  Error routing file: {e}", file=sys.stderr)


def watch_folder_polling(watch_dir: str, router: FileRouter, interval: int = 10):
    """Fallback polling watcher when watchdog is not available."""
    print(f"Using polling mode (interval: {interval}s)")
    known_files = set()
    watch = Path(watch_dir)

    while True:
        try:
            current_files = set(str(p) for p in watch.iterdir() if p.is_file())
            new_files = current_files - known_files

            for filepath in new_files:
                # Simulate watchdog event
                class FakeEvent:
                    def __init__(self, path):
                        self.src_path = path
                        self.is_directory = False

                router.on_created(FakeEvent(filepath))

            known_files = current_files
        except Exception as e:
            print(f"Error scanning: {e}", file=sys.stderr)

        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Watch folder and auto-route new files")
    parser.add_argument(
        "--watch-dir",
        default="Practice_Root/09_Inbox/01_Unsorted/",
        help="Directory to watch for new files",
    )
    parser.add_argument(
        "--rules",
        default="taxonomy/classification_rules.yaml",
        help="Path to classification rules YAML",
    )
    parser.add_argument(
        "--taxonomy",
        default="taxonomy/folder_structure.yaml",
        help="Path to taxonomy YAML",
    )
    parser.add_argument(
        "--root",
        default="Practice_Root",
        help="Root directory for organized folders",
    )
    parser.add_argument(
        "--audit",
        default="reports/audit_trail.jsonl",
        help="Path for audit trail log",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=10,
        help="Polling interval in seconds (fallback mode)",
    )
    args = parser.parse_args()

    watch_dir = Path(args.watch_dir)
    watch_dir.mkdir(parents=True, exist_ok=True)

    Path(args.audit).parent.mkdir(parents=True, exist_ok=True)

    router = FileRouter(args.rules, args.taxonomy, args.root, args.audit)

    print(f"Watching: {watch_dir}")
    print("Press Ctrl+C to stop.\n")

    if Observer:
        observer = Observer()
        observer.schedule(router, str(watch_dir), recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    else:
        print("Warning: watchdog not installed. Using polling mode.")
        try:
            watch_folder_polling(str(watch_dir), router, args.poll_interval)
        except KeyboardInterrupt:
            pass

    print("\nWatcher stopped.")


if __name__ == "__main__":
    main()
