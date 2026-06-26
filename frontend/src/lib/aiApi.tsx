import { API_BASE } from '../config';

export interface Session {
  id: string;
  name: string;
  created_at: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface AIQueryResponse {
  answer: string;
  sources: string[];
}

export async function ingestFile(file: File, sessionId: string): Promise<{ chunks_indexed: number }> {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Authorization token is missing');

  const formData = new FormData();
  formData.append('file', file);
  formData.append('session_id', sessionId);

  const response = await fetch(`${API_BASE}/api/ai/ingest`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to ingest file');
  }

  return response.json();
}

export async function queryAI(query: string, sessionId: string): Promise<AIQueryResponse> {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Authorization token is missing');

  const response = await fetch(`${API_BASE}/api/ai/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ query, session_id: sessionId }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to query AI');
  }

  return response.json();
}

export async function streamAnswer(
  query: string,
  sessionId: string,
  onToken: (token: string) => void,
  onDone: (citations: string[]) => void
): Promise<void> {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Authorization token is missing');

  const url = `${API_BASE}/api/ai/stream?query=${encodeURIComponent(query)}&session_id=${encodeURIComponent(sessionId)}`;
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to stream AI response');
  }

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const lines = decoder.decode(value).split('\n').filter((line) => line.startsWith('data:'));
    for (const line of lines) {
      const data = JSON.parse(line.slice(5));
      if (data.token) onToken(data.token);
      if (data.done) {
        onDone(data.citations || []);
        return;
      }
    }
  }
}

export async function getSessions(): Promise<Session[]> {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Authorization token is missing');

  const response = await fetch(`${API_BASE}/api/sessions`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to fetch sessions');
  }

  return response.json();
}

export async function createSession(name?: string): Promise<Session> {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Authorization token is missing');

  const response = await fetch(`${API_BASE}/api/sessions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ name }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to create session');
  }

  return response.json();
}

export async function getMessages(sessionId: string): Promise<Message[]> {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Authorization token is missing');

  const response = await fetch(`${API_BASE}/api/sessions/${sessionId}/messages`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to fetch messages');
  }

  return response.json();
}