import { useState, useRef } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { uploadAndProcessUserStories, ProcessingResult } from '../lib/api';
import styles from '../styles/Upload.module.css';

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [uploadInfo, setUploadInfo] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (selectedFile: File) => {
    const allowedTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/pdf',
      'text/csv'
    ];

    if (!allowedTypes.includes(selectedFile.type)) {
      setError('Invalid file type. Please upload CSV, Excel, Word, or PDF files only.');
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) { // 10MB limit
      setError('File size must be less than 10MB');
      return;
    }

    setFile(selectedFile);
    setError('');
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleUploadAndProcess = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const result = await uploadAndProcessUserStories(file);
      
      // Store result in sessionStorage and navigate to categorization page
      sessionStorage.setItem('processingResult', JSON.stringify(result));
      router.push('/categorize');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Upload failed. Please try again.';
      setError(message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.logo}>
          <span className={styles.logoIcon}>Ana</span> Ana Designer
        </div>
        <div className={styles.steps}>
          <div className={`${styles.step} ${styles.active}`}>
            <div className={styles.stepNumber}>1</div>
            <span>Upload</span>
          </div>
          <div className={styles.step}>
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
        <Link href="/home" className={styles.backButton}>
          ← Back to Home
        </Link>
      </div>

      {/* Main Content */}
      <div className={styles.main}>
        <div className={styles.content}>
          <h1 className={styles.title}>Add User Stories</h1>
          <p className={styles.subtitle}>Supports ~200-300 stories</p>

          {/* Upload Area */}
          <div
            className={`${styles.uploadArea} ${dragActive ? styles.dragActive : ''} ${file ? styles.hasFile : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx,.xls,.docx,.pdf,.csv"
              onChange={handleFileInputChange}
              style={{ display: 'none' }}
            />
            
            <div className={styles.uploadIcon}>↑</div>
            
            {file ? (
              <div className={styles.fileInfo}>
                <div className={styles.fileName}>{file.name}</div>
                <div className={styles.fileSize}>
                  {(file.size / 1024).toFixed(2)} KB
                </div>
              </div>
            ) : (
              <>
                <div className={styles.uploadText}>Drag & drop files here</div>
                <div className={styles.uploadSubtext}>CSV, Word, Excel or PDF</div>
              </>
            )}
            
            <button className={styles.chooseButton} onClick={(e) => {
              e.stopPropagation();
              fileInputRef.current?.click();
            }}>
              📎 Choose File
            </button>
            
            <a href="#" className={styles.downloadSample}>Download sample</a>
          </div>

          <div className={styles.validation}>
            <small>Validation: Max 10MB • Required: Story No, Description</small>
          </div>

          {error && (
            <div className={styles.error}>{error}</div>
          )}

          {/* Action Buttons */}
          <div className={styles.actions}>
            <button
              className={styles.uploadButton}
              onClick={handleUploadAndProcess}
              disabled={!file || uploading}
            >
              {uploading ? 'Processing...' : 'Upload & Proceed'}
            </button>
          </div>
        </div>

        {/* Preview Panel */}
        {file && (
          <div className={styles.preview}>
            <h3>Upload Preview</h3>
            <div className={styles.previewStats}>
              <div className={styles.stat}>
                <div className={styles.statLabel}>Selected File</div>
                <div className={styles.statValue}>{file.name}</div>
              </div>
            </div>
            <p className={styles.previewNote}>
              Full details available in Categorize step
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
