"use client";

import { useCallback, useEffect, useState } from "react";
import { processDocument, fetchHistory } from "./api";
import { ProcessedDocument, HistoryRow } from "../types";

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [statusIsError, setStatusIsError] = useState(false);
  const [result, setResult] = useState<ProcessedDocument | null>(null);
  const [history, setHistory] = useState<HistoryRow[]>([]);

  const loadHistory = useCallback(async () => {
    try {
      const rows = await fetchHistory();
      setHistory(rows);
    } catch {
      // Backend not reachable yet — leave history as-is, the panel shows an empty state
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  function onFileChosen(file: File) {
    setSelectedFile(file);
    setResult(null);
    setStatusMessage("");
    setStatusIsError(false);
  }

  async function handleProcess() {
    if (!selectedFile) return;
    setIsProcessing(true);
    setStatusIsError(false);
    setStatusMessage("Processing — this calls the AI pipeline, may take a few seconds…");
    setResult(null);

    try {
      const doc = await processDocument(selectedFile);
      setResult(doc);
      setStatusMessage("");
      loadHistory();
    } catch (err) {
      setStatusIsError(true);
      setStatusMessage(`Failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsProcessing(false);
    }
  }

  return (
    <>
      <header>
        <h1>Document Intelligence</h1>
        <p>Upload a PDF — it gets classified, extracted, and flagged automatically.</p>
      </header>

      <main>
        <section className="panel">
          <div
            className={`drop${isDragOver ? " dragover" : ""}`}
            onClick={() => document.getElementById("fileInput")?.click()}
            onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setIsDragOver(false);
              if (e.dataTransfer.files.length) onFileChosen(e.dataTransfer.files[0]);
            }}
          >
            <p><strong>Click to choose a PDF</strong> or drag one here</p>
          </div>
          <input
            id="fileInput"
            type="file"
            accept="application/pdf"
            style={{ display: "none" }}
            onChange={(e) => { if (e.target.files?.length) onFileChosen(e.target.files[0]); }}
          />

          {selectedFile && <div className="filename">{selectedFile.name}</div>}

          <button onClick={handleProcess} disabled={!selectedFile || isProcessing}>
            Process document
          </button>

          {statusMessage && (
            <div className={`status${statusIsError ? " error" : ""}`}>{statusMessage}</div>
          )}

          {result && <ResultView doc={result} />}
        </section>

        <section className="panel">
          <h2 style={{ marginTop: 0, fontSize: "1.05rem" }}>Recent documents</h2>
          <HistoryTable rows={history} />
        </section>
      </main>
    </>
  );
}

function ResultView({ doc }: { doc: ProcessedDocument }) {
  const { classification: c, fields, flagged, flag_reason } = doc;
  return (
    <div className="result">
      <div className="result-head">
        <div>
          <span className="doc-type">{c.doc_type.replace(/_/g, " ")}</span>
          <span className="confidence"> · {(c.confidence * 100).toFixed(0)}% confidence</span>
        </div>
        <span className={`badge ${flagged ? "flagged" : "clear"}`}>
          {flagged ? `Flagged — ${flag_reason}` : "Clear"}
        </span>
      </div>
      <table className="fields">
        <tbody>
          {Object.entries(fields).map(([key, value]) => (
            <tr key={key}>
              <td>{key.replace(/_/g, " ")}</td>
              <td>{value ? value : <span className="empty">not found</span>}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function HistoryTable({ rows }: { rows: HistoryRow[] }) {
  if (!rows.length) {
    return <div className="empty-state">No documents processed yet.</div>;
  }
  return (
    <table className="history">
      <thead>
        <tr>
          <th>File</th>
          <th>Type</th>
          <th>Confidence</th>
          <th>Status</th>
          <th>Processed</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.id}>
            <td>
              <span className={`dot ${row.flagged ? "flagged" : "clear"}`} />
              {row.filename}
            </td>
            <td>{(row.doc_type || "").replace(/_/g, " ")}</td>
            <td>{row.confidence != null ? `${(row.confidence * 100).toFixed(0)}%` : "—"}</td>
            <td>{row.flagged ? row.flag_reason || "Flagged" : "Clear"}</td>
            <td>{row.created_at}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
