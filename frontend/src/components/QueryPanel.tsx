import React, { KeyboardEvent, useState } from 'react';
import { QueryStatus } from '../types';

interface Props {
  question:           string;
  onQuestionChange:   (v: string) => void;
  webSopUrls:         string;
  onWebSopUrlsChange: (v: string) => void;
  onSubmit:           () => void;
  status:             QueryStatus;
  auditReady:         boolean;
}

export const QueryPanel: React.FC<Props> = ({
  question, onQuestionChange, webSopUrls, onWebSopUrlsChange,
  onSubmit, status, auditReady,
}) => {
  const [showUrls, setShowUrls] = useState(false);
  const loading = status === 'loading';

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) { e.preventDefault(); onSubmit(); }
  };

  return (
    <section className="query-panel">
      <label className="field-label">QUERY</label>
      <textarea
        className="query-textarea"
        value={question}
        onChange={e => onQuestionChange(e.target.value)}
        onKeyDown={handleKey}
        placeholder={auditReady
          ? 'Ask a question about the loaded SOPs and audit criteria…'
          : 'Load an audit criteria document above to begin'}
        disabled={!auditReady || loading}
        rows={4}
      />
      <div className="query-actions">
        <button className="btn-ghost" type="button" disabled={loading}
          onClick={() => setShowUrls(v => !v)}>
          {showUrls ? '− Web SOPs' : '+ Web SOPs'}
        </button>
        <div className="query-hint">⌘ + Enter</div>
        <button className="btn-primary" type="button"
          onClick={onSubmit}
          disabled={!auditReady || !question.trim() || loading}>
          {loading ? <><span className="btn-spinner" /> Querying…</> : 'Send'}
        </button>
      </div>
      {showUrls && (
        <div className="web-sop-panel">
          <label className="field-label field-label--sm">
            WEB SOP URLS <span className="field-hint">— one per line</span>
          </label>
          <textarea className="url-textarea" value={webSopUrls} rows={3}
            onChange={e => onWebSopUrlsChange(e.target.value)} disabled={loading}
            placeholder="https://example.com/sop-calibration" />
        </div>
      )}
    </section>
  );
};
