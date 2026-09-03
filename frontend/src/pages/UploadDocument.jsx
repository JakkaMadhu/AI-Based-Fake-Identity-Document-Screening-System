import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DocumentUploader from '../components/DocumentUploader';
import ScreeningProgress from '../components/ScreeningProgress';
import ResultCard from '../components/ResultCard';
import { uploadDocumentFile, uploadLiveCapture, screenDocument } from '../services/api';

export default function UploadDocument() {
  const [viewState, setViewState] = useState('upload'); // 'upload' | 'screening' | 'result'
  const [isUploading, setIsUploading] = useState(false);
  const [activeDocId, setActiveDocId] = useState(null);
  const [screeningResult, setScreeningResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const navigate = useNavigate();

  async function handleFileProceed(file) {
    setIsUploading(true);
    setErrorMessage(null);

    try {
      const uploadRes = await uploadDocumentFile(file);
      const docId = uploadRes.document_id;
      setActiveDocId(docId);
      setIsUploading(false);

      setViewState('screening');

      const result = await screenDocument(docId);
      
      setTimeout(() => {
        setScreeningResult(result);
        setViewState('result');
      }, 1400);
    } catch (err) {
      console.error('Upload / Screening failed:', err);
      setErrorMessage(err.message || 'An error occurred during screening.');
      setIsUploading(false);
      setViewState('upload');
    }
  }

  async function handleDualCaptureProceed(documentBase64, faceBase64, filename) {
    setIsUploading(true);
    setErrorMessage(null);

    try {
      const uploadRes = await uploadLiveCapture(documentBase64, faceBase64, filename);
      const docId = uploadRes.document_id;
      setActiveDocId(docId);
      setIsUploading(false);

      setViewState('screening');

      const result = await screenDocument(docId);

      setTimeout(() => {
        setScreeningResult(result);
        setViewState('result');
      }, 1400);
    } catch (err) {
      console.error('2-step live KYC screening failed:', err);
      setErrorMessage(err.message || 'An error occurred during screening.');
      setIsUploading(false);
      setViewState('upload');
    }
  }

  function handleReset() {
    setActiveDocId(null);
    setScreeningResult(null);
    setErrorMessage(null);
    setViewState('upload');
  }

  return (
    <div className="page-container">
      <div className="page-header" style={{ textAlign: 'center', maxWidth: '780px', margin: '0 auto 2rem' }}>
        <h1 className="page-title">Border Checkpoint Document & Biometric Screening</h1>
        <p className="page-desc">
          Capture travel credentials, perform live biometric cross-matching, and execute multi-spectral forgery detection
        </p>
      </div>

      {errorMessage && (
        <div style={{
          maxWidth: '780px',
          margin: '0 auto 1.5rem',
          padding: '0.85rem 1.25rem',
          backgroundColor: 'var(--status-suspicious-bg)',
          border: '1px solid var(--status-suspicious-border)',
          borderRadius: 'var(--radius-sm)',
          color: 'var(--status-suspicious-text)',
          fontSize: '0.88rem',
          fontWeight: 600
        }}>
          SCREENING EXCEPTION: {errorMessage}
        </div>
      )}

      {viewState === 'upload' && (
        <DocumentUploader
          onProceedWithFile={handleFileProceed}
          onProceedWithDualCapture={handleDualCaptureProceed}
          isUploading={isUploading}
        />
      )}

      {viewState === 'screening' && (
        <ScreeningProgress />
      )}

      {viewState === 'result' && (
        <ResultCard
          result={screeningResult}
          onScreenAnother={handleReset}
        />
      )}
    </div>
  );
}
