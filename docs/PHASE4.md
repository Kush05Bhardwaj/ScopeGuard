# Phase 4 — Reports and Export

## Acceptance checklist

- [x] Generate a change-order proposal from the reviewed analysis without another model call.
- [x] Include project/date, agreement reference, client request, classification summary, verified evidence, proposed work, cost, timeline, and approval steps.
- [x] Keep cost and timeline as editable “To be agreed” placeholders unless supplied by the user.
- [x] Edit the Markdown proposal in the frontend before export.
- [x] Download Markdown and copy the proposal to the clipboard.
- [x] Reject empty or invalid request fields with HTTP 422.
- [x] Verify report evidence quotes against the supplied agreement text.
- [x] Backend tests pass and the frontend production build succeeds.

## API

`POST /api/reports/change-order` accepts project details, the agreement source
and text, client request, validated analysis summary/category/evidence, and any
user-provided proposed work, cost, or timeline. It returns a title and Markdown
draft. It does not call Ollama or save documents or report history.

Evidence quotes are checked as exact substrings of the agreement before they
are included. Invalid evidence is rejected. When no evidence is present, the
proposal calls out that manual review is required. This is a safeguard against
displaying fabricated quotations, not a guarantee about the analysis itself.

The React proposal editor is editable. Export Markdown downloads the current
editor contents; Copy proposal places the current contents on the clipboard.
PDF export and SQLite proposal history are deferred.
