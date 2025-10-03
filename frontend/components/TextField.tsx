import { InputHTMLAttributes } from 'react';
import styles from '../styles/FormControls.module.css';

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export function TextField({ label, error, id, ...props }: TextFieldProps) {
  const inputId = id ?? props.name;

  return (
    <label className={styles.field} htmlFor={inputId}>
      <span className={styles.label}>{label}</span>
      <input id={inputId} className={styles.input} {...props} />
      {error ? <span className={styles.error}>{error}</span> : null}
    </label>
  );
}
