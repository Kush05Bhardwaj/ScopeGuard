# Phase 3 — Local AI Analysis

## Acceptance checklist

- [x] Analysis request and response have bounded, validated schemas.
- [x] FastAPI calls Ollama's local chat API using configurable URL and model settings.
- [x] Evidence quotes are checked as exact substrings of the submitted agreement.
- [x] Invented or missing evidence forces `needs_review` and human review.
- [x] Ollama connection, timeout, upstream, and invalid-output errors map to API errors.
- [x] The frontend uploads an agreement, submits a request, and displays verified evidence.
- [x] Deterministic tests mock the model; Phase 1/2 tests and frontend build pass.
- [x] Gemma 3 4B is installed and a real API inference request succeeded.

## Local model setup

Install Ollama for Windows, then in PowerShell run:

```powershell
ollama pull gemma3:4b
ollama list
Invoke-RestMethod http://localhost:11434/api/tags
```

The API defaults to `http://127.0.0.1:11434` and `gemma3:4b`. Override those
values in the backend process if needed:

```powershell
$env:OLLAMA_BASE_URL = "http://127.0.0.1:11434"
$env:OLLAMA_MODEL = "gemma3:4b"
```

Start Ollama and the FastAPI backend, then use the frontend at
`http://localhost:5173`. Upload a `.txt` or text-based `.pdf` agreement, enter a
client request, and choose **Review request**. Inference can take a few minutes
on the first request. Scanned PDFs are not OCR processed.

Automated tests mock Ollama so they do not require a running model. The model is
not used as a source of truth: unverified quotations are removed, and the result
is downgraded to `needs_review`.
