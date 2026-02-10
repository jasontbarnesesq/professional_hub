# System Administration Guide

## Overview

This guide covers the maintenance and operation of the automated file
organization system. It is intended for the person responsible for keeping
the scripts, configurations, and folder structure running smoothly.

---

## System Components

| Component | Script | Purpose |
|---|---|---|
| Inventory Scanner | `scripts/01_inventory.py` | Full file system audit |
| Exact Dedup | `scripts/02_dedup.py` | SHA-256 duplicate detection |
| Near-Duplicate Detector | `scripts/03_near_dupes.py` | Similarity-based detection |
| Structure Creator | `scripts/04_create_structure.py` | Build folder tree from YAML |
| Categorizer | `scripts/05_categorize.py` | Rule-based file classification |
| Migrator | `scripts/06_migrate.py` | Safe file migration with verification |
| Email Watcher | `scripts/07_email_watcher.py` | IMAP email ingestion |
| Hot Folder Watcher | `scripts/08_hot_folder_watcher.py` | Auto-classify dropped files |

---

## Installation

### Prerequisites
- Python 3.10 or later
- pip package manager

### Setup
```bash
cd MyLegalContacts
pip install -r requirements.txt
```

### Configuration
1. Copy `config/email_config.yaml.example` to `config/email_config.yaml`
2. Fill in your email server credentials
3. Review and customize `config/team_routing.yaml`
4. Review `taxonomy/classification_rules.yaml` and adjust patterns as needed

---

## Running the System

### One-Time Setup
```bash
# Create the folder structure
python3 scripts/04_create_structure.py --root /path/to/practice

# Run initial inventory (may take hours for 50K+ files)
python3 scripts/01_inventory.py --source-dirs /path/to/files --output inventory.csv

# Deduplicate
python3 scripts/02_dedup.py --inventory inventory.csv --dry-run
python3 scripts/02_dedup.py --inventory inventory.csv

# Categorize and migrate
python3 scripts/05_categorize.py --inventory inventory.csv
python3 scripts/06_migrate.py --plan reports/categorization_plan.csv --dry-run
python3 scripts/06_migrate.py --plan reports/categorization_plan.csv --execute
```

### Ongoing Operations

#### Email Watcher (run as service)
```bash
# Run continuously
python3 scripts/07_email_watcher.py --config config/email_config.yaml

# Or run once (e.g., from cron)
python3 scripts/07_email_watcher.py --config config/email_config.yaml --once
```

#### Hot Folder Watcher (run as service)
```bash
python3 scripts/08_hot_folder_watcher.py --watch-dir "Practice_Root/09_Inbox/01_Unsorted/"
```

#### Running as System Services (Linux)

Create systemd unit files for persistent operation:

```ini
# /etc/systemd/system/legal-email-watcher.service
[Unit]
Description=Legal Practice Email Watcher
After=network.target

[Service]
Type=simple
User=legaladmin
WorkingDirectory=/path/to/MyLegalContacts
ExecStart=/usr/bin/python3 scripts/07_email_watcher.py --config config/email_config.yaml
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable legal-email-watcher
sudo systemctl start legal-email-watcher
```

---

## Updating Classification Rules

### Adding a New Rule

Edit `taxonomy/classification_rules.yaml`:

```yaml
- name: new_rule_name
  type: filename          # filename, content, extension, email, metadata
  pattern: "(?i)your_regex_here"
  target: "02_Regulatory/01_SEC/New_Subfolder/"
  confidence: 0.85
```

### Testing Rule Changes

After modifying rules, re-run categorization on a sample:

```bash
# Run on existing inventory to see what would change
python3 scripts/05_categorize.py \
  --inventory inventory.csv \
  --rules taxonomy/classification_rules.yaml \
  --output reports/test_categorization.csv \
  --skip-content

# Compare with previous categorization
diff reports/categorization_plan.csv reports/test_categorization.csv
```

### Adding a New Folder to the Taxonomy

1. Edit `taxonomy/folder_structure.yaml` to add the new directory
2. Run `python3 scripts/04_create_structure.py` to create it on disk
3. Add classification rules that route files to the new folder
4. Update `docs/TAXONOMY.md` with the new folder's purpose
5. Notify the team of the change

---

## Monitoring

### Audit Trail

All automated actions are logged to `reports/audit_trail.jsonl`. Each line
is a JSON object. Monitor for:

- `"status": "pending_review"` — items needing human attention
- `"confidence"` values below 0.50 — classification rules may need tuning
- Error entries — system issues

### Quick Health Check

```bash
# Count items in inbox (should be low)
ls Practice_Root/09_Inbox/01_Unsorted/ | wc -l
ls Practice_Root/09_Inbox/02_Pending_Review/ | wc -l

# Check audit trail for recent errors
grep '"status": "error"' reports/audit_trail.jsonl | tail -20

# Check email watcher is running
ps aux | grep email_watcher

# Check hot folder watcher is running
ps aux | grep hot_folder_watcher
```

### Periodic Maintenance

| Frequency | Task |
|---|---|
| Daily | Clear inbox folders, review audit trail |
| Weekly | Re-run inventory on new files, check for stale items in review queue |
| Monthly | Review classification accuracy, update rules, run near-duplicate scan |
| Quarterly | Full re-inventory, archive closed matters, backup configuration |
| Annually | Review entire taxonomy for relevance, update for regulatory changes |

---

## Backup & Recovery

### What to Back Up
1. `taxonomy/` — folder structure and classification rules
2. `config/` — email and routing configuration
3. `reports/` — audit trails and logs
4. `scripts/` — all automation scripts
5. The entire `Practice_Root/` directory tree

### Recovery Procedure
1. Restore the `taxonomy/` and `config/` directories
2. Run `scripts/04_create_structure.py` to recreate the folder tree
3. Restore files from backup into the structure
4. Re-run inventory to verify completeness
5. Restart watchers

---

## Troubleshooting

| Problem | Likely Cause | Solution |
|---|---|---|
| Inventory scan is slow | Large files or network drives | Use `--include-hidden` flag sparingly; scan local copies |
| Many files classified as "unclassified" | Rules don't cover these file types | Review samples, add new rules |
| Email watcher disconnects | IMAP timeout or credential issue | Check config, verify credentials, check server logs |
| Hot folder watcher misses files | File written slowly (large upload) | Increase debounce time in script |
| Checksum verification fails | Disk error or file in use | Re-run migration for failed files |
| Near-duplicate detection too slow | Too many document files | Increase `--threshold` or limit to specific directories |
