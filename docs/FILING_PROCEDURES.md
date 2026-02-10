# Filing Procedures Guide

## Purpose

This guide provides step-by-step instructions for team members to file
documents into the practice management folder structure. Follow these
procedures to maintain consistency, ensure compliance with record-keeping
requirements, and enable efficient retrieval.

---

## 1. Receiving a New Document

### From Email
1. If the email watcher is running, attachments are automatically downloaded
   and routed. Check `reports/audit_trail.jsonl` for confirmation.
2. If manually handling: save the email as `.eml` and all attachments to
   `09_Inbox/01_Unsorted/`.
3. Name the saved files according to the naming conventions in
   `docs/NAMING_CONVENTIONS.md`.

### From Physical Mail (scanned)
1. Scan to PDF at minimum 300 DPI, grayscale or color as appropriate.
2. Use OCR if the scanner supports it.
3. Save to `09_Inbox/01_Unsorted/` with the naming convention:
   `{YYYY-MM-DD}_{Sender}_{Description}.pdf`

### From Client Portal / Secure Upload
1. Download and save to `09_Inbox/01_Unsorted/`.
2. If the hot folder watcher is running, it will attempt automatic classification.
3. Verify the classification and move to the correct folder if needed.

### Internal Work Product
1. Save drafts to the appropriate matter's `05_Work_Product/` folder.
2. Name using: `{YYYY-MM-DD}_{Document_Type}_{Description}_DRAFT_v{N}.{ext}`
3. When finalized, remove the `DRAFT` designation and update the version number.

---

## 2. Classifying a Document

Ask these questions in order:

### Question 1: Is this related to a specific client matter?
- **YES** → File under `01_Clients/{ClientID}/02_Matters/{MatterID}/`
  - Correspondence → `01_Correspondence/`
  - Court/regulatory filing → `02_Pleadings_Filings/`
  - Discovery material → `03_Discovery/`
  - Research/analysis → `04_Research_Memos/`
  - Deliverable/work product → `05_Work_Product/`
  - Exhibit → `06_Exhibits/`
  - Court order → `07_Court_Orders/`

### Question 2: Is this from or about a regulatory body?
- **YES** → File under `02_Regulatory/{Agency}/`
  - SEC materials → `01_SEC/` (further by subcategory)
  - FINRA materials → `02_FINRA/` (further by subcategory)
  - State regulators → `03_State_Regulators/`

### Question 3: Is this a compliance program document?
- **YES** → File under `03_Compliance_Programs/`
  - Policy/procedure → `01_Policies_Procedures/{type}/`
  - Annual review → `02_Annual_Reviews/`
  - Training material → `03_Training_Materials/`
  - Testing/surveillance → `04_Testing_Surveillance/`
  - Exam-related → `05_Regulatory_Exams/{agency}/`

### Question 4: Is this a reusable form or template?
- **YES** → File under `04_Forms_Templates/`

### Question 5: Is this research or educational?
- **YES** → File under `05_Research/`

### Question 6: Is this firm administrative?
- **YES** → File under `06_Firm_Administration/`

### If none of the above:
- Place in `09_Inbox/02_Pending_Review/` and flag for senior review.

---

## 3. Opening a New Client

1. Conduct conflicts check. Document result in the client's `04_Conflicts/` folder.
2. Create client folder: `01_Clients/CLI-{NNNNN}_{Client_Name}/`
3. Create standard subfolders (use the structure script or copy from template).
4. File the signed engagement letter in `01_Engagement_Letters/`.
5. Create the first matter folder under `02_Matters/`.
6. Update the client registry (if maintained).

---

## 4. Opening a New Matter

1. Assign matter ID: `MAT-{NNNNN}`.
2. Create matter folder: `02_Matters/MAT-{NNNNN}_{MatterType}_{YYYY-MM}/`
3. Ensure all eight standard subfolders exist.
4. File the initial documents.
5. Update the matter index (if maintained).

---

## 5. Closing a Matter

1. Ensure all documents are properly filed and named.
2. Verify no documents remain in `09_Inbox/` related to this matter.
3. Create a closing memo in `08_Closing/`.
4. Review retention requirements for the matter type.
5. Move the entire matter folder to `08_Archive/{Year}/`.
6. Update the matter index with closed status and archive location.

---

## 6. Daily Filing Workflow

| Time | Task | Responsible |
|---|---|---|
| 9:00 AM | Review `09_Inbox/01_Unsorted/` for overnight items | Office Manager |
| 9:30 AM | Review `09_Inbox/02_Pending_Review/` for auto-classified items | Paralegal |
| 10:00 AM | Process `09_Inbox/03_Pending_Filing/` — move approved items to final location | Paralegal |
| 2:00 PM | Second pass on all inbox folders | Office Manager |
| 4:30 PM | End-of-day review: inbox should be empty or flagged for next day | Office Manager |

---

## 7. Quality Checks

### Weekly
- [ ] All inbox folders reviewed and cleared
- [ ] No files with generic names (`Document1`, `Untitled`, etc.)
- [ ] Spot-check 10 recently filed documents for correct placement
- [ ] Review audit trail for any errors or low-confidence classifications

### Monthly
- [ ] Full review of `09_Inbox/02_Pending_Review/` — nothing older than 30 days
- [ ] Verify all active matters have current documents
- [ ] Check for misfiled documents reported by team members
- [ ] Review and update classification rules if false positives/negatives observed

### Quarterly
- [ ] Review closed matters for archive eligibility
- [ ] Update taxonomy if new regulatory areas or matter types emerge
- [ ] Team training refresher on filing procedures
- [ ] Backup verification
