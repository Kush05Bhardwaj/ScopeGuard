import { useEffect, useState, type ChangeEvent, type FormEvent } from "react";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

type HealthResponse = { status: string; service: string; mode: string };
type AgreementPage = { page_number: number; text: string };
type ParsedAgreement = {
  filename: string;
  content_type: string;
  page_count: number;
  text: string;
  pages: AgreementPage[];
};
type EvidenceItem = { quote: string; explanation: string };
type ScopeCategory = "in_scope" | "potential_scope_change" | "needs_review";
type ScopeAnalysis = {
  category: ScopeCategory;
  summary: string;
  reasoning: string;
  evidence: EvidenceItem[];
  model: string;
  requires_human_review: boolean;
};

const categoryLabels: Record<ScopeCategory, string> = {
  in_scope: "In scope",
  potential_scope_change: "Potential scope change",
  needs_review: "Needs review",
};

async function responseError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: unknown };
    if (typeof data.detail === "string") return data.detail;
  } catch {
    // Fall back to the HTTP status when the API body is not JSON.
  }
  return `API returned HTTP ${response.status}`;
}

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [backendError, setBackendError] = useState<string | null>(null);
  const [agreement, setAgreement] = useState<ParsedAgreement | null>(null);
  const [clientRequest, setClientRequest] = useState("");
  const [analysis, setAnalysis] = useState<ScopeAnalysis | null>(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const agreementTooLong = (agreement?.text.length ?? 0) > 100_000;

  useEffect(() => {
    const controller = new AbortController();
    async function checkBackend() {
      try {
        const response = await fetch(`${API_BASE}/api/health`, { signal: controller.signal });
        if (!response.ok) throw new Error(`API returned HTTP ${response.status}`);
        setHealth((await response.json()) as HealthResponse);
        setBackendError(null);
      } catch (err) {
        if (controller.signal.aborted) return;
        setBackendError(err instanceof Error ? err.message : "Unable to reach the API");
      }
    }
    void checkBackend();
    return () => controller.abort();
  }, []);

  async function uploadAgreement(event: ChangeEvent<HTMLInputElement>) {
    const input = event.currentTarget;
    const file = input.files?.[0];
    if (!file) return;
    setAgreement(null);
    setAnalysis(null);
    setError(null);
    setUploading(true);
    const form = new FormData();
    form.append("file", file);
    try {
      const response = await fetch(`${API_BASE}/api/agreements/parse`, { method: "POST", body: form });
      if (!response.ok) throw new Error(await responseError(response));
      setAgreement((await response.json()) as ParsedAgreement);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to parse this agreement.");
    } finally {
      setUploading(false);
      input.value = "";
    }
  }

  async function runAnalysis(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!agreement || !clientRequest.trim()) return;
    setAnalysis(null);
    setError(null);
    setAnalyzing(true);
    try {
      const response = await fetch(`${API_BASE}/api/analysis/scope`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agreement_text: agreement.text, client_request: clientRequest }),
      });
      if (!response.ok) throw new Error(await responseError(response));
      setAnalysis((await response.json()) as ScopeAnalysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to analyze this request.");
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <main className="app">
      <header className="topbar">
        <a className="brand" href="/" aria-label="ScopeGuard Local home">
          <span className="brand-mark">S</span>
          <span>ScopeGuard<span className="muted"> Local</span></span>
        </a>
        <div className="topbar-meta">
          <span className="privacy-label">LOCAL-FIRST</span>
          <span className="connection" aria-live="polite">
            <i className={`status-dot ${health ? "online" : ""}`} />
            {health ? "API connected" : backendError ? "API unavailable" : "Connecting"}
          </span>
        </div>
      </header>

      <section className="hero">
        <p className="eyebrow">SCOPE REVIEW · PRIVATE BY DESIGN</p>
        <h1>Keep the scope clear.</h1>
        <p className="subtitle">Compare a new client request with the agreement. Review the source passages before deciding what to do next.</p>

        {backendError && <p className="notice error-notice">Backend connection failed: {backendError}</p>}
        {error && <p className="notice error-notice" role="alert">{error}</p>}

        <form className="workspace" onSubmit={(event) => void runAnalysis(event)}>
          <section className="input-card" aria-labelledby="agreement-heading">
            <div className="step-label"><span>01</span><span>AGREEMENT</span></div>
            <h2 id="agreement-heading">Add the agreed scope</h2>
            <p className="card-help">Upload a text file or a PDF with selectable text. Files are parsed locally and are not saved.</p>
            <label className="upload-zone">
              <input type="file" accept=".txt,.pdf,text/plain,application/pdf" onChange={(event) => void uploadAgreement(event)} disabled={uploading || analyzing} />
              <span className="upload-icon" aria-hidden="true">↑</span>
              <span className="upload-title">{uploading ? "Reading agreement…" : "Choose an agreement"}</span>
              <span className="upload-subtitle">TXT or text-based PDF · up to 10 MB</span>
            </label>
            {agreement && (
              <div className="file-ready" role="status">
                <span className="file-check">✓</span>
                <div><strong>{agreement.filename}</strong><p>{agreement.page_count} {agreement.page_count === 1 ? "page" : "pages"} parsed · text stays on this device</p>
                  {agreementTooLong && <p className="inline-warning">This agreement exceeds the 100,000-character analysis limit. Upload a shorter text selection to continue.</p>}
                </div>
              </div>
            )}
          </section>

          <section className="input-card" aria-labelledby="request-heading">
            <div className="step-label"><span>02</span><span>CLIENT REQUEST</span></div>
            <h2 id="request-heading">What changed?</h2>
            <p className="card-help">Paste the new request as the client sent it.</p>
            <label className="visually-hidden" htmlFor="client-request">Client request</label>
            <textarea
              id="client-request"
              value={clientRequest}
              onChange={(event) => setClientRequest(event.target.value)}
              maxLength={10_000}
              placeholder="For example: Please add an administrator dashboard and recurring subscriptions."
              rows={7}
              disabled={analyzing}
            />
            <div className="field-meta"><span>Request text is sent only to your configured local API.</span><span>{clientRequest.length.toLocaleString()} / 10,000</span></div>
            <button className="analyze-button" type="submit" disabled={!agreement || agreementTooLong || !clientRequest.trim() || uploading || analyzing}>
              {analyzing ? "Analyzing locally…" : "Review request"}<span aria-hidden="true">→</span>
            </button>
          </section>
        </form>

        {analyzing && <p className="inference-note" role="status">Local model inference can take a few minutes on the first request.</p>}

        {analysis && (
          <section className="result-card" aria-labelledby="result-heading" aria-live="polite">
            <div className="result-topline">
              <div className={`category-badge category-${analysis.category}`}><span className="category-dot" />{categoryLabels[analysis.category]}</div>
              <span className="model-label">LOCAL MODEL · {analysis.model}</span>
            </div>
            <h2 id="result-heading">{analysis.summary}</h2>
            <p className="reasoning">{analysis.reasoning}</p>

            {analysis.requires_human_review && <p className="review-notice">Review the agreement and evidence yourself before responding to the client.</p>}

            <div className="evidence-heading"><span>SUPPORTING PASSAGES</span><span>VERIFIED AGAINST AGREEMENT</span></div>
            {analysis.evidence.length ? (
              <div className="evidence-list">
                {analysis.evidence.map((item, index) => {
                  const page = agreement?.pages.find((source) => source.text.includes(item.quote));
                  return (
                    <blockquote className="evidence-item" key={`${item.quote}-${index}`}>
                      <p>“{item.quote}”</p>
                      <footer><span>{item.explanation}</span><span className="page-ref">{page ? `Page ${page.page_number}` : "Agreement text"}</span></footer>
                    </blockquote>
                  );
                })}
              </div>
            ) : <p className="no-evidence">The model could not provide a verified passage. Human review is required.</p>}
            <p className="disclaimer">Decision support only. This is not a legal conclusion. No response is sent to the client.</p>
          </section>
        )}
        <p className="footer-note">Agreement text and requests are processed by your local ScopeGuard API and Ollama runtime.</p>
      </section>
    </main>
  );
}

export default App;
