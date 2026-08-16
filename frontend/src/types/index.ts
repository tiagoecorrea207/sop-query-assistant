export type ResponseType = 'answer' | 'not_found' | 'out_of_context' | 'error';

export interface AuditEntry {
  id:            string;
  question:      string;
  answer:        string;
  sources:       string[];
  type:          ResponseType;
  timestamp:     string;
  webErrors?:    string[];
}

export interface QueryResponse {
  type:          ResponseType;
  answer:        string;
  sources:       string[];
  response_type: string;
  web_errors?:   string[];
}

export type UploadStatus = 'idle' | 'uploading' | 'classifying' | 'ready' | 'error';
export type QueryStatus  = 'idle' | 'loading' | 'done' | 'error';
