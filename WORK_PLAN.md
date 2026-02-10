# Securities Compliance Practice — File Organization Master Work Plan

## Executive Summary

This work plan addresses the organization of approximately 50,000 files into a
professional practice management structure for a securities compliance law
practice. The plan is divided into five phases, each building on the previous,
designed to be executed sequentially with clearly defined deliverables.

---

## Phase 1: Audit, Inventory & Deduplication

**Priority:** CRITICAL — Must be completed first
**Complexity:** High
**Dependencies:** None

### Step 1.1 — Full File System Inventory

Run the `scripts/01_inventory.py` script (included in this repo) to crawl all
target directories and produce a CSV manifest of every file with:

- Full path, filename, extension
- File size, created date, modified date
- SHA-256 hash (for deduplication)
- MIME type

**Command:**
```bash
python3 scripts/01_inventory.py \
  --source-dirs "/path/to/files" "/path/to/more/files" \
  --output inventory.csv
```

### Step 1.2 — Exact Duplicate Detection & Removal

Using the inventory, group files by SHA-256 hash. Files with identical hashes
are exact duplicates. The script will:

1. Keep the file with the most recent modified date (or the one in the most
   logical location).
2. Move duplicates to a `_duplicates/` staging folder (not delete).
3. Produce a dedup report (`reports/dedup_report.csv`).

**Command:**
```bash
python3 scripts/02_dedup.py \
  --inventory inventory.csv \
  --duplicates-dir _duplicates \
  --report reports/dedup_report.csv
```

### Step 1.3 — Near-Duplicate Detection

For document files (PDF, DOCX, TXT), compute similarity using:

- **SimHash** for text content fingerprinting
- **Filename similarity** (Levenshtein distance)
- **Metadata comparison** (same author, similar dates, similar size)

Files flagged as near-duplicates are placed in a review queue
(`reports/near_dupes_review.csv`) for manual decision.

**Command:**
```bash
python3 scripts/03_near_dupes.py \
  --inventory inventory.csv \
  --threshold 0.85 \
  --report reports/near_dupes_review.csv
```

### Step 1.4 — Manual Review of Near-Duplicates

A team member reviews `near_dupes_review.csv` and marks each row as:
- `KEEP` — not a duplicate
- `REMOVE` — move to `_duplicates/`
- `MERGE` — combine content from both versions

---

## Phase 2: Taxonomy & Folder Structure

**Priority:** CRITICAL
**Complexity:** Medium
**Dependencies:** Phase 1 (inventory complete)

### Step 2.1 — Create the Directory Structure

Run the setup script to create the full directory tree:

```bash
python3 scripts/04_create_structure.py
```

This creates the structure defined in `taxonomy/folder_structure.yaml`
(included in this repo). See `docs/TAXONOMY.md` for the full specification.

### Step 2.2 — Top-Level Structure Overview

```
Practice_Root/
├── 01_Clients/
│   └── {ClientID}_{ClientName}/
│       ├── 01_Engagement_Letters/
│       ├── 02_Matters/
│       │   └── {MatterID}_{MatterType}_{Date}/
│       │       ├── 01_Correspondence/
│       │       ├── 02_Pleadings_Filings/
│       │       ├── 03_Discovery/
│       │       ├── 04_Research_Memos/
│       │       ├── 05_Work_Product/
│       │       ├── 06_Exhibits/
│       │       ├── 07_Court_Orders/
│       │       └── 08_Closing/
│       ├── 03_Billing/
│       └── 04_Conflicts/
├── 02_Regulatory/
│   ├── 01_SEC/
│   │   ├── Rules_Releases/
│   │   ├── No_Action_Letters/
│   │   ├── Enforcement_Actions/
│   │   ├── Staff_Guidance/
│   │   └── Comment_Letters/
│   ├── 02_FINRA/
│   │   ├── Rules/
│   │   ├── Regulatory_Notices/
│   │   ├── Disciplinary_Actions/
│   │   └── Guidance/
│   ├── 03_State_Regulators/
│   ├── 04_DOJ/
│   └── 05_Other_SROs/
├── 03_Compliance_Programs/
│   ├── 01_Policies_Procedures/
│   │   ├── Written_Supervisory_Procedures/
│   │   ├── Code_of_Ethics/
│   │   ├── AML_BSA/
│   │   ├── Insider_Trading/
│   │   ├── Business_Continuity/
│   │   ├── Cybersecurity/
│   │   └── Privacy/
│   ├── 02_Annual_Reviews/
│   ├── 03_Training_Materials/
│   ├── 04_Testing_Surveillance/
│   └── 05_Regulatory_Exams/
│       ├── SEC_Exams/
│       ├── FINRA_Exams/
│       └── State_Exams/
├── 04_Forms_Templates/
│   ├── 01_Registration/
│   │   ├── Form_ADV/
│   │   ├── Form_BD/
│   │   ├── Form_U4_U5/
│   │   └── Form_13F_13D_13G/
│   ├── 02_Disclosure/
│   ├── 03_Client_Agreements/
│   ├── 04_Internal_Checklists/
│   └── 05_Memo_Templates/
├── 05_Research/
│   ├── 01_Legal_Research/
│   ├── 02_Industry_Reports/
│   ├── 03_CLE_Materials/
│   └── 04_Publications/
├── 06_Firm_Administration/
│   ├── 01_HR/
│   ├── 02_Finance/
│   ├── 03_IT/
│   ├── 04_Insurance/
│   └── 05_Marketing/
├── 07_Active_Projects/
│   └── {ProjectID}_{Description}_{Date}/
├── 08_Archive/
│   └── {Year}/
│       └── {ClientID}_{MatterID}/
└── 09_Inbox/
    ├── 01_Unsorted/
    ├── 02_Pending_Review/
    └── 03_Pending_Filing/
```

---

## Phase 3: Automated Categorization & File Migration

**Priority:** HIGH
**Complexity:** High
**Dependencies:** Phases 1 & 2

### Step 3.1 — Content-Based Classification

The `scripts/05_categorize.py` script analyzes each file using:

1. **Extension mapping** — `.pdf`, `.docx`, `.xlsx` → document types
2. **Filename pattern matching** — regex for common legal naming:
   - `*Form_ADV*` → `04_Forms_Templates/01_Registration/Form_ADV/`
   - `*engagement*letter*` → `01_Clients/{Client}/01_Engagement_Letters/`
   - `*WSP*` or `*supervisory*` → `03_Compliance_Programs/01_Policies_Procedures/Written_Supervisory_Procedures/`
3. **Content keyword extraction** — scan first 5000 chars for regulatory terms
4. **Metadata extraction** — author, creation date, client identifiers
5. **Email parsing** — `.eml`/`.msg` files parsed for sender, recipient, subject

**Command:**
```bash
python3 scripts/05_categorize.py \
  --inventory inventory.csv \
  --taxonomy taxonomy/folder_structure.yaml \
  --rules taxonomy/classification_rules.yaml \
  --output reports/categorization_plan.csv
```

### Step 3.2 — Review the Categorization Plan

Before moving files, review `categorization_plan.csv`. Each row shows:

| source_path | proposed_destination | confidence | rule_matched | needs_review |
|---|---|---|---|---|
| /old/path/file.pdf | 01_Clients/ACME/02_Matters/... | 0.92 | filename_match | No |

Files with confidence < 0.70 are flagged `needs_review = Yes`.

### Step 3.3 — Execute the File Migration

```bash
python3 scripts/06_migrate.py \
  --plan reports/categorization_plan.csv \
  --dry-run          # Preview first
```

```bash
python3 scripts/06_migrate.py \
  --plan reports/categorization_plan.csv \
  --execute \
  --log reports/migration_log.csv
```

The migration script:
- Copies (not moves) files first, then verifies checksums
- Only deletes originals after verification
- Creates a full audit log (`migration_log.csv`)
- Handles filename collisions with sequential suffixes

### Step 3.4 — Handle Uncategorized Files

Files that could not be categorized go to `09_Inbox/01_Unsorted/`. A team
member triages these using the review interface or manually moves them.

---

## Phase 4: Incoming Document Automation

**Priority:** MEDIUM
**Complexity:** High
**Dependencies:** Phases 2 & 3

### Step 4.1 — Email Ingestion Pipeline

The `scripts/07_email_watcher.py` script monitors a designated mailbox
(via IMAP or Microsoft Graph API) and:

1. Downloads new emails and attachments
2. Parses sender, subject, and body for client/matter identifiers
3. Routes attachments to the correct folder
4. Logs all actions to `reports/email_ingestion_log.csv`
5. Creates tasks in the task queue for items needing human review

### Step 4.2 — Document Drop Folder (Hot Folder)

The `scripts/08_hot_folder_watcher.py` script monitors `09_Inbox/01_Unsorted/`
and runs the categorization engine on any new files:

```bash
python3 scripts/08_hot_folder_watcher.py \
  --watch-dir "09_Inbox/01_Unsorted/" \
  --taxonomy taxonomy/folder_structure.yaml \
  --rules taxonomy/classification_rules.yaml
```

### Step 4.3 — Task Assignment & Audit Trail

Every automated action creates an entry in `reports/audit_trail.jsonl` with:

```json
{
  "timestamp": "2026-02-10T14:30:00Z",
  "action": "file_routed",
  "source": "email_ingestion",
  "file": "SEC_Comment_Letter_2026-02-08.pdf",
  "destination": "02_Regulatory/01_SEC/Comment_Letters/",
  "assigned_to": "jbarnett",
  "confidence": 0.95,
  "status": "completed"
}
```

Task assignment rules are configured in `config/team_routing.yaml`.

### Step 4.4 — Notification System

Configurable notifications via:
- Email alerts for high-priority items (regulatory deadlines, new enforcement actions)
- Daily digest of all automated filing actions
- Escalation alerts for items stuck in review queues > 48 hours

---

## Phase 5: Documentation, Protocols & Training

**Priority:** MEDIUM
**Complexity:** Low
**Dependencies:** Phases 1–4

### Deliverables

| Document | Location | Purpose |
|---|---|---|
| `docs/TAXONOMY.md` | This repo | Full folder structure specification |
| `docs/NAMING_CONVENTIONS.md` | This repo | File and folder naming rules |
| `docs/FILING_PROCEDURES.md` | This repo | Step-by-step filing guide for team |
| `docs/ESCALATION_WORKFLOW.md` | This repo | When and how to escalate issues |
| `docs/SYSTEM_ADMIN_GUIDE.md` | This repo | How to maintain scripts and configs |

All documentation is included in this repository.

---

## Implementation Priority Matrix

| Phase | Priority | Can Start | Blocked By |
|---|---|---|---|
| 1. Audit & Dedup | CRITICAL | Immediately | Nothing |
| 2. Taxonomy | CRITICAL | Immediately | Nothing (parallel with 1) |
| 3. Categorization & Migration | HIGH | After 1 & 2 | Phases 1, 2 |
| 4. Automation | MEDIUM | After 2 & 3 | Phases 2, 3 |
| 5. Documentation | MEDIUM | Immediately | Nothing (iterative) |

---

## Required Tools & Dependencies

```
Python 3.10+
pip install:
  - python-magic       # MIME type detection
  - pandas             # Data manipulation
  - openpyxl           # Excel file reading
  - python-docx        # Word document parsing
  - PyPDF2             # PDF text extraction
  - simhash            # Near-duplicate detection
  - python-Levenshtein # String similarity
  - watchdog           # File system monitoring
  - pyyaml             # Config file parsing
  - extract-msg        # Outlook .msg parsing
  - imapclient         # Email ingestion
  - tqdm               # Progress bars
```

Install all at once:
```bash
pip install -r requirements.txt
```

---

## Quick Start

```bash
# 1. Clone this repo and install dependencies
git clone <this-repo>
cd MyLegalContacts
pip install -r requirements.txt

# 2. Run the inventory scan
python3 scripts/01_inventory.py --source-dirs "/path/to/files" --output inventory.csv

# 3. Deduplicate
python3 scripts/02_dedup.py --inventory inventory.csv --duplicates-dir _duplicates

# 4. Create folder structure
python3 scripts/04_create_structure.py

# 5. Categorize files
python3 scripts/05_categorize.py --inventory inventory.csv --output reports/categorization_plan.csv

# 6. Review the plan, then migrate
python3 scripts/06_migrate.py --plan reports/categorization_plan.csv --dry-run
python3 scripts/06_migrate.py --plan reports/categorization_plan.csv --execute

# 7. Start automation watchers
python3 scripts/08_hot_folder_watcher.py --watch-dir "09_Inbox/01_Unsorted/"
```
