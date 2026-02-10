# File & Folder Naming Conventions

## General Rules

1. **No spaces** — use underscores (`_`) to separate words
2. **No special characters** — only use `A-Z`, `a-z`, `0-9`, `_`, `-`, `.`
3. **Dates always use ISO format** — `YYYY-MM-DD` (e.g., `2026-02-10`)
4. **Dates go at the beginning** when the file is date-driven
5. **Keep names under 80 characters** (excluding extension)
6. **Use Title_Case** for folder names and descriptive segments
7. **Use lowercase** for file extensions (`.pdf`, not `.PDF`)

## Folder Naming

### Client Folders
```
{ClientID}_{Client_Name}
CLI-00142_Acme_Securities
CLI-00143_Blue_Capital_Advisors
```

### Matter Folders
```
{MatterID}_{MatterType}_{YYYY-MM}
MAT-00301_SEC_Exam_2026-01
MAT-00302_Registration_2026-02
MAT-00303_Enforcement_2025-11
```

### Project Folders
```
{ProjectID}_{Description}_{YYYY-MM}
PROJ-001_AML_Program_Overhaul_2026-01
PROJ-002_Annual_Review_2026
```

## File Naming

### Correspondence
```
{YYYY-MM-DD}_{Direction}_{Recipient_or_Sender}_{Subject}.{ext}

2026-02-10_TO_SEC_Response_to_Deficiency_Letter.pdf
2026-02-08_FROM_Client_Engagement_Letter_Signed.pdf
2026-01-15_INTERNAL_Memo_Re_AML_Findings.docx
```

Direction codes: `TO`, `FROM`, `INTERNAL`, `CC`

### Pleadings & Filings
```
{YYYY-MM-DD}_{Document_Type}_{Description}.{ext}

2026-02-01_Motion_to_Dismiss_Securities_Fraud_Claim.pdf
2026-01-20_Answer_to_Complaint.pdf
2026-01-15_Subpoena_Duces_Tecum.pdf
```

### Regulatory Documents
```
{Agency}_{Document_Type}_{Reference_Number}_{Date}.{ext}

SEC_Rule_Release_34-99876_2026-01-15.pdf
SEC_No_Action_Letter_Acme_Fund_2025-12-01.pdf
FINRA_Reg_Notice_26-01_2026-01-10.pdf
FINRA_AWC_2025065432101_2026-02-01.pdf
```

### Policies & Procedures
```
{Policy_Name}_v{Version}_{YYYY-MM-DD}.{ext}

Written_Supervisory_Procedures_v3.2_2026-01-15.pdf
Code_of_Ethics_v2.0_2025-12-01.docx
AML_Program_v4.1_2026-02-01.pdf
Business_Continuity_Plan_v1.5_2025-06-15.docx
```

### Forms
```
{Form_Name}_{Client_or_Entity}_{YYYY-MM-DD}.{ext}

Form_ADV_Part2A_Blue_Capital_2026-03-30.pdf
Form_U4_Amendment_John_Smith_2026-01-15.pdf
Form_13F_Q4_2025_Acme_Fund.xlsx
```

### Research & Memos
```
{YYYY-MM-DD}_{Memo_Type}_{Subject}.{ext}

2026-02-10_Research_Memo_Reg_BI_Compliance_Obligations.docx
2026-01-22_Client_Alert_SEC_Marketing_Rule_Updates.pdf
2025-12-15_CLE_Presentation_Cybersecurity_Best_Practices.pptx
```

### Billing
```
{YYYY-MM-DD}_Invoice_{ClientID}_{Invoice_Number}.{ext}

2026-02-01_Invoice_CLI-00142_INV-2026-0215.pdf
2026-01-31_Trust_Account_Statement_CLI-00143.pdf
```

### Emails (saved as files)
```
{YYYY-MM-DD}_{HHMM}_{Sender}_{Subject_Abbreviated}.eml

2026-02-10_1430_SEC_OCIE_Document_Request_Response.eml
2026-02-08_0915_Client_Acme_Engagement_Approval.eml
```

## Version Control

When updating a document, create a new version rather than overwriting:

```
AML_Program_v4.0_2025-06-01.pdf    (superseded)
AML_Program_v4.1_2026-02-01.pdf    (current)
```

Mark superseded versions by moving them to an `_Archive/` subfolder within
the same directory, or prefix with `SUPERSEDED_`.

## Prohibited Patterns

Do NOT use:
- Spaces in filenames (use `_` instead)
- Dates in `MM/DD/YYYY` or `DD-MM-YYYY` format
- Generic names like `Document1.docx`, `Scan001.pdf`, `New Folder`
- Client names without client IDs
- Abbreviations without context (except standard ones: SEC, FINRA, AML, etc.)
- Version indicators like `_final`, `_final_v2`, `_FINAL_FINAL` — use version numbers
