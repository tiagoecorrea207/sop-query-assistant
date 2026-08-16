import React from 'react';
import { AuditEntry } from '../types';

const BADGE: Record<string, { text: string; cls: string }> = {
  answer:          { text: 'ANSWER',       cls: 'badge--answer' },
  not_found:       { text: 'NOT FOUND',    cls: 'badge--not-found' },
  out_of_context:  { text: 'OUT OF SCOPE', cls: 'badge--out-of-context' },
  error:           { text: 'ERROR',        cls: 'badge--error' },
};

export const AuditEntryCard: React.FC<{ entry: AuditEntry; index: number }> = ({ entry, index }) => {
  const badge = BADGE[entry.type] || BADGE.error;
  const answer = (entry.answer || '').replace(/^(OUT_OF_CONTEXT|NOT_FOUND):\s*/i, '');
  const sources = Array.isArray(entry.sources) ? entry.sources : [];

  return (
    <article className="entry-card" style={{ animationDelay: `${index * 30}ms` }}>
      <div className="entry-card__header">
        <span className={`badge ${badge.cls}`}>{badge.text}</span>
        <time className="entry-card__time">{entry.timestamp}</time>
      </div>
      <p className="entry-card__question">{entry.question}</p>
      <div className="entry-card__rule" />
      <div className="entry-card__answer">
        {answer.split('\n').map((l, i) => <p key={i}>{l}</p>)}
      </div>
      {sources.length > 0 && (
        <div className="entry-card__sources">
          <span className="sources-label">SOURCES</span>
          <div className="source-pills">
            {sources.map(src => (
              <span key={src} className="source-pill">
                {src.length > 48 ? '…' + src.slice(-42) : src}
              </span>
            ))}
          </div>
        </div>
      )}
      {entry.webErrors && entry.webErrors.length > 0 && (
        <div className="entry-card__web-errors">
          <span className="sources-label sources-label--warn">WEB ERRORS</span>
          {entry.webErrors.map((e, i) => <p key={i} className="web-error-line">{e}</p>)}
        </div>
      )}
    </article>
  );
};
