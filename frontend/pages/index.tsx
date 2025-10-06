import { useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { AuthLayout } from '../components/AuthLayout';
import { TextField } from '../components/TextField';
import { login } from '../lib/api';
import styles from '../styles/FormControls.module.css';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await login(email, password);
      localStorage.setItem('user', JSON.stringify(data));
      router.push('/home');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <h2 style={{ marginBottom: '24px', fontSize: '24px', color: 'var(--primary-text)' }}>Login</h2>
      <form onSubmit={handleSubmit} style={{ width: '100%', maxWidth: '400px' }}>
        <TextField
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="name@company.com"
          required
        />
        <div className={styles.passwordField}>
          <TextField
            label="Password"
            type={showPassword ? "text" : "password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button
            type="button"
            className={styles.passwordToggle}
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? "Hide" : "Show"}
          </button>
        </div>
        
        <div className={styles.forgotPassword}>
          <Link href="/forgot-password">
            Forgot password?
          </Link>
        </div>

        <div className={styles.checkbox}>
          <input
            type="checkbox"
            id="remember"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
          />
          <label htmlFor="remember">Remember me</label>
        </div>

        {error && (
          <div style={{ color: 'var(--error-red)', marginBottom: '16px', fontSize: '14px' }}>
            {error}
          </div>
        )}

        <button type="submit" className={styles.button} disabled={loading}>
          {loading ? 'Signing in...' : 'Login'}
        </button>

        <div className={styles.linkText}>
          Not a member? <Link href="/signup">Sign up here</Link>
        </div>
      </form>
    </AuthLayout>
  );
}
