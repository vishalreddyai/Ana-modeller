import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { authService } from '../lib/auth';

export default function ForgotPassword() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Redirect if already authenticated
    if (authService.isAuthenticated()) {
      router.push('/');
    }
  }, [router]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    if (error) {
      setError('');
    }
  };

  const validateEmail = (): boolean => {
    if (!email.trim()) {
      setError('Email is required');
      return false;
    }
    
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError('Please enter a valid email address');
      return false;
    }
    
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateEmail()) {
      return;
    }

    setIsLoading(true);
    setMessage('');

    try {
      await authService.forgotPassword(email);
      setMessage('Password reset instructions have been sent to your email address.');
    } catch (error: any) {
      setMessage(error.message || 'Failed to send password reset instructions.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1 className="auth-title">Forgot Password</h1>
        <p className="auth-subtitle">Enter your email to reset your password</p>

        {message && (
          <div className={`message ${message.includes('sent') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={email}
              onChange={handleInputChange}
              className={`form-input ${error ? 'error' : ''}`}
              placeholder="Enter your email address"
              disabled={isLoading}
            />
            {error && (
              <div className="error-message">{error}</div>
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
                Sending Instructions...
              </>
            ) : (
              'Send Reset Instructions'
            )}
          </button>
        </form>

        <div className="auth-links">
          <Link href="/login" className="auth-link">
            Remember your password? Sign in
          </Link>
          <br />
          <Link href="/signup" className="auth-link">
            Don't have an account? Sign up
          </Link>
        </div>
      </div>
    </div>
  );
}