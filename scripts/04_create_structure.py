#!/usr/bin/env python3
"""
Create Folder Structure

Reads the taxonomy YAML and creates the full directory tree on disk.
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: pyyaml is required. Install with: pip install pyyaml")
    sys.exit(1)


def create_dirs_from_yaml(node: dict, current_path: Path, dry_run: bool = False):
    """Recursively create directories from YAML structure."""
    for key, value in node.items():
        if key.startswith("_"):
            continue  # Skip metadata keys

        dir_path = current_path / key
        if dry_run:
            print(f"  [DRY RUN] Would create: {dir_path}")
        else:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Write description to .info file if present
        if isinstance(value, dict):
            desc = value.get("_description", "")
            if desc and not dry_run:
                info_file = dir_path / ".folder_info"
                info_file.write_text(f"Description: {desc}\n")

            # Check for children
            children = value.get("children", {})
            if children:
                create_dirs_from_yaml(children, dir_path, dry_run)

            # Create template readme if this is a templated directory
            template = value.get("_template", "")
            if template and not dry_run:
                readme = dir_path / "README_NAMING.md"
                readme.write_text(
                    f"# Naming Convention\n\n"
                    f"Create subdirectories using this pattern:\n\n"
                    f"    {template}\n\n"
                    f"Example: `{template.replace('{', '').replace('}', 'Example')}`\n"
                )


def main():
    parser = argparse.ArgumentParser(description="Create folder structure from YAML taxonomy")
    parser.add_argument(
        "--taxonomy",
        default="taxonomy/folder_structure.yaml",
        help="Path to taxonomy YAML file",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory where structure will be created",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview directory creation without making changes",
    )
    args = parser.parse_args()

    with open(args.taxonomy, "r") as f:
        taxonomy = yaml.safe_load(f)

    root_name = taxonomy.get("root", "Practice_Root")
    root_path = Path(args.root) / root_name
    structure = taxonomy.get("structure", {})

    print(f"Creating folder structure under: {root_path}")
    if args.dry_run:
        print("  (DRY RUN mode)")

    if not args.dry_run:
        root_path.mkdir(parents=True, exist_ok=True)

    create_dirs_from_yaml(structure, root_path, args.dry_run)

    # Count created directories
    if not args.dry_run:
        count = sum(1 for _ in root_path.rglob("*") if _.is_dir())
        print(f"\nCreated {count} directories under {root_path}")
    else:
        print("\nDry run complete. No directories were created.")


if __name__ == "__main__":
    main()
