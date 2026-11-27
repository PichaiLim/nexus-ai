"use client";

import { useEffect, useState } from "react";

type Model = { id: string; name: string; installed: boolean | null; loaded: boolean | null; served: boolean | null };
type Source = {
  id: string; name: string; engine: string; url: string;
  snapshot: { status: string; synced_at: string | null; error: string | null; models: Model[] };
};
type Action = "test" | "sync";
const endpoint = "/api/v1/model-sources";
const engineNames: Record<string, string> = { ollama: "Ollama", "lm-studio": "LM Studio" };
const demo: Source[] = [
  { id: "demo-ollama", name: "Demo Ollama", engine: "ollama", url: "",
    snapshot: { status: "ready", synced_at: null, error: null, models: [
      { id: "gemma-example", name: "Gemma example", installed: true, loaded: true, served: null },
      { id: "qwen-example", name: "Qwen example", installed: true, loaded: false, served: null },
    ] } },
  { id: "demo-lm", name: "Demo LM Studio", engine: "lm-studio", url: "",
    snapshot: { status: "ready", synced_at: null, error: null, models: [
      { id: "typhoon-example", name: "Typhoon example", installed: true, loaded: false, served: null },
      { id: "openthai-example", name: "OpenThai example", installed: true, loaded: true, served: null },
    ] } },
];

async function request<T>(path: string, method = "GET", signal?: AbortSignal): Promise<T> {
  const response = await fetch(path, { method, signal, cache: "no-store", headers: { "X-Nexus-Request": "1" } });
  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new Error(typeof data?.detail === "string" ? data.detail : "Model Sources API is unavailable.");
  }
  return response.json();
}

export default function ModelSources() {
  const [live, setLive] = useState(false);
  const [sources, setSources] = useState<Source[] | null>(null);
  const [problem, setProblem] = useState("");
  const [busy, setBusy] = useState<Record<string, Action | undefined>>({});
  const [messages, setMessages] = useState<Record<string, string>>({});
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (!live) return;
    const controller = new AbortController();
    request<Source[]>(endpoint, "GET", controller.signal).then(setSources).catch((error: Error) => {
      if (!controller.signal.aborted) setProblem(error.message);
    });
    return () => controller.abort();
  }, [live, attempt]);

  async function run(source: Source, action: Action) {
    if (!live) {
      setMessages(previous => ({ ...previous, [source.id]: action === "test" ? "Simulated connection passed." : "Demo sample refreshed." }));
      return;
    }
    setBusy(previous => ({ ...previous, [source.id]: action }));
    setMessages(previous => ({ ...previous, [source.id]: "" }));
    try {
      const path = `${endpoint}/${encodeURIComponent(source.id)}/${action}`;
      if (action === "test") {
        await request(path, "POST");
        setMessages(previous => ({ ...previous, [source.id]: "Connection passed." }));
      } else {
        const synced = await request<Source>(path, "POST");
        setSources(previous => previous?.map(item => item.id === synced.id ? synced : item) ?? null);
        setMessages(previous => ({ ...previous, [source.id]: synced.snapshot.error ?? "Sync complete." }));
      }
    } catch (error) {
      setMessages(previous => ({ ...previous, [source.id]: error instanceof Error ? error.message : "Request failed." }));
    } finally {
      setBusy(previous => ({ ...previous, [source.id]: undefined }));
    }
  }

  const visible = live ? sources : demo;
  return <div className="model-sources">
      <div className="pagehead">
        <div><div className="eyebrow">Model Studio</div><h1>Model Sources</h1>
          <p>{live ? "Read-only discovery from configured runtimes." : "Sample sources and model statuses for demonstration."}</p>
        </div>
        <div className="row wrap" aria-label="Data mode" role="group">
          <button className={`btn ${live ? "" : "primary"}`} aria-pressed={!live} onClick={() => setLive(false)}>Demo</button>
          <button className={`btn ${live ? "primary" : ""}`} aria-pressed={live} onClick={() => { setProblem(""); setLive(true); }}>Live</button>
        </div>
      </div>
      {live && problem && <p role="alert">{problem} <button className="btn" onClick={() => { setProblem(""); setAttempt(value => value + 1); }}>Retry</button></p>}
      {live && !problem && visible === null && <p role="status">Loading model sources…</p>}
      {visible?.length === 0 && <p className="card">No sources configured. Set NEXUS_MODEL_SOURCES on the API and restart it.</p>}
      {visible?.map(source => <section className="card section" key={source.id} aria-labelledby={`source-${source.id}`}>
        <div className="row wrap"><div><p className="tiny">{engineNames[source.engine] ?? source.engine}</p>
          <h2 id={`source-${source.id}`}>{source.name}</h2>{source.url && <p className="url">{source.url}</p>}
        </div><span className="spacer"></span><span className={`pill state ${source.snapshot.status === "ready" ? "good" : "warn"}`}>{source.snapshot.status}</span></div>
        <div className="row wrap section">
          <button className="btn" disabled={!!busy[source.id]} onClick={() => run(source, "test")}>{busy[source.id] === "test" ? "Testing…" : "Test connection"}</button>
          <button className="btn primary" disabled={!!busy[source.id]} onClick={() => run(source, "sync")}>{busy[source.id] === "sync" ? "Syncing…" : "Sync"}</button>
        </div>
        {source.snapshot.synced_at && <p className="crumb">Last synced {new Date(source.snapshot.synced_at).toLocaleString()}</p>}
        <p role="status" className="feedback">{messages[source.id] || source.snapshot.error}</p>
        {source.snapshot.models.length ? <ul className="models" aria-label="Discovered models">
          {source.snapshot.models.map(model => <li className="listline" key={model.id}><span><strong>{model.name}</strong><small className="tiny">{model.id}</small></span>
            <span>{model.installed === null ? "Install status unknown" : model.installed ? "Installed" : "Not installed"} · {model.served ? "Served" : model.loaded === null ? "Load status unknown" : model.loaded ? "Loaded" : "Not loaded"}</span>
          </li>)}
        </ul> : <p>No models to display.</p>}
      </section>)}
  </div>;
}
