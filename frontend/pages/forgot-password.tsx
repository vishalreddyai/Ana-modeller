import Link from 'next/link';
import { FormEvent, useState } from 'react';

import { AuthLayout } from '../components/AuthLayout';
import { TextField } from '../components/TextField';
import formStyles from '../styles/FormControls.module.css';
import { forgotPassword } from '../lib/api';

interface ForgotPasswordState {
  email: string;
  loading: boolean;
  error: string | null;
  success: string | null;
}

export default function ForgotPasswordPage() {
  const [state, setState] = useState<ForgotPasswordState>({
    email: '',
    loading: false,
    error: null,
    success: null
  });

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setState((prev) => ({ ...prev, loading: true, error: null, success: null }));

    try {
      const response = await forgotPassword(state.email);
      setState((prev) => ({
        ...prev,
        loading: false,
        success: response.message
      }));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unable to process request.';
      setState((prev) => ({ ...prev, loading: false, error: message }));
    }
  };

  return (
    <AuthLayout
      title="Reset your password"
      subtitle="Enter your account email to receive password reset instructions."
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
            onChange={(event) => setState((prev) => ({ ...prev, email: event.target.value }))}
          />
        </div>
        <button className={formStyles.button} type="submit" disabled={state.loading}>
          {state.loading ? 'Sending instructions…' : 'Send reset link'}
        </button>
        <div className={formStyles.linkRow}>
          <Link href="/">Back to sign in</Link>
          <Link href="/signup">Create account</Link>
        </div>
        {state.error ? <div className={formStyles.warning}>{state.error}</div> : null}
        {state.success ? <div className={formStyles.notice}>{state.success}</div> : null}
      </form>
    </AuthLayout>
  );
}
