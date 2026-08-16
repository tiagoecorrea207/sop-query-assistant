import React, { useRef, useState, DragEvent } from 'react';
import { UploadStatus } from '../types';

interface Props {
  status:   UploadStatus;
  filename: string | null;
  error:    string | null;
  onFile:   (file: File) => void;
}

export const UploadZone: React.FC<Props> = ({ status, filename, error, onFile }) => {
  const inputRef          = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) onFile(file);
  };

  const label = () => {
    switch (status) {
      case 'idle':        return <><span className="upload-icon">⬆</span><span className="upload-main">Drop audit criteria here</span><span className="upload-sub">PDF or DOCX · click to browse</span></>;
      case 'uploading':   return <><span className="upload-spinner" /><span className="upload-main">Uploading…</span></>;
      case 'classifying': return <><span className="upload-spinner" /><span className="upload-main">Classifying document…</span><span className="upload-sub">Claude verifying audit criteria</span></>;
      case 'ready':       return <><span className="upload-check">✓</span><span className="upload-main upload-main--ready">{filename}</span><span className="upload-sub">Loaded · click to replace</span></>;
      case 'error':       return <><span className="upload-icon upload-icon--error">✕</span><span className="upload-main upload-main--error">{error}</span><span className="upload-sub">Click to try again</span></>;
    }
  };

  return (
    <div
      className={['upload-zone', dragging ? 'upload-zone--dragging' : '', status === 'ready' ? 'upload-zone--ready' : '', status === 'error' ? 'upload-zone--error' : ''].filter(Boolean).join(' ')}
      onClick={() => inputRef.current?.click()}
      onDragOver={e => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      role="button" tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && inputRef.current?.click()}
    >
      {label()}
      <input ref={inputRef} type="file" accept=".pdf,.docx" style={{ display: 'none' }}
        onChange={e => { const f = e.target.files?.[0]; if (f) onFile(f); }} />
    </div>
  );
};
