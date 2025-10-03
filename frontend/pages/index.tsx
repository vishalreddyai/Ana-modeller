import Link from 'next/link';
import { FormEvent, useState } from 'react';
import { useRouter } from 'next/router';

import { AuthLayout } from '../components/AuthLayout';
import { TextField } from '../components/TextField';
import formStyles from '../styles/FormControls.module.css';
import { login } from '../lib/api';

type LoginState = {
  email: string;
  password: string;
  loading: boolean;
  error: string | null;
};

export default function LoginPage() {
  const router = useRouter();
  const [state, setState] = useState<LoginState>({
    email: '',
    password: '',
    loading: false,
    error: null
  });

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      await login(state.email, state.password);
      await router.push('/home');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unable to sign in.';
      setState((prev) => ({ ...prev, loading: false, error: message }));
      return;
    }
  };

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to access your personalised analytics workspace."
    >
      <form onSubmit={handleSubmit} className={formStyles.form}>
        <div className={formStyles.stack}>
          <TextField
            name="email"
            type="email"
            label="Email address"
            placeholder="you@example.com"
            required
            value={state.email}
            onChange={(event) =>
              setState((prev) => ({ ...prev, email: event.target.value }))
            }
          />
          <TextField
            name="password"
            type="password"
            label="Password"
            placeholder="Enter your password"
            required
            value={state.password}
            onChange={(event) =>
              setState((prev) => ({ ...prev, password: event.target.value }))
            }
          />
        </div>
        <button className={formStyles.button} type="submit" disabled={state.loading}>
          {state.loading ? 'Signing you in…' : 'Sign in'}
        </button>
        <div className={formStyles.linkRow}>
          <Link href="/signup">Create account</Link>
          <Link href="/forgot-password">Forgot password?</Link>
        </div>
        {state.error ? <div className={formStyles.warning}>{state.error}</div> : null}
      </form>
    </AuthLayout>
  );
}
