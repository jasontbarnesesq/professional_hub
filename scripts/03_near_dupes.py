#!/usr/bin/env python3
"""
Near-Duplicate Detection

Identifies files that are similar but not identical using:
- SimHash for text content fingerprinting
- Filename similarity (Levenshtein distance)
- Metadata comparison (similar size, dates, authors)
"""

import argparse
import csv
import os
import re
import sys
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

try:
    import Levenshtein
except ImportError:
    Levenshtein = None
    print("Warning: python-Levenshtein not installed. Using basic similarity.")


# ---- Text extraction helpers ----

def extract_text_pdf(filepath: str, max_chars: int = 5000) -> str:
    """Extract text from PDF."""
    try:
        import PyPDF2
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages[:5]:  # First 5 pages
                text += page.extract_text() or ""
                if len(text) >= max_chars:
                    break
        return text[:max_chars]
    except Exception:
        return ""


def extract_text_docx(filepath: str, max_chars: int = 5000) -> str:
    """Extract text from DOCX."""
    try:
        import docx
        doc = docx.Document(filepath)
        text = "\n".join(p.text for p in doc.paragraphs)
        return text[:max_chars]
    except Exception:
        return ""


def extract_text_plain(filepath: str, max_chars: int = 5000) -> str:
    """Extract text from plain text files."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(max_chars)
    except Exception:
        return ""


def extract_text(filepath: str) -> str:
    """Extract text from a file based on extension."""
    ext = Path(filepath).suffix.lower()
    if ext == ".pdf":
        return extract_text_pdf(filepath)
    elif ext in (".docx", ".doc"):
        return extract_text_docx(filepath)
    elif ext in (".txt", ".md", ".rtf", ".csv"):
        return extract_text_plain(filepath)
    return ""


# ---- Similarity functions ----

def simhash(text: str, hash_bits: int = 64) -> int:
    """Compute SimHash of text."""
    import hashlib

    tokens = re.findall(r"\w+", text.lower())
    if not tokens:
        return 0

    v = [0] * hash_bits
    for token in tokens:
        token_hash = int(hashlib.md5(token.encode()).hexdigest(), 16)
        for i in range(hash_bits):
            if token_hash & (1 << i):
                v[i] += 1
            else:
                v[i] -= 1

    fingerprint = 0
    for i in range(hash_bits):
        if v[i] > 0:
            fingerprint |= 1 << i
    return fingerprint


def hamming_distance(h1: int, h2: int, bits: int = 64) -> int:
    """Count differing bits between two hashes."""
    return bin(h1 ^ h2).count("1")


def simhash_similarity(h1: int, h2: int, bits: int = 64) -> float:
    """Similarity score from SimHash (0.0 to 1.0)."""
    distance = hamming_distance(h1, h2, bits)
    return 1.0 - (distance / bits)


def filename_similarity(name1: str, name2: str) -> float:
    """Compute filename similarity score."""
    if Levenshtein:
        return Levenshtein.ratio(name1.lower(), name2.lower())
    # Basic fallback
    s1, s2 = set(name1.lower()), set(name2.lower())
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


def size_similarity(size1: int, size2: int) -> float:
    """Compute file size similarity (0.0 to 1.0)."""
    if size1 == 0 and size2 == 0:
        return 1.0
    larger = max(size1, size2)
    if larger == 0:
        return 0.0
    return 1.0 - abs(size1 - size2) / larger


def combined_similarity(record1: dict, record2: dict, text_cache: dict) -> float:
    """
    Compute weighted combined similarity score.

    Weights:
    - Content SimHash: 0.50
    - Filename: 0.30
    - File size: 0.20
    """
    fp1, fp2 = record1["filepath"], record2["filepath"]

    # Content similarity
    h1 = text_cache.get(fp1, 0)
    h2 = text_cache.get(fp2, 0)
    if h1 and h2:
        content_sim = simhash_similarity(h1, h2)
    else:
        content_sim = 0.0

    # Filename similarity
    fn_sim = filename_similarity(record1["filename"], record2["filename"])

    # Size similarity
    sz_sim = size_similarity(int(record1["size_bytes"]), int(record2["size_bytes"]))

    return 0.50 * content_sim + 0.30 * fn_sim + 0.20 * sz_sim


def find_near_duplicates(records: list, threshold: float = 0.85) -> list:
    """Find near-duplicate pairs above the similarity threshold."""

    # Filter to document types only
    doc_extensions = {".pdf", ".docx", ".doc", ".txt", ".rtf", ".md"}
    doc_records = [
        r for r in records
        if Path(r["filepath"]).suffix.lower() in doc_extensions
        and r["sha256"] != "ERROR"
    ]
    print(f"  Analyzing {len(doc_records):,} document files for near-duplicates...")

    # Pre-compute SimHash for all documents
    print("  Extracting text and computing fingerprints...")
    text_cache = {}
    iterator = tqdm(doc_records, desc="  Fingerprinting") if tqdm else doc_records
    for record in iterator:
        fp = record["filepath"]
        if os.path.exists(fp):
            text = extract_text(fp)
            text_cache[fp] = simhash(text) if text else 0

    # Compare pairs (group by extension and similar size to reduce comparisons)
    print("  Comparing file pairs...")
    pairs = []
    seen_hashes = set()

    # Group by extension for efficiency
    from collections import defaultdict
    ext_groups = defaultdict(list)
    for r in doc_records:
        ext = Path(r["filepath"]).suffix.lower()
        ext_groups[ext].append(r)

    for ext, group in ext_groups.items():
        n = len(group)
        for i in range(n):
            for j in range(i + 1, min(i + 500, n)):  # Limit comparisons per file
                r1, r2 = group[i], group[j]

                # Skip if same hash (exact duplicate, handled elsewhere)
                if r1["sha256"] == r2["sha256"]:
                    continue

                sim = combined_similarity(r1, r2, text_cache)
                if sim >= threshold:
                    pair_key = tuple(sorted([r1["filepath"], r2["filepath"]]))
                    if pair_key not in seen_hashes:
                        seen_hashes.add(pair_key)
                        pairs.append(
                            {
                                "file_1": r1["filepath"],
                                "file_2": r2["filepath"],
                                "similarity_score": round(sim, 3),
                                "file_1_size": r1["size_bytes"],
                                "file_2_size": r2["size_bytes"],
                                "file_1_modified": r1["modified_date"],
                                "file_2_modified": r2["modified_date"],
                                "action": "REVIEW",
                            }
                        )

    return pairs


def main():
    parser = argparse.ArgumentParser(description="Detect near-duplicate files")
    parser.add_argument("--inventory", required=True, help="Path to inventory CSV")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Similarity threshold 0.0-1.0 (default: 0.85)",
    )
    parser.add_argument(
        "--report",
        default="reports/near_dupes_review.csv",
        help="Output report path",
    )
    args = parser.parse_args()

    print("Loading inventory...")
    with open(args.inventory, "r", encoding="utf-8") as f:
        records = list(csv.DictReader(f))
    print(f"  Loaded {len(records):,} records")

    pairs = find_near_duplicates(records, args.threshold)

    # Write report
    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    with open(report, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "file_1", "file_2", "similarity_score",
                "file_1_size", "file_2_size",
                "file_1_modified", "file_2_modified",
                "action",
            ],
        )
        writer.writeheader()
        writer.writerows(pairs)

    print(f"\nNear-duplicate pairs found: {len(pairs):,}")
    print(f"Report written to: {args.report}")
    if pairs:
        print("Review the report and mark each row as KEEP, REMOVE, or MERGE.")


if __name__ == "__main__":
    main()
