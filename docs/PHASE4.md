# Phase 4 — Reports and Export

## Implemented

- Deterministic proposal text at `POST /api/reports/change-order`.
- Optional local model suggestions for cost and timeline, including explicit
  assumptions for freelancer review.
- Proposal sections for project/date, client, agreement reference, request,
  analysis, verified evidence, proposed work, cost, timeline, and approval.
- Editable Markdown preview, clipboard copy, and Markdown/PDF downloads for the
  current edited draft.
- Schema validation, evidence quote verification, and human-review checks.

## Request contract

The API accepts project and agreement metadata, the agreement text, client
request, a validated nested analysis response, and proposal details. Enable
`auto_estimate` to request local Ollama suggestions when cost or timeline is
missing. Optional `estimate_context` can provide currency, hourly rate, region,
or availability to guide those suggestions. Invalid or missing fields return
HTTP 422; Ollama errors use controlled 5xx responses.

Every evidence quote must be an exact substring of `agreement_text`. A report
without evidence is accepted only when analysis is `needs_review` and requires
human review. The API cannot establish semantic correctness or authenticate
the origin of the supplied analysis.

Generated estimates are rough model suggestions, not market quotes or agreed
terms. The freelancer should check and edit them before sharing. PDF export
sends the current editor contents to the local API for conversion; report
history and SQLite persistence remain deferred.
