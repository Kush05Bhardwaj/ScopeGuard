# ScopeGuard Local — MVP

## Problem

Freelancers can lose time and revenue when new client requests extend beyond the deliverables agreed at the start of a project.

## Target users

- Freelance web developers
- Independent designers
- Small digital agencies

## Primary workflow

1. Create a project.
2. Import or enter the original agreement.
3. Submit a new client request.
4. Compare the request against the agreement.
5. Review classifications and supporting passages.
6. Generate a proposed change-order draft with optional model-suggested cost
   and timeline estimates.
7. Review and edit the draft, then download it as Markdown or PDF.

## Analysis classifications

- In scope: explicitly supported by the agreement.
- Potential scope change: appears outside the documented scope.
- Needs review: ambiguous, incomplete, or conflicting evidence.

These labels are decision support, not legal conclusions.

## MVP exclusions

- Authentication and team accounts
- Cloud synchronization
- Billing and payment processing
- Automatic client communication
- Legal advice or definitive contract interpretation
- Persistent project/report history

## Acceptance criteria

- A user can enter project scope and a client request.
- The system preserves the source of extracted requirements.
- Missing or conflicting evidence is flagged for review.
- Analysis results are validated before display.
- Users can review and edit generated drafts before export.
- Optional model-generated cost and timeline suggestions include assumptions
  and require freelancer review.
- The final editable proposal can be downloaded as PDF.
- No external AI API is required for the intended local workflow.
