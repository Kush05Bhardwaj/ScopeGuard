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
5. Generate and edit a change-order proposal with optional local cost and
   timeline suggestions.
6. Copy or download the final proposal as Markdown or PDF.

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
- Deterministic proposal text from validated analysis, with optional local model
  suggestions for cost and timeline.
- Editable proposal preview, clipboard copy, and Markdown/PDF downloads.
- Automated backend coverage and a frontend production build.

## Deferred or excluded

- SQLite project and report history
- OCR for scanned PDFs
- Authentication, teams, and cloud synchronization
- Billing and payment processing
- Automatic client communication
- Legal advice or definitive contract interpretation

## Product safeguards

- Do not display model-generated evidence as verified unless its quotation
  exists exactly in the submitted agreement.
- Require human review when evidence is missing or the model reports ambiguity
  or a potential scope change.
- Label model-generated price and timeline values as rough estimates, include
  their assumptions, and require freelancer review before sharing.
- Require users to review and edit proposals before sharing them.
- Do not automatically send client-facing messages.
