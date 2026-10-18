# ScopeGuard Local

A local-first assistant for comparing client requests with an agreed project scope.

## Stack

- Frontend: React, Vite, TypeScript
- Backend: Python, FastAPI
- Planned storage: SQLite
- Local inference: Ollama with Gemma 3 4B

## Development

Run the API from the repository root:

```powershell
py -3.14 -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

In a second PowerShell window, run the frontend:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

The API is at http://127.0.0.1:8000 and its health check is at
http://127.0.0.1:8000/api/health. The frontend is at http://localhost:5173.
Copy `frontend/.env.example` to `frontend/.env.local` to configure the API URL.

Agreement text can be parsed with `POST /api/agreements/parse` using a multipart
`file` field containing a UTF-8 `.txt` or text-based `.pdf` file. Uploads are
limited to 10 MB and PDFs to 100 pages. Files are parsed in memory and are not
saved. Scanned PDFs are not OCR processed.

Scope review is available at `POST /api/analysis/scope`. It calls a local Ollama
server (defaults: `http://127.0.0.1:11434`, model `gemma3:4b`) and verifies every
evidence quote against the submitted agreement before returning it.

Change-order proposals are generated from a reviewed analysis with
`POST /api/reports/change-order`. When enabled, the local model suggests a rough
cost range and timeline for missing values and lists its assumptions. Treat
these as editable planning estimates, not a quote. The frontend lets you edit
the Markdown, then download the final draft as Markdown or PDF.

By default, the frontend API URL and Ollama URL point to `127.0.0.1`, so
agreement parsing and inference run on the same device. If you override either
URL, agreement and request text may be sent to that configured host. Application
code does not log agreement or request contents. This is a local-first default,
not a guarantee of privacy for every custom deployment.

Python 3.12 is the recommended baseline; the environment used to establish this
foundation has Python 3.14. Node.js 22 LTS is recommended; Node.js 24 is installed.
If PowerShell blocks the `npm` script, invoke `npm.cmd` as shown above.

See the [MVP](docs/MVP.md) and [architecture](docs/ARCHITECTURE.md) for product
scope and implementation details. Persistent project storage is planned for a
later release.

## Privacy

Do not commit real client agreements, credentials, or confidential customer data.
The included sample agreement and requests are synthetic.

## License

MIT
