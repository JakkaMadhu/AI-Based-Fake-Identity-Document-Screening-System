import React, { useState, useRef } from 'react';
import LiveCameraScanner from './LiveCameraScanner';

export default function DocumentUploader({ onProceedWithFile, onProceedWithDualCapture, isUploading }) {
  const [activeMode, setActiveMode] = useState('camera'); // 'camera' | 'file'
  const [currentStep, setCurrentStep] = useState('doc_capture'); // 'doc_capture' | 'face_capture' | 'review'

  const [docImage, setDocImage] = useState(null);
  const [faceImage, setFaceImage] = useState(null);
  
  const [dragActive, setDragActive] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const fileInputRef = useRef(null);

  const MAX_FILE_SIZE = 15 * 1024 * 1024; // 15MB
  const ALLOWED_TYPES = [
    'image/jpeg', 'image/png', 'image/jpg',
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ];

  function validateFile(file) {
    if (!file) return 'No document file selected.';
    const ext = file.name.split('.').pop().toLowerCase();
    const allowedExts = ['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx'];
    if (!ALLOWED_TYPES.includes(file.type.toLowerCase()) && !allowedExts.includes(ext)) {
      return `Invalid format '${file.type || ext}'. Permitted types: JPG, PNG, PDF, DOC, DOCX.`;
    }
    if (file.size > MAX_FILE_SIZE) {
      return `File size (${(file.size / (1024 * 1024)).toFixed(1)} MB) exceeds institutional maximum of 10 MB.`;
    }
    return null;
  }

  function handleFileSelected(file) {
    setErrorMessage(null);
    const err = validateFile(file);
    if (err) {
      setErrorMessage(err);
      return;
    }
    const objectUrl = URL.createObjectURL(file);
    const fileExt = file.name.split('.').pop().toLowerCase();
    const isNonImage = ['pdf', 'doc', 'docx'].includes(fileExt);
    setDocImage({
      url: isNonImage ? null : objectUrl,
      file: file,
      base64: null,
      filename: file.name,
      isDocument: isNonImage,
      fileExt: fileExt
    });
    setCurrentStep('face_capture');
  }

  function handleDocCameraCaptured(base64Image) {
    setErrorMessage(null);
    setDocImage({
      url: base64Image,
      base64: base64Image,
      file: null,
      filename: `doc_scan_${Date.now().toString().slice(-6)}.jpg`
    });
    setCurrentStep('face_capture');
  }

  function handleFaceCameraCaptured(base64Image) {
    setErrorMessage(null);
    setFaceImage({
      url: base64Image,
      base64: base64Image
    });
    setCurrentStep('review');
  }

  function handleSkipFace() {
    setFaceImage(null);
    setCurrentStep('review');
  }

  function handleRetakeDoc() {
    setDocImage(null);
    setCurrentStep('doc_capture');
  }

  function handleRetakeFace() {
    setFaceImage(null);
    setCurrentStep('face_capture');
  }

  function handleFinalSubmit() {
    if (!docImage) return;

    if (docImage.base64) {
      onProceedWithDualCapture(
        docImage.base64,
        faceImage ? faceImage.base64 : null,
        docImage.filename
      );
    } else if (docImage.file) {
      if (faceImage && faceImage.base64) {
        const reader = new FileReader();
        reader.onload = () => {
          onProceedWithDualCapture(
            reader.result,
            faceImage.base64,
            docImage.filename
          );
        };
        reader.readAsDataURL(docImage.file);
      } else {
        onProceedWithFile(docImage.file);
      }
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  }

  return (
    <div style={{ maxWidth: '820px', margin: '0 auto' }}>
      {/* Step Wizard Header */}
      <div className="step-wizard-header">
        <div className={`wizard-step-badge ${currentStep === 'doc_capture' ? 'active' : ''} ${docImage ? 'completed' : ''}`}>
          <span className="wizard-step-num">{docImage ? 'DONE' : '1'}</span>
          <span>STEP 1: DOCUMENT ACQUISITION</span>
        </div>

        <span className="wizard-step-separator">&bull;&bull;&bull;</span>

        <div className={`wizard-step-badge ${currentStep === 'face_capture' ? 'active' : ''} ${faceImage ? 'completed' : ''}`}>
          <span className="wizard-step-num">{faceImage ? 'DONE' : '2'}</span>
          <span>STEP 2: BIOMETRIC PORTRAIT</span>
        </div>

        <span className="wizard-step-separator">&bull;&bull;&bull;</span>

        <div className={`wizard-step-badge ${currentStep === 'review' ? 'active' : ''}`}>
          <span className="wizard-step-num">3</span>
          <span>STEP 3: SCREENING REVIEW</span>
        </div>
      </div>

      {errorMessage && (
        <div style={{
          padding: '0.75rem 1rem',
          backgroundColor: 'var(--status-suspicious-bg)',
          border: '1px solid var(--status-suspicious-border)',
          borderRadius: 'var(--radius-sm)',
          color: 'var(--status-suspicious-text)',
          fontSize: '0.85rem',
          fontWeight: 600,
          marginBottom: '1.25rem'
        }}>
          INPUT ERROR: {errorMessage}
        </div>
      )}

      {/* STEP 1: DOCUMENT CAPTURE */}
      {currentStep === 'doc_capture' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <div className="upload-mode-toggle">
              <button
                type="button"
                className={`upload-mode-btn ${activeMode === 'camera' ? 'active' : ''}`}
                onClick={() => { setActiveMode('camera'); setErrorMessage(null); }}
              >
                LIVE OPTICAL FEED
              </button>
              <button
                type="button"
                className={`upload-mode-btn ${activeMode === 'file' ? 'active' : ''}`}
                onClick={() => { setActiveMode('file'); setErrorMessage(null); }}
              >
                LOCAL FILE SELECTION
              </button>
            </div>
          </div>

          {activeMode === 'camera' && (
            <LiveCameraScanner
              mode="document"
              promptText="Align Document Border Inside Frame"
              onCapture={handleDocCameraCaptured}
              onCancel={() => setActiveMode('file')}
            />
          )}

          {activeMode === 'file' && (
            <div
              className={`dropzone ${dragActive ? 'active' : ''}`}
              onDragEnter={() => setDragActive(true)}
              onDragLeave={() => setDragActive(false)}
              onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current && fileInputRef.current.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".jpg,.jpeg,.png,.pdf,.doc,.docx,image/jpeg,image/png,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                style={{ display: 'none' }}
                onChange={(e) => e.target.files && e.target.files[0] && handleFileSelected(e.target.files[0])}
              />
              <div className="dropzone-title">
                Click to Browse or Drag Document File
              </div>
              <div className="dropzone-desc">
                Supported: Passport, Visa, National ID (JPG, PNG, PDF, DOC, DOCX — max 15MB)
              </div>
            </div>
          )}
        </div>
      )}

      {/* STEP 2: BIOMETRIC LIVE FACE CAPTURE */}
      {currentStep === 'face_capture' && (
        <div style={{ textAlign: 'center' }}>
          <div style={{ marginBottom: '1.25rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Step 2: Live Facial Biometrics</h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Position traveler face inside the oval guide for cross-matching against document portrait
            </p>
          </div>

          <LiveCameraScanner
            mode="face"
            promptText="Center Facial Landmarks in Oval Guide"
            onCapture={handleFaceCameraCaptured}
            onCancel={handleSkipFace}
          />

          <div style={{ marginTop: '1.25rem' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleSkipFace}
            >
              Skip Biometric Capture (Document Inspection Only)
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: DUAL REVIEW & SUBMISSION */}
      {currentStep === 'review' && (
        <div className="card">
          <div style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Inspection Pre-Screening Review</h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Confirm image alignment before executing automated forensic verification pipeline
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
            {/* Cropped Document Preview */}
            <div style={{ textAlign: 'center', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', padding: '1rem' }}>
              <div style={{ fontSize: '0.78rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                Primary Document Frame
              </div>
              {docImage && (
                docImage.isDocument ? (
                  <div style={{
                    height: '220px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: 'var(--bg-surface-alt)',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-strong)',
                    gap: '0.5rem'
                  }}>
                    <span style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-secondary)' }}>
                      {docImage.fileExt.toUpperCase()}
                    </span>
                    <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', wordBreak: 'break-all', padding: '0 1rem', textAlign: 'center' }}>
                      {docImage.filename}
                    </span>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      Will be converted to image for screening
                    </span>
                  </div>
                ) : (
                  <img
                    src={docImage.url}
                    alt="Document Frame"
                    style={{
                      width: '100%',
                      maxHeight: '220px',
                      objectFit: 'contain',
                      border: '1px solid var(--border-strong)',
                      borderRadius: 'var(--radius-sm)',
                      backgroundColor: '#ffffff'
                    }}
                  />
                )
              )}
              <div style={{ marginTop: '0.75rem' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleRetakeDoc}
                  disabled={isUploading}
                  style={{ fontSize: '0.78rem', padding: '0.35rem 0.75rem' }}
                >
                  Recapture Document
                </button>
              </div>
            </div>

            {/* Face Selfie Preview */}
            <div style={{ textAlign: 'center', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', padding: '1rem' }}>
              <div style={{ fontSize: '0.78rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                Biometric Face Frame
              </div>
              {faceImage ? (
                <img
                  src={faceImage.url}
                  alt="Biometric Face Frame"
                  style={{
                    width: '100%',
                    maxHeight: '220px',
                    objectFit: 'contain',
                    border: '1px solid var(--border-strong)',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: '#ffffff'
                  }}
                />
              ) : (
                <div style={{
                  height: '220px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: 'var(--bg-surface-alt)',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--text-muted)',
                  fontSize: '0.82rem',
                  border: '1px dashed var(--border-strong)'
                }}>
                  Biometric capture bypassed
                </div>
              )}
              <div style={{ marginTop: '0.75rem' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleRetakeFace}
                  disabled={isUploading}
                  style={{ fontSize: '0.78rem', padding: '0.35rem 0.75rem' }}
                >
                  {faceImage ? 'Recapture Biometric' : 'Capture Biometric'}
                </button>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', borderTop: '1px solid var(--border-color)', paddingTop: '1.25rem' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleRetakeDoc}
              disabled={isUploading}
            >
              Reset All
            </button>

            <button
              type="button"
              className="btn btn-primary"
              onClick={handleFinalSubmit}
              disabled={isUploading}
              style={{ minWidth: '240px' }}
            >
              {isUploading ? (
                <>
                  <span className="spinner" style={{ marginRight: '0.5rem' }} />
                  Executing Pipeline...
                </>
              ) : (
                'Run Screening Pipeline'
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
