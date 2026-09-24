import { ProcessedDocument, HistoryRow } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://192.168.189.167:8000";

export async function processDocument(file: File): Promise<ProcessedDocument> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/process-document`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Server responded ${res.status}`);
  }

  return res.json();
}

export async function fetchHistory(): Promise<HistoryRow[]> {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error(`Server responded ${res.status}`);
  return res.json();
}
