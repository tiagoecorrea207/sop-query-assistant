import { useState, useCallback, useRef } from 'react';
import { AuditEntry, UploadStatus, QueryStatus, QueryResponse } from '../types';
import { ingestAuditDocument, createQuerySocket, exportPDF } from '../utils/api.ts';

let counter = 0;
const uid   = () => `entry-${++counter}-${Date.now()}`;

export function useAuditSession() {
  const [uploadStatus,     setUploadStatus]     = useState<UploadStatus>('idle');
  const [uploadedFilename, setUploadedFilename] = useState<string | null>(null);
  const [uploadError,      setUploadError]      = useState<string | null>(null);
  const [queryStatus,      setQueryStatus]      = useState<QueryStatus>('idle');
  const [currentQuestion,  setCurrentQuestion]  = useState('');
  const [webSopUrls,       setWebSopUrls]       = useState('');
  const [entries,          setEntries]          = useState<AuditEntry[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  const uploadAuditDoc = useCallback(async (file: File) => {
    setUploadStatus('uploading');
    setUploadError(null);
    try {
      setUploadStatus('classifying');
      const res = await ingestAuditDocument(file);
      setUploadedFilename(res.filename);
      setUploadStatus('ready');
    } catch (err: any) {
      setUploadError(err.message || 'Upload failed');
      setUploadStatus('error');
    }
  }, []);

  const submitQuery = useCallback(() => {
    const question = currentQuestion.trim();
    if (!question || queryStatus === 'loading') return;

    const urls = webSopUrls.split('\n').map(u => u.trim()).filter(Boolean);
    setQueryStatus('loading');

    const ws = createQuerySocket(
      question,
      urls,
      (data: QueryResponse) => {
        const entry: AuditEntry = {
          id:        uid(),
          question,
          answer:    data.answer,
          sources:   data.sources,
          type:      data.type,
          timestamp: new Date().toLocaleString('en-GB', {
            day: '2-digit', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit',
          }),
          webErrors: data.web_errors,
        };
        setEntries(prev => [entry, ...prev]);
        setCurrentQuestion('');
        setQueryStatus('done');
        ws.close();
      },
      (errMsg) => {
        setQueryStatus('error');
        setEntries(prev => [{
          id: uid(), question, answer: errMsg,
          sources: [], type: 'error',
          timestamp: new Date().toLocaleString(),
        }, ...prev]);
      }
    );
    wsRef.current = ws;
  }, [currentQuestion, webSopUrls, queryStatus]);

  const clearSession    = useCallback(() => setEntries([]), []);
  const handleExportPDF = useCallback(async () => {
    if (entries.length === 0) return;
    await exportPDF([...entries].reverse());
  }, [entries]);

  return {
    uploadStatus, uploadedFilename, uploadError, uploadAuditDoc,
    queryStatus, currentQuestion, setCurrentQuestion,
    webSopUrls, setWebSopUrls, submitQuery,
    entries, clearSession, handleExportPDF,
  };
}
