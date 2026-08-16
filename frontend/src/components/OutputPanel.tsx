import React, { useEffect, useRef } from 'react';
import { AuditEntry } from '../types';
import { AuditEntryCard } from './AuditEntryCard.tsx';

interface Props {
  entries:  AuditEntry[];
  onExport: () => void;
  onClear:  () => void;
}

export const OutputPanel: React.FC<Props> = ({ entries, onExport, onClear }) => {
  const topRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (entries.length > 0) topRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, [entries.length]);

  return (
    <section className="output-panel">
      <div className="output-header">
        <div className="output-header__left">
          <h2 className="output-title">Audit Log</h2>
          {entries.length > 0 && (
            <span className="output-count">{entries.length} {entries.length === 1 ? 'entry' : 'entries'}</span>
          )}
        </div>
        {entries.length > 0 && (
          <div className="output-header__actions">
            <button className="btn-ghost btn-ghost--sm" onClick={onClear} type="button">Clear</button>
            <button className="btn-export" onClick={onExport} type="button">Save as PDF</button>
          </div>
        )}
      </div>
      <div ref={topRef} />
      <div className="output-entries">
        {entries.length === 0 ? (
          <div className="output-empty">
            <div className="output-empty__icon">⬡</div>
            <p className="output-empty__title">No entries yet</p>
            <p className="output-empty__sub">Upload an audit criteria document and submit a query. Results accumulate here and can be saved as a PDF.</p>
          </div>
        ) : (
          entries.map((e, i) => <AuditEntryCard key={e.id} entry={e} index={i} />)
        )}
      </div>
    </section>
  );
};
