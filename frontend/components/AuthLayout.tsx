import { ReactNode } from 'react';
import styles from '../styles/AuthLayout.module.css';

interface AuthLayoutProps {
  children: ReactNode;
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className={styles.authContainer}>
      <div className={styles.leftPanel}>
        <div className={styles.logo}>Ana Designer</div>
        <h1 className={styles.heading}>Design Anaplan faster.</h1>
        <ul className={styles.featureList}>
          <li className={styles.featureItem}>
            <span className={styles.featureIcon}>✓</span>
            Upload stories efficiently and accurately with powerful parsing capabilities.
          </li>
          <li className={styles.featureItem}>
            <span className={styles.featureIcon}>✓</span>
            Auto-categorize data using advanced DISCO & Persona recognition.
          </li>
          <li className={styles.featureItem}>
            <span className={styles.featureIcon}>✓</span>
            Generate design & structure for your Anaplan models instantly.
          </li>
        </ul>
      </div>
      <div className={styles.rightPanel}>
        <div className={styles.formContainer}>
          {children}
        </div>
      </div>
    </div>
  );
}
