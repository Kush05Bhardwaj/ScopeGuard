# Phase 5 — Validation and Polish

Validation run on 2026-10-17 against the merged Phase 1–4 implementation.

## Live synthetic workflow

The sample agreement was uploaded to the parsing endpoint, then three requests
were sent through the configured local Ollama service using Gemma 3 4B:

| Request | Live result | Evidence and review |
|---|---|---|
| Contact form works on mobile devices | `in_scope` | One exact responsive-layout passage; no human review requested. |
| Add an administrator dashboard and recurring subscription payments | `potential_scope_change` | Two exact exclusion passages; the model requested human review. The generated report returned HTTP 200 and retained the cost/timeline placeholders. |
| Make the website more professional | `needs_review` | No evidence returned; human review required. |

All returned quotations were checked as exact substrings of the uploaded sample.
This is one run of a probabilistic model, not a guarantee of semantic accuracy.

The first live run revealed that Gemma sometimes omitted an evidence
explanation. The API now supplies neutral review wording for that missing
field, without claiming that the passage supports the request. Analysis with
no verified evidence is downgraded to `needs_review`; report generation rejects
a confident classification when evidence is absent. Malformed response JSON
and invalid response schemas produce controlled API errors. Unreadable
replacement characters in model text trigger human review. Potential scope
changes and ambiguous results must both retain the human-review flag.

The report endpoint now requires a complete Pydantic-validated analysis object
and checks its evidence against the agreement again. This validates structure
and quote presence; it cannot prove semantic correctness or cryptographically
prove where the analysis originated. Human review remains necessary.

## Automated validation

- Backend suite: **49 passed**, including upload limits and malformed PDFs,
  analysis evidence validation, missing Ollama, timeout, invalid JSON, invalid
  model categories, report validation, and a complete mocked upload-analysis-
  report API workflow.
- Frontend production build: passed with `npm.cmd run build`.
- The frontend has no configured test script.
- The Markdown download helper smoke check confirmed `.md` filename handling,
  Blob URL creation, and anchor click/removal. No automated real-browser
  download test is configured.

## Privacy and local-first checks

- Agreement parsing occurs in memory and does not persist uploaded files.
- Default frontend API and Ollama endpoints use `127.0.0.1`; custom URL
  overrides can send agreement/request text to another configured host.
- Application code inspection found no logging or printing of document text.
  API error responses use fixed messages rather than echoing submitted text.
- `.env.local`, `.venv`, databases, uploads, `node_modules`, and build output are
  ignored. Tracked environment files are examples only. The tracked sample
  agreement is synthetic.
- These checks support local-first defaults, not a blanket privacy guarantee.

## User feedback

No freelancer or external developer feedback was collected during this
validation run. The self-test used only synthetic agreement data and does not
count as external usability validation; the three user feedback questions
remain unanswered.
