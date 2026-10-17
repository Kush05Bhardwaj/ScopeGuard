# Architecture

## Components

### Frontend

React, Vite, and TypeScript provide agreement upload, request entry, analysis
review, and change-order editing/export. The default API URL is
`http://127.0.0.1:8000` and can be changed with `VITE_API_BASE_URL`.

### Backend

FastAPI exposes the health, agreement parsing, scope analysis, and report
endpoints. Pydantic schemas bound and validate request and model-response
shapes. Uploads are read in memory and are not persisted.

### Inference

The analysis service calls Ollama's local HTTP API. The defaults are
`http://127.0.0.1:11434` and `gemma3:4b`; `OLLAMA_BASE_URL` and `OLLAMA_MODEL`
can override them. Model output is untrusted. The backend validates its schema,
removes quotations absent from the submitted agreement, and requires human
review if evidence is missing or invalid.

Quotation presence is a source check, not a semantic correctness guarantee.
Potential scope changes and ambiguous results require human review.

### Reports

The frontend sends the analysis response, agreement text, and proposal details
to `POST /api/reports/change-order`. The backend validates the nested analysis
schema and checks evidence quotations against the agreement again. It then
generates Markdown deterministically without another model call. The frontend
lets the user edit the returned Markdown before copying or downloading it.

The report endpoint validates schema and quote presence, but does not persist
analysis or authenticate its origin. Treat it as a local application API, not
as proof that an analysis is true.

### Storage

Project data, uploads, analysis results, and proposal history are not currently
stored in SQLite. A database and retention/deletion behavior remain future
work. Original uploaded files are not saved by the parser.

## Current request flow

1. The browser sends one TXT or PDF file to `POST /api/agreements/parse`.
2. The API parses UTF-8 text or extracts PDF page text in memory and returns
   structured text with page references. Scanned PDFs are not OCR processed.
3. The browser sends the parsed text and client request to
   `POST /api/analysis/scope`.
4. The backend calls Ollama, validates the structured response, and verifies
   every evidence quotation against the submitted text.
5. The browser displays the classification, reasoning, evidence, and review
   notice.
6. When asked, the browser sends the analysis and proposal fields to
   `POST /api/reports/change-order`.
7. The backend verifies the report evidence and returns a Markdown draft. The
   user edits and exports it; the app does not contact the client.

## Local-first and reliability notes

- By default, both the browser API URL and Ollama URL point to `127.0.0.1`.
- Custom endpoint URLs may send agreement and request text to another host.
- Application code does not log document or request contents.
- API errors use fixed details and do not echo submitted document text.
- Missing evidence, invalid model output, ambiguous requests, and potential
  scope changes are surfaced for human review.
- The model's classification can still be wrong; users should review the
  agreement and source passages before acting.
