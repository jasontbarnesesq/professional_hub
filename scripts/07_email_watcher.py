#!/usr/bin/env python3
"""
Email Ingestion Pipeline

Monitors a mailbox via IMAP for new emails, downloads attachments,
classifies them, and routes to appropriate folders. Creates audit trail
entries and task assignments.
"""

import argparse
import email
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime
from email.header import decode_header
from pathlib import Path

try:
    from imapclient import IMAPClient
except ImportError:
    IMAPClient = None

try:
    import yaml
except ImportError:
    yaml = None


def load_config(config_path: str) -> dict:
    """Load email configuration."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def decode_subject(msg) -> str:
    """Decode email subject header."""
    subject = msg.get("Subject", "")
    decoded_parts = decode_header(subject)
    parts = []
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            parts.append(part.decode(encoding or "utf-8", errors="replace"))
        else:
            parts.append(part)
    return " ".join(parts)


def sanitize_filename(name: str) -> str:
    """Remove unsafe characters from filename."""
    return re.sub(r'[<>:"/\\|?*]', "_", name).strip()


def extract_attachments(msg, output_dir: Path) -> list:
    """Extract and save email attachments. Returns list of saved file paths."""
    saved = []
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        filename = part.get_filename()
        if filename:
            filename = sanitize_filename(filename)
            filepath = output_dir / filename

            # Handle duplicates
            if filepath.exists():
                stem = Path(filename).stem
                suffix = Path(filename).suffix
                counter = 1
                while filepath.exists():
                    filepath = output_dir / f"{stem}_{counter:03d}{suffix}"
                    counter += 1

            payload = part.get_payload(decode=True)
            if payload:
                filepath.write_bytes(payload)
                saved.append(str(filepath))

    return saved


def detect_routing(subject: str, sender: str, body: str, routing_rules: dict) -> dict:
    """
    Determine where to route an email based on subject, sender, and body.
    Returns routing info dict.
    """
    combined = f"{subject}\n{sender}\n{body[:2000]}"

    # Check sender-based rules
    sender_rules = routing_rules.get("sender_rules", {})
    for pattern, destination in sender_rules.items():
        if re.search(pattern, sender, re.IGNORECASE):
            return {"destination": destination, "method": "sender_match", "confidence": 0.85}

    # Check subject-based rules
    subject_rules = routing_rules.get("subject_rules", {})
    for pattern, destination in subject_rules.items():
        if re.search(pattern, subject, re.IGNORECASE):
            return {"destination": destination, "method": "subject_match", "confidence": 0.80}

    # Check keyword-based rules
    keyword_rules = routing_rules.get("keyword_rules", {})
    for pattern, destination in keyword_rules.items():
        if re.search(pattern, combined, re.IGNORECASE):
            return {"destination": destination, "method": "keyword_match", "confidence": 0.60}

    # Default: inbox unsorted
    return {
        "destination": "09_Inbox/01_Unsorted/",
        "method": "default",
        "confidence": 0.0,
    }


def write_audit_entry(audit_path: str, entry: dict):
    """Append an audit trail entry as JSON lines."""
    with open(audit_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def process_mailbox(config: dict, practice_root: str, audit_path: str, once: bool = False):
    """Connect to mailbox and process new messages."""

    if IMAPClient is None:
        print("Error: imapclient is required. Install with: pip install imapclient")
        sys.exit(1)

    imap_config = config["email"]
    routing_rules = config.get("routing", {})
    team_routing = config.get("team_assignments", {})

    root = Path(practice_root)
    inbox_dir = root / "09_Inbox" / "01_Unsorted"
    inbox_dir.mkdir(parents=True, exist_ok=True)

    print(f"Connecting to {imap_config['server']}...")

    while True:
        try:
            with IMAPClient(imap_config["server"], ssl=True) as client:
                client.login(imap_config["username"], imap_config["password"])
                client.select_folder(imap_config.get("folder", "INBOX"))

                # Search for unseen messages
                messages = client.search(["UNSEEN"])
                print(f"  Found {len(messages)} new messages")

                for uid in messages:
                    raw = client.fetch([uid], ["RFC822"])
                    msg = email.message_from_bytes(raw[uid][b"RFC822"])

                    subject = decode_subject(msg)
                    sender = msg.get("From", "")
                    date = msg.get("Date", "")

                    # Get body text
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                payload = part.get_payload(decode=True)
                                if payload:
                                    body = payload.decode("utf-8", errors="replace")
                                break
                    else:
                        payload = msg.get_payload(decode=True)
                        if payload:
                            body = payload.decode("utf-8", errors="replace")

                    # Route the email
                    routing = detect_routing(subject, sender, body, routing_rules)
                    dest_dir = root / routing["destination"]
                    dest_dir.mkdir(parents=True, exist_ok=True)

                    # Save email as .eml
                    safe_subject = sanitize_filename(subject)[:80]
                    eml_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_subject}.eml"
                    eml_path = dest_dir / eml_name
                    eml_path.write_bytes(raw[uid][b"RFC822"])

                    # Extract attachments
                    attachments = extract_attachments(msg, dest_dir)

                    # Determine team assignment
                    assigned_to = "unassigned"
                    for team_pattern, member in team_routing.items():
                        if re.search(team_pattern, routing["destination"], re.IGNORECASE):
                            assigned_to = member
                            break

                    # Write audit entry
                    audit_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "action": "email_ingested",
                        "source": "email_watcher",
                        "email_subject": subject,
                        "email_sender": sender,
                        "email_date": date,
                        "destination": routing["destination"],
                        "routing_method": routing["method"],
                        "confidence": routing["confidence"],
                        "attachments": attachments,
                        "assigned_to": assigned_to,
                        "status": "filed" if routing["confidence"] >= 0.70 else "pending_review",
                    }
                    write_audit_entry(audit_path, audit_entry)

                    print(f"  Processed: {subject[:60]}...")
                    print(f"    -> {routing['destination']} (conf: {routing['confidence']:.2f})")

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)

        if once:
            break

        # Poll interval
        interval = config.get("poll_interval_seconds", 300)
        print(f"\nSleeping {interval}s before next check...")
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Monitor mailbox and route emails")
    parser.add_argument(
        "--config",
        default="config/email_config.yaml",
        help="Path to email configuration YAML",
    )
    parser.add_argument(
        "--root",
        default="Practice_Root",
        help="Root directory for practice folders",
    )
    parser.add_argument(
        "--audit",
        default="reports/audit_trail.jsonl",
        help="Path for audit trail log",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process once and exit (don't poll continuously)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    process_mailbox(config, args.root, args.audit, args.once)


if __name__ == "__main__":
    main()
