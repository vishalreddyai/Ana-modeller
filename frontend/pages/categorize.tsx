import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { ProcessingResult, DISCOCategory, PersonaCategory } from '../lib/api';
import styles from '../styles/Categorize.module.css';

export default function CategorizePage() {
  const router = useRouter();
  const [result, setResult] = useState<ProcessingResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [autoCategorizing, setAutoCategorizing] = useState(false);

  useEffect(() => {
    // Get processing result from sessionStorage
    const resultStr = sessionStorage.getItem('processingResult');
    
    if (!resultStr) {
      router.push('/upload');
      return;
    }

    try {
      const parsedResult = JSON.parse(resultStr);
      setResult(parsedResult);
      setLoading(false);
    } catch (err) {
      setError('Error loading results');
      setLoading(false);
    }
  }, [router]);

  const handleExportToExcel = (type: 'disco' | 'persona') => {
    if (!result) return;
    
    const data = type === 'disco' ? result.disco_categories : result.persona_categories;
    
    // Create CSV content
    const headers = type === 'disco' 
      ? ['Story No', 'Category (DISCO)', 'Description']
      : ['UST', 'Persona', 'Description'];
    
    const csvContent = [
      headers.join(','),
      ...data.map(row => {
        const values = type === 'disco'
          ? [(row as DISCOCategory).story_no, (row as DISCOCategory).category, `"${(row as DISCOCategory).description}"`]
          : [(row as PersonaCategory).story_no, (row as PersonaCategory).persona, `"${(row as PersonaCategory).description}"`];
        return values.join(',');
      })
    ].join('\n');
    
    // Download
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${type}_categories.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const handleNext = () => {
    // Navigate to next step (Design)
    alert('Design step coming soon!');
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading results...</div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>{error || 'No results found'}</div>
        <Link href="/upload">← Back to Upload</Link>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.logo}>
          <span className={styles.logoIcon}>Ana</span> Ana Designer
        </div>
        <div className={styles.breadcrumb}>
          Ana Designer → Categorize → Design → Structure
        </div>
        <div className={styles.steps}>
          <div className={styles.step}>
            <div className={styles.stepNumber}>1</div>
            <span>Upload</span>
          </div>
          <div className={`${styles.step} ${styles.active}`}>
            <div className={styles.stepNumber}>2</div>
            <span>Categorize</span>
          </div>
          <div className={styles.step}>
            <div className={styles.stepNumber}>3</div>
            <span>Design</span>
          </div>
          <div className={styles.step}>
            <div className={styles.stepNumber}>4</div>
            <span>Structure</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className={styles.main}>
        <div className={styles.titleBar}>
          <h1 className={styles.title}>Categorization</h1>
          <button 
            className={styles.autoCategorize}
            onClick={() => setAutoCategorizing(true)}
            disabled={autoCategorizing}
          >
            🤖 Auto-categorize
          </button>
        </div>

        {/* Error Messages */}
        {result.errors && result.errors.length > 0 && (
          <div className={styles.errorBanner}>
            <strong>Warnings:</strong>
            <ul>
              {result.errors.map((err, idx) => (
                <li key={idx}>{err}</li>
              ))}
            </ul>
          </div>
        )}

        {/* DISCO Category Table */}
        <div className={styles.tableSection}>
          <div className={styles.tableHeader}>
            <h2 className={styles.tableTitle}>DISCO Category</h2>
            <div className={styles.tableActions}>
              <button 
                className={styles.editButton}
                onClick={() => alert('Edit functionality coming soon!')}
              >
                Edit
              </button>
              <button 
                className={styles.exportButton}
                onClick={() => handleExportToExcel('disco')}
              >
                📥 Export to Excel
              </button>
            </div>
          </div>
          
          <div className={styles.tableContainer}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Story No</th>
                  <th>Category (DISCO)</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {result.disco_categories.map((item, idx) => (
                  <tr key={idx}>
                    <td>{item.story_no}</td>
                    <td>
                      <span className={`${styles.badge} ${styles[item.category.toLowerCase()]}`}>
                        {item.category}
                      </span>
                    </td>
                    <td>{item.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Persona Table */}
        <div className={styles.tableSection}>
          <div className={styles.tableHeader}>
            <h2 className={styles.tableTitle}>Persona</h2>
            <div className={styles.tableActions}>
              <button 
                className={styles.editButton}
                onClick={() => alert('Edit functionality coming soon!')}
              >
                Edit
              </button>
              <button 
                className={styles.exportButton}
                onClick={() => handleExportToExcel('persona')}
              >
                📥 Export to Excel
              </button>
            </div>
          </div>
          
          <div className={styles.tableContainer}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>UST</th>
                  <th>Persona</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {result.persona_categories.map((item, idx) => (
                  <tr key={idx}>
                    <td>{item.story_no}</td>
                    <td>
                      <span className={styles.personaBadge}>
                        {item.persona}
                      </span>
                    </td>
                    <td>{item.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Action Buttons */}
        <div className={styles.actions}>
          <Link href="/upload" className={styles.backButton}>
            ← Back
          </Link>
          <button className={styles.nextButton} onClick={handleNext}>
            Next →
          </button>
        </div>
      </div>
    </div>
  );
}
