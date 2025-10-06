export interface ApiError {
  message: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const data = await response.json().catch(() => ({ detail: 'Request failed' }));
    const message = typeof data.detail === 'string' ? data.detail : 'Request failed';
    throw new Error(message);
  }
  return response.json();
}

export async function login(email: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/api/auth/signin`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password })
  });
  return handleResponse(response);
}

export async function signup(email: string, username: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, username, password })
  });
  return handleResponse(response);
}

export async function forgotPassword(email: string) {
  const response = await fetch(`${API_BASE_URL}/api/auth/forgot-password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email })
  });
  return handleResponse(response);
}
