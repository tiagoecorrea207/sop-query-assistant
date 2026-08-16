import React from 'react';
import { UploadZone } from './UploadZone.tsx';
import { QueryPanel } from './QueryPanel.tsx';
import { UploadStatus, QueryStatus } from '../types';

interface Props {
  uploadStatus: UploadStatus; uploadedFilename: string | null;
  uploadError: string | null; onFile: (f: File) => void;
  question: string; onQuestionChange: (v: string) => void;
  webSopUrls: string; onWebSopUrlsChange: (v: string) => void;
  onSubmit: () => void; queryStatus: QueryStatus; entryCount: number;
}

export const Sidebar: React.FC<Props> = ({
  uploadStatus, uploadedFilename, uploadError, onFile,
  question, onQuestionChange, webSopUrls, onWebSopUrlsChange,
  onSubmit, queryStatus, entryCount,
}) => (
  <aside className="sidebar">
    <div className="sidebar__brand">
      <span className="brand-mark">◈</span>
      <div>
        <div className="brand-name">SOP Audit</div>
        <div className="brand-sub">RAG · pgvector · Claude</div>
      </div>
    </div>
    <div className="sidebar__divider" />
    <div className="sidebar__section">
      <div className="step-label">
        <span className="step-num">01</span>
        <span className="step-text">AUDIT CRITERIA</span>
      </div>
      <UploadZone status={uploadStatus} filename={uploadedFilename} error={uploadError} onFile={onFile} />
    </div>
    <div className="sidebar__divider" />
    <div className="sidebar__section">
      <div className="step-label">
        <span className="step-num">02</span>
        <span className="step-text">QUERY</span>
      </div>
      <QueryPanel
        question={question} onQuestionChange={onQuestionChange}
        webSopUrls={webSopUrls} onWebSopUrlsChange={onWebSopUrlsChange}
        onSubmit={onSubmit} status={queryStatus}
        auditReady={uploadStatus === 'ready'}
      />
    </div>
    <div className="sidebar__footer">
      {entryCount > 0 && <p className="footer-note">{entryCount} result{entryCount > 1 ? 's' : ''} in log</p>}
      <p className="footer-note footer-note--dim">SOPs loaded at startup · audit criteria per session</p>
    </div>
  </aside>
);
