import React from 'react';
import { Sidebar } from './components/Sidebar.tsx';
import { OutputPanel } from './components/OutputPanel.tsx';
import { StatusBar } from './components/StatusBar.tsx';
import { useAuditSession } from './hooks/useAuditSession.ts';
import './App.css';

const App: React.FC = () => {
  const {
    uploadStatus, uploadedFilename, uploadError, uploadAuditDoc,
    queryStatus, currentQuestion, setCurrentQuestion,
    webSopUrls, setWebSopUrls, submitQuery,
    entries, clearSession, handleExportPDF,
  } = useAuditSession();

  return (
    <div className="app-shell">
      <StatusBar onRejectedSops={() => {}} />
      <div className="app-body">
        <Sidebar
          uploadStatus={uploadStatus} uploadedFilename={uploadedFilename}
          uploadError={uploadError} onFile={uploadAuditDoc}
          question={currentQuestion} onQuestionChange={setCurrentQuestion}
          webSopUrls={webSopUrls} onWebSopUrlsChange={setWebSopUrls}
          onSubmit={submitQuery} queryStatus={queryStatus}
          entryCount={entries.length}
        />
        <main className="main-content">
          <OutputPanel entries={entries} onExport={handleExportPDF} onClear={clearSession} />
        </main>
      </div>
    </div>
  );
};

export default App;
