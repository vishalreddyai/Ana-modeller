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
  return handleResponse(
    fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    })
  );
}

export async function signup(fullName: string, email: string, password: string) {
  return handleResponse(
    fetch(`${API_BASE_URL}/api/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ full_name: fullName, email, password })
    })
  );
}

export async function forgotPassword(email: string) {
  return handleResponse(
    fetch(`${API_BASE_URL}/api/auth/forgot-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email })
    })
  );
}
