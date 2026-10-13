# Architecture

## Components

### Frontend

React, Vite, and TypeScript handle the project workspace, request submission, evidence display, and draft review.

### Backend

Python and FastAPI validate requests, parse agreement documents, orchestrate analysis, validate structured output, and manage persistence.

### Local model runtime

Ollama with a compatible Gemma model will extract requirements, compare requests with documented scope, and produce structured draft content. Model output is untrusted input.

### Storage

SQLite is planned for project metadata, extracted requirements, analysis results, and request history. Original documents remain local. Data deletion and retention behavior must be documented before release.

## Planned request flow

1. User imports an agreement.
2. Backend extracts text and source references.
3. Requirements are stored with evidence.
4. User submits a new client request.
5. Analysis compares the request against the evidence.
6. The result is schema-validated and returned to the frontend.
7. The user reviews the result and edits the proposed response.

## Privacy and reliability

- No external inference API by default.
- No confidential document contents in application logs.
- Validate model output using explicit schemas.
- Treat uncertain conclusions as requiring human review.
- Never automatically send a client-facing response.
