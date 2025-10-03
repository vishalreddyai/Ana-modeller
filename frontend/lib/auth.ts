import axios from 'axios';
import Cookies from 'js-cookie';

const API_BASE_URL = 'http://localhost:5000/api';

export interface User {
  user_id: string;
  email: string;
  created_at: string;
}

export interface LoginResponse {
  message: string;
  token: string;
  user_id: string;
}

export interface RegisterData {
  user_id: string;
  email: string;
  password: string;
}

export interface LoginData {
  user_id: string;
  password: string;
}

class AuthService {
  private getAuthHeaders() {
    const token = Cookies.get('token');
    return {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    };
  }

  async register(data: RegisterData): Promise<{ message: string }> {
    try {
      const response = await axios.post(`${API_BASE_URL}/register`, data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Registration failed');
    }
  }

  async login(data: LoginData): Promise<LoginResponse> {
    try {
      const response = await axios.post(`${API_BASE_URL}/login`, data);
      const { token } = response.data;
      
      // Store token in cookie
      Cookies.set('token', token, { expires: 1 }); // 1 day
      
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Login failed');
    }
  }

  async logout(): Promise<void> {
    Cookies.remove('token');
  }

  async verifyToken(): Promise<{ user_id: string }> {
    try {
      const token = Cookies.get('token');
      if (!token) {
        throw new Error('No token found');
      }

      const response = await axios.post(`${API_BASE_URL}/verify`, { token });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Token verification failed');
    }
  }

  async getProfile(): Promise<User> {
    try {
      const response = await axios.get(`${API_BASE_URL}/profile`, {
        headers: this.getAuthHeaders(),
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to get profile');
    }
  }

  async forgotPassword(email: string): Promise<{ message: string }> {
    try {
      const response = await axios.post(`${API_BASE_URL}/forgot-password`, { email });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Password reset request failed');
    }
  }

  isAuthenticated(): boolean {
    return !!Cookies.get('token');
  }
}

export const authService = new AuthService();