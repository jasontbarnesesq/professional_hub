# Escalation Workflow

## Purpose

This document defines when and how to escalate filing, classification, and
document management issues. Timely escalation prevents misfiling, missed
deadlines, and compliance failures.

---

## Escalation Levels

| Level | Description | Response Time | Who Handles |
|---|---|---|---|
| 1 — Routine | Standard filing, known classification | Same business day | Office Manager / Paralegal |
| 2 — Review | Uncertain classification, new document type | 4 business hours | Associate / Compliance Officer |
| 3 — Urgent | Regulatory exam material, enforcement, deadline-sensitive | 2 hours | Senior Counsel / Partner |

---

## When to Escalate

### Escalate to Level 2 (Associate/Compliance Officer)

- File cannot be classified after consulting this guide and the taxonomy
- File appears to be client-confidential but no client/matter can be identified
- File was auto-classified with confidence < 0.50
- File contains potentially privileged material in an unexpected location
- Naming convention doesn't fit any standard pattern
- New matter type not represented in the taxonomy

### Escalate to Level 3 (Senior Counsel/Partner)

- Anything from SEC OCIE/EXAMS, FINRA Enforcement, or DOJ
- Documents with regulatory deadlines (response due dates)
- Subpoenas, document preservation notices, litigation holds
- Potential data breach or unauthorized access indicators
- Files containing material non-public information (MNPI)
- Any document related to an active regulatory examination
- Wells notices or preliminary determination letters

---

## Escalation Procedure

### Step 1: Document the Issue

Create an escalation entry with:
- Date and time
- Your name
- Description of the issue
- File path or document identifier
- What you've already tried
- Recommended action (if any)

### Step 2: Notify the Appropriate Person

- **Level 2:** Email the compliance officer with subject line:
  `[FILING ESCALATION] {brief description}`
- **Level 3:** Email senior counsel AND call/message directly. Subject line:
  `[URGENT FILING] {brief description}`

### Step 3: Interim Filing

While awaiting resolution:
- Move the file to `09_Inbox/02_Pending_Review/`
- Add a note file alongside it: `_NOTE_{YYYY-MM-DD}_{your_initials}.txt`
  containing the escalation details
- Do NOT attempt to file the document in a "best guess" location

### Step 4: Resolution

Once the escalation is resolved:
- File the document in its correct location
- Update the audit trail
- If the issue revealed a gap in the taxonomy or rules, notify the system
  administrator to update the classification rules

---

## Regulatory Deadline Escalation

Documents with regulatory deadlines require immediate handling:

| Source | Typical Deadline | Escalation |
|---|---|---|
| SEC Exam Document Request | 7-14 calendar days | Level 3 immediately |
| FINRA 8210 Request | 10-25 business days | Level 3 immediately |
| State Exam Request | Varies | Level 3 within 2 hours |
| Wells Notice | 30 calendar days | Level 3 immediately |
| Deficiency Letter Response | 30-60 calendar days | Level 3 within 4 hours |
| Annual Filing (ADV, etc.) | Fixed annual deadline | Level 2, 30 days before due |

---

## Automation Failures

If the automated filing system produces errors:

| Issue | Action |
|---|---|
| Email watcher stops running | Notify IT; manually check mailbox |
| Hot folder watcher stops | Notify IT; manually review `01_Unsorted/` |
| High volume of low-confidence classifications | Review classification rules; may need tuning |
| Files routed to wrong location | Move to correct location; report to system admin |
| Duplicate file warnings | Review dedup report; determine which to keep |

---

## Contacts

| Role | Name | Email | Phone |
|---|---|---|---|
| Office Manager | _(fill in)_ | | |
| Paralegal | _(fill in)_ | | |
| Compliance Officer | _(fill in)_ | | |
| Senior Counsel | _(fill in)_ | | |
| Managing Partner | _(fill in)_ | | |
| IT Support | _(fill in)_ | | |
