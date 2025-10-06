import Link from 'next/link';
import { FormEvent, useState } from 'react';
import { useRouter } from 'next/router';

import { AuthLayout } from '../components/AuthLayout';
import { TextField } from '../components/TextField';
import formStyles from '../styles/FormControls.module.css';
import { signup } from '../lib/api';

interface SignupState {
  fullName: string;
  email: string;
  password: string;
  confirmPassword: string;
  loading: boolean;
  error: string | null;
  success: string | null;
}

export default function SignupPage() {
  const router = useRouter();
  const [state, setState] = useState<SignupState>({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    loading: false,
    error: null,
    success: null
  });

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (state.password !== state.confirmPassword) {
      setState((prev) => ({
        ...prev,
        error: 'Passwords do not match.',
        success: null
      }));
      return;
    }

    setState((prev) => ({ ...prev, loading: true, error: null, success: null }));

    // Basic client-side email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(state.email)) {
      setState((prev) => ({
        ...prev,
        error: 'Please enter a valid email address.',
        success: null,
        loading: false
      }));
      return;
    }

    try {
      await signup(state.email, state.fullName, state.password);
      setState((prev) => ({
        ...prev,
        loading: false,
        success: 'Account created successfully. Redirecting to sign in…'
      }));
      setTimeout(() => {
        router.push('/');
      }, 1500);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unable to create account.';
      setState((prev) => ({ ...prev, loading: false, error: message }));
    }
  };

  return (
    <AuthLayout>
      <h2 style={{ marginBottom: '24px', fontSize: '24px', color: 'var(--primary-text)' }}>Create your account</h2>
      <p style={{ marginBottom: '24px', fontSize: '16px', color: 'var(--secondary-text)' }}>Get started with Ana Modeller in minutes.</p>
      <form onSubmit={handleSubmit} className={formStyles.form}>
        <div className={formStyles.stack}>
          <TextField
            name="fullName"
            type="text"
            label="Full name"
            placeholder="Jane Doe"
            required
            value={state.fullName}
            onChange={(event) =>
              setState((prev) => ({ ...prev, fullName: event.target.value }))
            }
          />
          <TextField
            name="email"
            type="email"
            label="Email address"
            placeholder="you@example.com"
            required
            value={state.email}
            onChange={(event) => setState((prev) => ({ ...prev, email: event.target.value }))}
          />
          <TextField
            name="password"
            type="password"
            label="Password"
            placeholder="Create a strong password"
            required
            value={state.password}
            onChange={(event) =>
              setState((prev) => ({ ...prev, password: event.target.value }))
            }
          />
          <TextField
            name="confirmPassword"
            type="password"
            label="Confirm password"
            placeholder="Repeat your password"
            required
            value={state.confirmPassword}
            onChange={(event) =>
              setState((prev) => ({ ...prev, confirmPassword: event.target.value }))
            }
          />
        </div>
        <button className={formStyles.button} type="submit" disabled={state.loading}>
          {state.loading ? 'Creating your account…' : 'Create account'}
        </button>
        <div className={formStyles.linkText}>
          <span>
            Already have an account? <Link href="/">Sign in</Link>
          </span>
        </div>
        {state.error ? <div className={formStyles.warning}>{state.error}</div> : null}
        {state.success ? <div className={formStyles.notice}>{state.success}</div> : null}
      </form>
    </AuthLayout>
  );
}
