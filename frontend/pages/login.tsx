import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { authService, LoginData } from '../lib/auth';

export default function Login() {
  const router = useRouter();
  const [formData, setFormData] = useState<LoginData>({
    user_id: '',
    password: '',
  });
  const [errors, setErrors] = useState<Partial<LoginData>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Redirect if already authenticated
    if (authService.isAuthenticated()) {
      router.push('/');
    }
  }, [router]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    
    // Clear error when user starts typing
    if (errors[name as keyof LoginData]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<LoginData> = {};

    if (!formData.user_id.trim()) {
      newErrors.user_id = 'User ID is required';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setMessage('');

    try {
      await authService.login(formData);
      setMessage('Login successful! Redirecting...');
      
      // Redirect to homepage after successful login
      setTimeout(() => {
        router.push('/');
      }, 1000);
    } catch (error: any) {
      setMessage(error.message || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1 className="auth-title">Welcome Back</h1>
        <p className="auth-subtitle">Sign in to your account</p>

        {message && (
          <div className={`message ${message.includes('successful') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="user_id" className="form-label">
              User ID or Email
            </label>
            <input
              type="text"
              id="user_id"
              name="user_id"
              value={formData.user_id}
              onChange={handleInputChange}
              className={`form-input ${errors.user_id ? 'error' : ''}`}
              placeholder="Enter your user ID or email"
              disabled={isLoading}
            />
            {errors.user_id && (
              <div className="error-message">{errors.user_id}</div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              className={`form-input ${errors.password ? 'error' : ''}`}
              placeholder="Enter your password"
              disabled={isLoading}
            />
            {errors.password && (
              <div className="error-message">{errors.password}</div>
            )}
          </div>

          <button
            type="submit"
            className="auth-button"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="loading-spinner"></span>
                Signing In...
              </>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <div className="auth-links">
          <Link href="/signup" className="auth-link">
            Don't have an account? Sign up
          </Link>
          <br />
          <Link href="/forgot-password" className="auth-link">
            Forgot your password?
          </Link>
        </div>
      </div>
    </div>
  );
}