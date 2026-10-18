# Architecture

## Components

### Frontend

React, Vite, and TypeScript handle agreement upload, request submission, and display classifications with verified evidence.

### Backend

Python and FastAPI validate requests, parse agreement documents, orchestrate analysis, validate structured model output, and verify evidence against source text.

### Local model runtime

Ollama with a compatible Gemma model compares requests with documented scope and returns structured analysis. Model output is untrusted input; each evidence quote is checked against the submitted agreement before it is returned.

### Reports

The report endpoint validates the analysis and verifies evidence quotations
again. It generates the proposal text deterministically. If automatic
estimates are enabled and cost or timeline is missing, it calls the configured
local Ollama model for rough suggestions and assumptions. The user edits the
Markdown draft and can download the final edited content as Markdown or PDF.

### Storage

SQLite is planned for project metadata, extracted requirements, analysis results, and request history. Original documents remain local. Data deletion and retention behavior must be documented before release.

## Planned request flow

1. User imports an agreement.
2. Backend extracts text and source references.
3. Requirements are stored with evidence.
4. User submits a new client request.
5. Analysis compares the request against the evidence.
6. The result is schema-validated and returned to the frontend.
7. The user reviews the result and prepares an editable change-order proposal.
8. Optional estimate suggestions are generated locally, then the user edits and
   exports the proposal.

## Privacy and reliability

- No external inference API by default.
- No confidential document contents in application logs.
- Validate model output using explicit schemas.
- Treat uncertain conclusions as requiring human review.
- Never automatically send a client-facing response.
