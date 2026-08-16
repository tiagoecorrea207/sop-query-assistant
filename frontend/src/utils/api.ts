import { AuditEntry, QueryResponse } from '../types';

const BASE   = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WS_BASE = process.env.REACT_APP_WS_URL  || 'ws://localhost:8000';

export async function fetchHealth() {
  const res = await fetch(`${BASE}/health`);
  if (!res.ok) throw new Error('Backend unreachable');
  return res.json() as Promise<{ status: string; model: string; chunk_count: number }>;
}

export async function ingestAuditDocument(file: File): Promise<{ filename: string }> {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${BASE}/ingest-audit`, { method: 'POST', body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(err.detail || `Error ${res.status}`);
  }
  return res.json();
}

export async function exportPDF(entries: AuditEntry[]): Promise<void> {
  const exportEntries = entries.map((entry) => ({
    question: entry.question,
    answer: entry.answer || '',
    sources: Array.isArray(entry.sources) ? entry.sources : [],
    response_type: entry.type,
    timestamp: entry.timestamp,
  }));

  const res = await fetch(`${BASE}/export-pdf`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ entries: exportEntries }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'PDF export failed' }));
    throw new Error(err.detail || 'PDF export failed');
  }
  const blob = await res.blob();
  const url  = window.URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = `audit-session-${new Date().toISOString().slice(0, 10)}.pdf`;
  a.click();
  window.URL.revokeObjectURL(url);
}

export function createQuerySocket(
  question:    string,
  webSopUrls:  string[],
  onMessage:   (data: QueryResponse) => void,
  onError:     (msg: string) => void,
): WebSocket {
  const ws = new WebSocket(`${WS_BASE}/query`);
  ws.onopen    = () => ws.send(JSON.stringify({ question, web_sop_urls: webSopUrls }));
  ws.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);

      if (data.type === 'error') {
        onError(data.value || 'Query failed');
        return;
      }

      if (data.type !== 'done') {
        return;
      }

      onMessage({
        type: data.response_type || 'error',
        answer: data.answer || '',
        sources: Array.isArray(data.sources) ? data.sources : [],
        response_type: data.response_type || 'error',
        web_errors: Array.isArray(data.web_errors) ? data.web_errors : [],
      });
    }
    catch {
      onError('Malformed response from server');
    }
  };
  ws.onerror   = () => onError('Connection to server lost');
  return ws;
}
