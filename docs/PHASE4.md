# Phase 4 — Reports and Export

## Implemented

- Deterministic proposal generation at `POST /api/reports/change-order`, with
  optional local cost and timeline suggestions.
- Proposal sections for project/date, client (optional), agreement reference,
  request, classification, summary/reasoning, evidence, proposed work, cost,
  timeline, and approval steps.
- Explicit placeholders when estimate suggestions are disabled or unavailable.
- Estimate assumptions shown and labeled for freelancer review.
- Editable Markdown preview, clipboard copy, and Markdown/PDF downloads.
- Schema validation, evidence quote verification against the source agreement,
  and review-flag checks before rendering.

## Request contract

The proposal API accepts project and agreement metadata, agreement text, client
request, a validated nested `ScopeAnalysisResponse`, and proposal details. Set
`auto_estimate` to ask local Ollama for missing cost or timeline values. Optional
`estimate_context` provides currency, rate, region, or availability context.
Invalid or missing fields return HTTP 422.

Every evidence quote must be an exact substring of `agreement_text`. A report
without evidence is accepted only when analysis is `needs_review` and requires
human review. `potential_scope_change` and `needs_review` analyses must carry a
human-review flag.

The API validates shape and source-quote presence. It cannot prove semantic
correctness or authenticate the origin of the supplied analysis. Review results
before using or sharing a proposal.

`POST /api/reports/change-order/pdf` accepts the current edited Markdown and
returns a local PDF download. Estimates are suggestions, not market quotes or
agreed terms; the freelancer should review and edit them before sharing.

## Deferred

- SQLite proposal history or project persistence
- Automatic client communication
