# Phase 4 — Reports and Export

## Implemented

- Deterministic change-order generation at `POST /api/reports/change-order`;
  report creation makes no additional model call.
- Proposal sections for project/date, client (optional), agreement reference,
  request, classification, summary/reasoning, evidence, proposed work, cost,
  timeline, and approval steps.
- Explicit placeholders for unspecified proposed work, cost, and timeline.
- Editable Markdown preview, clipboard copy, and `.md` download in the frontend.
- Schema validation, evidence quote verification against the source agreement,
  and review-flag checks before rendering.

## Request contract

The API accepts project and agreement metadata, the agreement text, client
request, a complete nested `ScopeAnalysisResponse` under `analysis`, and
user-provided proposal details. The nested analysis includes its category,
summary, reasoning, evidence, model name, and human-review flag. Invalid or
missing fields return HTTP 422.

Every evidence quote must be an exact substring of `agreement_text`. A report
without evidence is accepted only when analysis is `needs_review` and requires
human review. `potential_scope_change` and `needs_review` analyses must carry a
human-review flag.

The API validates shape and source-quote presence. It cannot prove semantic
correctness or authenticate the origin of the supplied analysis. Review results
before using or sharing a proposal.

## Deferred

- PDF export
- SQLite proposal history or project persistence
- Automatic client communication
