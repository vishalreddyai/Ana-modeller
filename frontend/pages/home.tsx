import Link from 'next/link';

import styles from '../styles/HomePage.module.css';

export default function HomePage() {
  return (
    <div className={styles.wrapper}>
      <header className={styles.navbar}>
        <div className={styles.brand}>Ana Modeller</div>
        <nav>
          <Link href="/">Sign out</Link>
        </nav>
      </header>
      <main className={styles.content}>
        <section className={styles.hero}>
          <h1>Welcome to your analytics hub</h1>
          <p>
            You are now signed in. This dashboard is ready for integration with your data
            visualisations, predictive models, and collaborative workflows.
          </p>
          <div className={styles.actions}>
            <button type="button">Create new model</button>
            <button type="button" className={styles.secondary}>
              View reports
            </button>
          </div>
        </section>
        <section className={styles.tiles}>
          <article>
            <h2>Pipeline status</h2>
            <p>All data ingestion pipelines are running smoothly.</p>
          </article>
          <article>
            <h2>Recent activity</h2>
            <p>Track who viewed, edited, and deployed your models in real-time.</p>
          </article>
          <article>
            <h2>Next actions</h2>
            <p>Assign tasks, manage approvals, and keep delivery on track.</p>
          </article>
        </section>
      </main>
    </div>
  );
}
