import { useEffect, useState } from "react";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

type HealthResponse = { status: string; service: string; mode: string };

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    async function checkBackend() {
      try {
        const response = await fetch(`${API_BASE}/api/health`, { signal: controller.signal });
        if (!response.ok) throw new Error(`API returned HTTP ${response.status}`);
        setHealth((await response.json()) as HealthResponse);
        setError(null);
      } catch (err) {
        if (controller.signal.aborted) return;
        setError(err instanceof Error ? err.message : "Unable to reach the API");
      }
    }
    void checkBackend();
    return () => controller.abort();
  }, []);

  return (
    <main className="app">
      <header className="topbar">
        <a className="brand" href="/" aria-label="ScopeGuard Local home">
          <span className="brand-mark">S</span><span>ScopeGuard<span className="muted"> Local</span></span>
        </a>
        <span className="privacy-label">LOCAL-FIRST</span>
      </header>
      <section className="hero">
        <p className="eyebrow">YOUR WORK. YOUR DATA.</p>
        <h1>Keep the scope clear.</h1>
        <p className="subtitle">Understand what was agreed, identify potential scope changes, and prepare clearer conversations with clients.</p>
        <div className="status-card" aria-live="polite">
          <span className={`status-dot ${health ? "online" : ""}`} />
          <div><strong>{health ? "Backend connected" : "Backend connection"}</strong><p>{health ? "Your local API is responding." : error ? `Not connected: ${error}` : "Checking the local API..."}</p></div>
        </div>
        <div className="feature-grid">
          <article className="feature-card"><span className="feature-number">01</span><h2>Define the scope</h2><p>Start with the original agreement and its requirements.</p></article>
          <article className="feature-card"><span className="feature-number">02</span><h2>Review new requests</h2><p>Compare client requests with the agreed deliverables.</p></article>
          <article className="feature-card"><span className="feature-number">03</span><h2>Keep the evidence</h2><p>Review supporting passages before drafting a response.</p></article>
        </div>
        <p className="footer-note">Foundation build · AI analysis arrives in a later phase.</p>
      </section>
    </main>
  );
}

export default App;
