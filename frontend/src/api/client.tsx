import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
});

api.interceptors.request.use((config: AxiosRequestConfig) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${token}`,
    };
  }
  return config;
});

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.clear();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  accessToken: string;
}

export const login = (data: LoginRequest) => api.post<LoginResponse>('/api/auth/login', data);

export interface RegisterRequest {
  email: string;
  password: string;
  confirmPassword: string;
}

export interface RegisterResponse {
  message: string;
}

export const register = (data: RegisterRequest) => api.post<RegisterResponse>('/api/auth/register', data);

export interface UploadDocumentRequest {
  file: File;
}

export interface UploadDocumentResponse {
  documentId: string;
}

export const uploadDocument = (data: FormData) =>
  api.post<UploadDocumentResponse>('/api/documents/upload', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

export interface GetUserDocumentsResponse {
  documents: Array<{
    id: string;
    name: string;
    uploadedAt: string;
  }>;
}

export const getUserDocuments = () => api.get<GetUserDocumentsResponse>('/api/documents');

export interface IngestDocumentsRequest {
  documentIds: string[];
}

export interface IngestDocumentsResponse {
  message: string;
}

export const ingestDocuments = (data: IngestDocumentsRequest) =>
  api.post<IngestDocumentsResponse>('/api/ai/ingest', data);

export interface AIQueryRequest {
  query: string;
  sessionId: string;
}

export interface AIQueryResponse {
  answer: string;
  citations: Array<{
    documentId: string;
    text: string;
  }>;
}

export const aiQuery = (data: AIQueryRequest) => api.post<AIQueryResponse>('/api/ai/query', data);

export interface GetChatSessionsResponse {
  sessions: Array<{
    id: string;
    name: string;
    createdAt: string;
  }>;
}

export const getChatSessions = () => api.get<GetChatSessionsResponse>('/api/chat/sessions');

export interface CreateChatSessionRequest {
  name: string;
}

export interface CreateChatSessionResponse {
  sessionId: string;
}

export const createChatSession = (data: CreateChatSessionRequest) =>
  api.post<CreateChatSessionResponse>('/api/chat/sessions', data);

export interface GetChatMessagesResponse {
  messages: Array<{
    id: string;
    sender: string;
    content: string;
    timestamp: string;
  }>;
}

export const getChatMessages = (sessionId: string) =>
  api.get<GetChatMessagesResponse>(`/api/chat/sessions/${sessionId}/messages`);