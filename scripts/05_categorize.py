#!/usr/bin/env python3
"""
Automated File Categorization

Analyzes each file from the inventory and proposes a destination folder
based on classification rules (filename patterns, content keywords,
extension mapping, metadata, and email parsing).
"""

import argparse
import csv
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: pyyaml is required. Install with: pip install pyyaml")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


# ---- Text extraction (reused from 03_near_dupes.py) ----

def extract_text(filepath: str, max_chars: int = 5000) -> str:
    """Extract text from a file based on extension."""
    ext = Path(filepath).suffix.lower()
    try:
        if ext == ".pdf":
            import PyPDF2
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages[:3]:
                    text += page.extract_text() or ""
                    if len(text) >= max_chars:
                        break
            return text[:max_chars]
        elif ext in (".docx",):
            import docx
            doc = docx.Document(filepath)
            return "\n".join(p.text for p in doc.paragraphs)[:max_chars]
        elif ext in (".txt", ".md", ".rtf", ".csv", ".html", ".htm"):
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(max_chars)
        elif ext in (".eml",):
            return parse_email_text(filepath)
        elif ext in (".msg",):
            return parse_msg_text(filepath)
    except Exception:
        pass
    return ""


def parse_email_text(filepath: str) -> str:
    """Parse .eml file and return combined metadata + body text."""
    import email
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            msg = email.message_from_file(f)
        parts = [
            f"From: {msg.get('From', '')}",
            f"To: {msg.get('To', '')}",
            f"Subject: {msg.get('Subject', '')}",
            f"Date: {msg.get('Date', '')}",
        ]
        # Get body
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True)
                    if body:
                        parts.append(body.decode("utf-8", errors="ignore"))
                    break
        else:
            body = msg.get_payload(decode=True)
            if body:
                parts.append(body.decode("utf-8", errors="ignore"))
        return "\n".join(parts)[:5000]
    except Exception:
        return ""


def parse_msg_text(filepath: str) -> str:
    """Parse Outlook .msg file."""
    try:
        import extract_msg
        msg = extract_msg.Message(filepath)
        return f"From: {msg.sender}\nTo: {msg.to}\nSubject: {msg.subject}\n{msg.body}"[:5000]
    except Exception:
        return ""


# ---- Client/Matter detection ----

# Common patterns for client IDs and matter numbers
CLIENT_PATTERNS = [
    r"(?i)client[_\s-]*(?:id|no|num)?[_\s:#-]*(\w{3,20})",
    r"(?i)matter[_\s-]*(?:id|no|num)?[_\s:#-]*(\w{3,20})",
    r"\b([A-Z]{2,5}-\d{3,6})\b",  # e.g., ACME-12345
]


def detect_client_matter(filename: str, text: str) -> tuple:
    """
    Attempt to detect client ID and matter ID from filename and text.
    Returns (client_id, matter_id) or (None, None).
    """
    combined = f"{filename}\n{text[:2000]}"
    client_id = None
    matter_id = None

    for pattern in CLIENT_PATTERNS:
        match = re.search(pattern, combined)
        if match:
            if client_id is None:
                client_id = match.group(1)
            elif matter_id is None:
                matter_id = match.group(1)
                break

    return client_id, matter_id


# ---- Classification engine ----

def load_rules(rules_path: str) -> list:
    """Load classification rules from YAML."""
    with open(rules_path, "r") as f:
        data = yaml.safe_load(f)
    return data.get("rules", [])


def classify_file(record: dict, rules: list, text_cache: dict) -> dict:
    """
    Classify a single file against all rules.
    Returns the best match with highest confidence.
    """
    filepath = record["filepath"]
    filename = record["filename"]
    ext = record["extension"]
    text = text_cache.get(filepath, "")

    best_match = None
    best_confidence = 0.0

    for rule in rules:
        rule_type = rule["type"]
        pattern = rule["pattern"]
        confidence = rule["confidence"]

        matched = False

        if rule_type == "filename":
            matched = bool(re.search(pattern, filename))
        elif rule_type == "extension":
            matched = bool(re.search(pattern, ext))
        elif rule_type == "content" and text:
            matched = bool(re.search(pattern, text))
        elif rule_type == "email" and ext in (".eml", ".msg"):
            matched = True  # Email catch-all with conditions
        elif rule_type == "metadata":
            matched = bool(re.search(pattern, text))

        if matched and confidence > best_confidence:
            # Resolve client/matter placeholders
            target = rule["target"]
            if "{client}" in target or "{matter}" in target:
                client_id, matter_id = detect_client_matter(filename, text)
                if client_id:
                    target = target.replace("{client}", client_id)
                else:
                    target = target.replace("{client}", "_UNKNOWN_CLIENT")
                if matter_id:
                    target = target.replace("{matter}", matter_id)
                else:
                    target = target.replace("{matter}", "_UNKNOWN_MATTER")

            best_match = {
                "rule_name": rule["name"],
                "target": target,
                "confidence": confidence,
            }
            best_confidence = confidence

    if best_match is None:
        best_match = {
            "rule_name": "unclassified",
            "target": "09_Inbox/01_Unsorted/",
            "confidence": 0.0,
        }

    return best_match


def categorize_files(
    inventory_path: str,
    rules_path: str,
    taxonomy_path: str,
    output_path: str,
    extract_content: bool = True,
):
    """Categorize all files and write the plan CSV."""

    print("Loading inventory...")
    with open(inventory_path, "r", encoding="utf-8") as f:
        records = list(csv.DictReader(f))
    print(f"  {len(records):,} files loaded")

    print("Loading classification rules...")
    rules = load_rules(rules_path)
    print(f"  {len(rules)} rules loaded")

    # Extract text for content-based rules
    text_cache = {}
    if extract_content:
        print("Extracting text content for classification...")
        content_extensions = {".pdf", ".docx", ".doc", ".txt", ".md", ".rtf",
                             ".eml", ".msg", ".html", ".htm"}
        content_records = [
            r for r in records
            if r["extension"].lower() in content_extensions
        ]
        iterator = tqdm(content_records, desc="  Extracting text") if tqdm else content_records
        for record in iterator:
            fp = record["filepath"]
            if os.path.exists(fp):
                text_cache[fp] = extract_text(fp)

    # Classify each file
    print("Classifying files...")
    plan_rows = []
    iterator = tqdm(records, desc="  Classifying") if tqdm else records

    for record in iterator:
        match = classify_file(record, rules, text_cache)
        needs_review = "Yes" if match["confidence"] < 0.70 else "No"

        plan_rows.append(
            {
                "source_path": record["filepath"],
                "filename": record["filename"],
                "extension": record["extension"],
                "size_bytes": record["size_bytes"],
                "proposed_destination": match["target"],
                "confidence": match["confidence"],
                "rule_matched": match["rule_name"],
                "needs_review": needs_review,
            }
        )

    # Write plan
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "source_path", "filename", "extension", "size_bytes",
                "proposed_destination", "confidence", "rule_matched", "needs_review",
            ],
        )
        writer.writeheader()
        writer.writerows(plan_rows)

    # Summary
    high_conf = sum(1 for r in plan_rows if float(r["confidence"]) >= 0.70)
    low_conf = sum(1 for r in plan_rows if 0 < float(r["confidence"]) < 0.70)
    unclassified = sum(1 for r in plan_rows if float(r["confidence"]) == 0)

    print(f"\nCategorization Summary:")
    print(f"  High confidence (>= 0.70): {high_conf:,}")
    print(f"  Low confidence (review needed): {low_conf:,}")
    print(f"  Unclassified: {unclassified:,}")
    print(f"  Plan written to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Categorize files into taxonomy folders")
    parser.add_argument("--inventory", required=True, help="Path to inventory CSV")
    parser.add_argument(
        "--taxonomy",
        default="taxonomy/folder_structure.yaml",
        help="Path to taxonomy YAML",
    )
    parser.add_argument(
        "--rules",
        default="taxonomy/classification_rules.yaml",
        help="Path to classification rules YAML",
    )
    parser.add_argument(
        "--output",
        default="reports/categorization_plan.csv",
        help="Output categorization plan CSV",
    )
    parser.add_argument(
        "--skip-content",
        action="store_true",
        help="Skip text extraction (faster, filename/extension only)",
    )
    args = parser.parse_args()

    categorize_files(
        args.inventory,
        args.rules,
        args.taxonomy,
        args.output,
        extract_content=not args.skip_content,
    )


if __name__ == "__main__":
    main()
