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
6. Generate a proposed change-order draft.
7. Review and export the draft.

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

## Acceptance criteria

- A user can enter project scope and a client request.
- The system preserves the source of extracted requirements.
- Missing or conflicting evidence is flagged for review.
- Analysis results are validated before display.
- Users can review and edit generated drafts before export.
- No external AI API is required for the intended local workflow.
