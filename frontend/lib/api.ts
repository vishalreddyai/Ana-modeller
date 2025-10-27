// lib/api.ts
export interface User {
  id: string;
  email: string;
  username: string;
  token?: string;
  refresh_token?: string;
}

export interface ApiError {
  message: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const { method = 'GET', body, headers = {} } = options;

  const config: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
  };

  if (body) {
    config.body = body;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred' }));
    const message = typeof errorData.detail === 'string' ? errorData.detail : 'Request failed';
    throw new Error(message);
  }

  return response.json();
}

export function login(email: string, password: string): Promise<User> {
  return apiClient<User>('/api/auth/signin', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export function signup(email: string, username: string, password: string): Promise<User> {
  return apiClient<User>('/api/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ email, username, password }),
  });
}

export function forgotPassword(email: string): Promise<{ message: string }> {
  return apiClient<{ message: string }>('/api/auth/forgot-password', {
    method: 'POST',
    body: JSON.stringify({ email }),
  });
}

// User Stories API
export interface UploadResponse {
  message: string;
  filename: string;
  total_stories: number;
  valid_stories: number;
  duplicates: number;
  errors: number;
  preview: Array<{ ust: string; description: string }>;
}

export interface DISCOCategory {
  story_no: string;
  category: string;
  description: string;
}

export interface PersonaCategory {
  story_no: string;
  persona: string;
  description: string;
}

export interface ProcessingResult {
  total_stories: number;
  processed_stories: number;
  disco_categories: DISCOCategory[];
  persona_categories: PersonaCategory[];
  errors: string[];
}

export async function uploadUserStories(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/stories/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }));
    const message = typeof errorData.detail === 'string' ? errorData.detail : 'Upload failed';
    throw new Error(message);
  }

  return response.json();
}

export async function processUserStories(filename: string): Promise<ProcessingResult> {
  return apiClient<ProcessingResult>(`/api/stories/process?filename=${encodeURIComponent(filename)}`, {
    method: 'POST',
  });
}

export async function uploadAndProcessUserStories(file: File): Promise<ProcessingResult> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/stories/upload-and-process`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Processing failed' }));
    const message = typeof errorData.detail === 'string' ? errorData.detail : 'Processing failed';
    throw new Error(message);
  }

  return response.json();
}
