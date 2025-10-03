import { ReactNode } from 'react';
import styles from '../styles/AuthLayout.module.css';

interface AuthLayoutProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
}

export function AuthLayout({ title, subtitle, children }: AuthLayoutProps) {
  return (
    <div className={styles.wrapper}>
      <div className={styles.card}>
        <div className={styles.branding}>
          <h1 className={styles.logo}>Ana Modeller</h1>
          <p className={styles.tagline}>
            Advanced analytics modelling platform delivering actionable insights.
          </p>
        </div>
        <div className={styles.formPanel}>
          <header className={styles.header}>
            <h2>{title}</h2>
            {subtitle && <p>{subtitle}</p>}
          </header>
          <div>{children}</div>
        </div>
      </div>
    </div>
  );
}
