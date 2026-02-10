# Folder Taxonomy Specification

## Overview

This document defines the canonical folder structure for the securities
compliance law practice. All files must be organized according to this taxonomy.
The structure is designed around four organizing principles:

1. **By client/matter** — primary organizational unit for client work
2. **By regulatory body** — for regulatory materials and guidance
3. **By compliance function** — for compliance program documents
4. **By workflow stage** — for active projects and the filing pipeline

## Directory Structure

### `01_Clients/`

Client-centric organization. Each client gets a folder named with their ID and
name. Within each client, matters are organized by matter ID, type, and date.

```
01_Clients/
└── {ClientID}_{ClientName}/
    ├── 01_Engagement_Letters/    — Signed engagement letters, amendments, fee agreements
    ├── 02_Matters/
    │   └── {MatterID}_{Type}_{YYYY-MM}/
    │       ├── 01_Correspondence/       — All client and third-party correspondence
    │       ├── 02_Pleadings_Filings/    — Court filings, regulatory submissions
    │       ├── 03_Discovery/            — Document requests, productions, depositions
    │       ├── 04_Research_Memos/       — Internal legal analysis and memos
    │       ├── 05_Work_Product/         — Drafts and final deliverables
    │       ├── 06_Exhibits/             — Supporting exhibits and appendices
    │       ├── 07_Court_Orders/         — Orders, judgments, rulings
    │       └── 08_Closing/              — Closing documents, final disposition
    ├── 03_Billing/               — Invoices, payment records, trust accounting
    └── 04_Conflicts/             — Conflict check records and waiver letters
```

**Client ID format:** `CLI-NNNNN` (e.g., `CLI-00142_Acme_Securities`)
**Matter ID format:** `MAT-NNNNN` (e.g., `MAT-00301_SEC_Exam_2026-01`)

### `02_Regulatory/`

Materials from regulatory bodies, organized by agency.

```
02_Regulatory/
├── 01_SEC/
│   ├── Rules_Releases/         — Final rules, proposed rules, releases (34-XXXXX, IA-XXXXX)
│   ├── No_Action_Letters/      — Staff no-action and interpretive letters
│   ├── Enforcement_Actions/    — Administrative proceedings, litigation releases, OIPs
│   ├── Staff_Guidance/         — Staff bulletins, FAQs, IM guidance updates
│   └── Comment_Letters/        — Comment letters submitted and received
├── 02_FINRA/
│   ├── Rules/                  — FINRA rulebook, proposed rule changes
│   ├── Regulatory_Notices/     — Reg notices, information notices
│   ├── Disciplinary_Actions/   — AWCs, complaints, sanctions
│   └── Guidance/               — Interpretive letters, FAQ, report on exam findings
├── 03_State_Regulators/        — NASAA model rules, individual state materials
├── 04_DOJ/                     — DOJ enforcement, cooperation agreements
└── 05_Other_SROs/              — MSRB, NFA, CBOE, CME materials
```

### `03_Compliance_Programs/`

Compliance program documents for both the firm and clients.

```
03_Compliance_Programs/
├── 01_Policies_Procedures/
│   ├── Written_Supervisory_Procedures/   — WSPs (broker-dealer supervision)
│   ├── Code_of_Ethics/                   — Code of ethics, personal trading
│   ├── AML_BSA/                          — Anti-money laundering programs
│   ├── Insider_Trading/                  — MNPI policies, information barriers
│   ├── Business_Continuity/              — BCP and disaster recovery
│   ├── Cybersecurity/                    — InfoSec policies, incident response
│   └── Privacy/                          — Reg S-P, Reg S-ID, privacy notices
├── 02_Annual_Reviews/                    — Rule 206(4)-7, FINRA 3120 reviews
├── 03_Training_Materials/                — Training decks, quizzes, sign-in sheets
├── 04_Testing_Surveillance/              — Branch exams, trade surveillance, testing
└── 05_Regulatory_Exams/
    ├── SEC_Exams/                        — OCIE/EXAMS correspondence, deficiency letters
    ├── FINRA_Exams/                      — Cycle exams, cause exams, 8210 requests
    └── State_Exams/                      — State regulatory examinations
```

### `04_Forms_Templates/`

Reusable forms, blank templates, and checklists.

```
04_Forms_Templates/
├── 01_Registration/
│   ├── Form_ADV/           — Parts 1, 2A, 2B, CRS
│   ├── Form_BD/            — Broker-dealer registration
│   ├── Form_U4_U5/         — Rep registration/termination
│   └── Form_13F_13D_13G/   — Beneficial ownership filings
├── 02_Disclosure/           — Brochure supplements, disclosure templates
├── 03_Client_Agreements/    — Advisory, sub-advisory, IMA templates
├── 04_Internal_Checklists/  — Onboarding, matter opening, closing checklists
└── 05_Memo_Templates/       — Research memo, client memo, reg response templates
```

### `05_Research/`

Legal research, publications, and educational materials.

### `06_Firm_Administration/`

Internal operations: HR, finance, IT, insurance, marketing.

### `07_Active_Projects/`

Non-client projects and firm initiatives. Named with project ID, description,
and date: `PROJ-001_Website_Redesign_2026-01/`

### `08_Archive/`

Closed matters organized by year. Matters are moved here after closing and
retention review.

### `09_Inbox/`

The filing pipeline:

- `01_Unsorted/` — files arrive here from hot folder, email ingestion, or manual drop
- `02_Pending_Review/` — automation has classified the file but confidence is low
- `03_Pending_Filing/` — reviewed and approved, waiting to be moved to final location

## Matter Types

Use these standardized matter type codes in folder names:

| Code | Description |
|---|---|
| `SEC_Exam` | SEC examination |
| `FINRA_Exam` | FINRA examination |
| `State_Exam` | State regulatory exam |
| `Enforcement` | Enforcement action response |
| `Registration` | Registration filing |
| `Advisory` | Investment advisory matter |
| `BD_Compliance` | Broker-dealer compliance |
| `AML_Review` | AML program review |
| `Policy_Draft` | Policy/procedure drafting |
| `Training` | Training program |
| `General` | General advisory/consultation |
