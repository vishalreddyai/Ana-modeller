import { InputHTMLAttributes } from 'react';
import styles from '../styles/FormControls.module.css';

interface TextFieldProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'className'> {
  label: string;
  error?: string;
}

export function TextField({ label, error, id, ...props }: TextFieldProps) {
  const inputId = id ?? props.name;

  return (
    <div className={styles.formControl}>
      <label htmlFor={inputId} className={styles.label}>
        {label}
      </label>
      <input id={inputId} className={styles.input} {...props} />
      {error && <div className={styles.error}>{error}</div>}
    </div>
  );
}
