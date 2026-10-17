# ScopeGuard Local — MVP

## Problem and users

Freelancers can lose time and revenue when a new client request extends beyond
the deliverables agreed at the start of a project. The MVP is intended for
freelance web developers, independent designers, and small digital agencies.

## Current workflow

1. Upload a text agreement or a PDF with selectable text.
2. Enter a new client request.
3. Compare it with the agreement using the configured Ollama model.
4. Review the classification, explanation, and verified source quotations.
5. Generate and edit a change-order proposal.
6. Copy the proposal or export it as Markdown.

The app does not currently create persistent projects. The project name is
entered as proposal metadata.

## Analysis labels

- **In scope:** The model finds agreement text that appears to support the
  request.
- **Potential scope change:** The request appears to conflict with or extend
  the documented scope. Human review is required.
- **Needs review:** The request or evidence is ambiguous, missing, or otherwise
  insufficient. Human review is required.

These labels are decision support, not legal conclusions. Exact quote
verification confirms that words occur in the submitted text; it does not
validate the model's interpretation.

## Implemented

- In-memory parsing for UTF-8 TXT and text-based PDF uploads.
- PDF page-level text references; scanned PDFs are not OCR processed.
- Local Ollama inference by default with structured response validation.
- Evidence quote checks and conservative handling of missing or invalid
  evidence.
- Deterministic change-order proposal generation from a validated analysis.
- Editable proposal preview, clipboard copy, and Markdown download.
- Automated backend coverage and a frontend production build.

## Deferred or excluded

- SQLite project and report history
- OCR for scanned PDFs
- PDF proposal export
- Authentication, teams, and cloud synchronization
- Billing and payment processing
- Automatic client communication
- Legal advice or definitive contract interpretation

## Product safeguards

- Do not display model-generated evidence as verified unless its quotation
  exists exactly in the submitted agreement.
- Require human review when evidence is missing or the model reports ambiguity
  or a potential scope change.
- Keep generated prices, dates, and contractual terms out of the report unless
  the user supplies them; otherwise use explicit placeholders.
- Require users to review and edit proposals before sharing them.
- Do not automatically send client-facing messages.
