# Phase 2 — Agreement Parsing

## Acceptance checklist

- [x] TXT uploads extract UTF-8 text into a structured response.
- [x] PDF uploads retain per-page text and one-based page references.
- [x] Unsupported, empty, over-10-MB, and over-100-page files are rejected.
- [x] `POST /api/agreements/parse` returns a structured response.
- [x] Automated tests cover valid uploads, malformed PDFs, and invalid uploads.
- [x] Phase 1 health tests and frontend production build pass.

Scanned PDFs are not OCR processed. The endpoint rejects PDFs that contain no
extractable text and explains this limitation in the response.
