# ScopeGuard Local

ScopeGuard Local helps freelancers compare a new client request with a project
agreement, review the supporting passages, and prepare an editable change-order
proposal. The current workflow uses a local FastAPI service and Ollama by
default.

## What works today

- Upload UTF-8 `.txt` agreements or text-based `.pdf` agreements. PDF text keeps
  page references. Uploads are parsed in memory; scanned PDFs are not OCR
  processed.
- Compare a client request with the agreement using Ollama and Gemma 3 4B.
- Review one of three classifications: `in_scope`,
  `potential_scope_change`, or `needs_review`.
- Check the model's evidence quotations against the original agreement text.
  Missing or invented evidence requires human review. Exact quotations do not
  prove that the model interpreted them correctly.
- Generate a change-order proposal from the validated analysis, edit it in the
  browser, then copy it or download it as Markdown. Unprovided cost and timeline
  remain “To be agreed.” Report generation does not make another model call.

ScopeGuard is decision support, not legal advice. Review the agreement,
classification, evidence, and proposal yourself before discussing a change with
a client. The project does not currently store projects or report history in
SQLite, export PDF, or contact clients.

## Requirements

- Windows 11 with PowerShell
- Python 3.12 recommended (Python 3.14 was also used for validation)
- Node.js 22 or newer with npm
- [Ollama for Windows](https://ollama.com/download/windows)

The local inference setup uses [Gemma 3 4B](https://ollama.com/library/gemma3).
You can configure a different Ollama-compatible model with `OLLAMA_MODEL`.

## Run locally

### 1. Install the model

Start the Ollama application, then run in PowerShell:

```powershell
ollama pull gemma3:4b
ollama list
```

Ollama normally runs its local API at `http://127.0.0.1:11434`. If it is not
running, start Ollama before using analysis.

### 2. Set up and start the backend

From the repository root:

```powershell
py -3.12 -m venv backend\.venv
.\backend\.venv\Scripts\python.exe -m pip install --upgrade pip
.\backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

Leave this PowerShell window open. The backend uses Ollama at
`http://127.0.0.1:11434` and model `gemma3:4b` by default. Set
`OLLAMA_BASE_URL` or `OLLAMA_MODEL` in the backend process environment to
override those defaults.

### 3. Set up and start the frontend

In a second PowerShell window, from the repository root:

```powershell
Copy-Item frontend\.env.example frontend\.env.local
Set-Location frontend
npm.cmd install
npm.cmd run dev
```

Open the Vite URL shown in the terminal (normally
`http://localhost:5173`). The frontend API URL defaults to
`http://127.0.0.1:8000`; set `VITE_API_BASE_URL` in
`frontend/.env.local` to change it, then restart Vite.

The API root is `http://127.0.0.1:8000/`, health check is
`http://127.0.0.1:8000/api/health`, and interactive API docs are at
`http://127.0.0.1:8000/docs`.

### Troubleshooting

- **Backend connection failed:** Start the backend command above and confirm
  `frontend/.env.local` points to the backend URL.
- **Ollama unavailable (HTTP 503):** Start the Ollama application and confirm
  `gemma3:4b` appears in `ollama list`.
- **Analysis is slow:** The first local model request may take longer while
  Ollama loads the model.
- **PDF has no text:** Scanned documents are not OCR processed. Use a
  text-based PDF or a UTF-8 text file.

## Use the workflow

1. Upload a `.txt` agreement or a PDF with selectable text (maximum 10 MB and
   100 pages).
2. Enter the client's request and choose **Review request**.
3. Review the classification, explanation, exact source quotations, and any
   human-review notice.
4. Enter proposal details and choose **Generate proposal**.
5. Edit the Markdown proposal, then choose **Export Markdown** or **Copy
   proposal**.

The included agreement and requests in `sample_data/` are synthetic examples.
They are suitable for local development and should not be treated as contracts.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Check that the backend is responding. |
| `POST` | `/api/agreements/parse` | Parse one TXT or text-based PDF upload in memory. |
| `POST` | `/api/analysis/scope` | Compare agreement text and a client request using Ollama. |
| `POST` | `/api/reports/change-order` | Validate analysis evidence and return a Markdown proposal. |

See the interactive API documentation at `/docs` while the backend is running.

## Tests and production build

Run backend tests from the repository root:

```powershell
$env:PYTHONPATH = "$PWD\backend"
.\backend\.venv\Scripts\python.exe -m pytest backend\tests -v
```

Build the frontend:

```powershell
Set-Location frontend
npm.cmd run build
```

## Local-first behavior and privacy

With the default configuration, the browser talks to the API on
`127.0.0.1:8000`, and the backend talks to Ollama on `127.0.0.1:11434`.
Agreement files are parsed in memory and are not persisted by the application.
Application code does not log agreement or request contents.

If you configure either service URL to a different host, agreement and request
text may be sent to that host. Do not upload confidential client documents to a
custom or shared service unless you have reviewed its data handling. Local
defaults are not a blanket privacy guarantee.

Real client agreements, credentials, local environment files, databases, and
uploads should not be committed. `.gitignore` excludes common local files;
check `git status` before committing.

## Documentation

- [MVP goals and current status](docs/MVP.md)
- [Architecture and data flow](docs/ARCHITECTURE.md)

## License

MIT. See [LICENSE](LICENSE).
