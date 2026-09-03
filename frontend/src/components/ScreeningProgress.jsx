import React, { useEffect, useState } from 'react';

const STAGES = [
  { id: 1, title: 'Document Ingestion & Rectification', desc: 'Validating image resolution, aspect ratio, and boundary integrity' },
  { id: 2, title: 'Vision Neural Classification', desc: 'Analyzing micro-patterns, texture continuity, and surface typography' },
  { id: 3, title: 'OCR & ICAO Doc 9303 MRZ Parsing', desc: 'Decoding Machine Readable Zone and Visual Inspection Zone fields' },
  { id: 4, title: 'Rule & Checksum Validation', desc: 'Executing 7-3-1 weight algorithms, temporal expiry checks, and watchlist lookup' },
  { id: 5, title: 'Forensic Tampering & Error Level Analysis', desc: 'Evaluating JPEG compression variance and EXIF editing signatures' },
  { id: 6, title: 'Biometric Cross-Matching & Blockchain Record', desc: 'Matching live selfie against ID portrait and committing SHA-256 block' }
];

export default function ScreeningProgress() {
  const [activeStep, setActiveStep] = useState(1);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => {
        if (prev < 6) return prev + 1;
        clearInterval(interval);
        return prev;
      });
    }, 450);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="card" style={{ maxWidth: '720px', margin: '0 auto', padding: '2rem' }}>
      <div style={{ textAlign: 'center', marginBottom: '1.75rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1.25rem' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.6rem', color: 'var(--accent-primary)', fontWeight: 700, fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          <span className="spinner" />
          <span>Screening Pipeline Active</span>
        </div>
        <h2 style={{ fontSize: '1.35rem', fontWeight: 700, marginTop: '0.4rem', color: 'var(--text-primary)' }}>
          Automated Identity Inspection
        </h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
          Running Modules 1 through 4 & appending to cryptographic audit ledger
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        {STAGES.map((stage) => {
          const isCompleted = activeStep > stage.id;
          const isActive = activeStep === stage.id;

          return (
            <div
              key={stage.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                padding: '0.75rem 1rem',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: isActive ? 'var(--accent-primary-light)' : (isCompleted ? '#ffffff' : 'var(--bg-surface-alt)'),
                border: isActive ? '1px solid var(--accent-primary)' : '1px solid var(--border-color)'
              }}
            >
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: 'var(--radius-sm)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.75rem',
                fontWeight: 700,
                backgroundColor: isCompleted ? 'var(--status-genuine-bg)' : (isActive ? 'var(--accent-primary)' : 'var(--border-color)'),
                color: isCompleted ? 'var(--status-genuine-text)' : (isActive ? '#ffffff' : 'var(--text-muted)'),
                border: isCompleted ? '1px solid var(--status-genuine-border)' : 'none'
              }}>
                {isCompleted ? 'OK' : `0${stage.id}`}
              </div>

              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontWeight: 600, fontSize: '0.88rem', color: 'var(--text-primary)' }}>
                    {stage.title}
                  </div>
                  <span style={{
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    color: isCompleted ? 'var(--status-genuine-text)' : (isActive ? 'var(--accent-primary)' : 'var(--text-muted)')
                  }}>
                    {isCompleted ? 'PASSED' : (isActive ? 'RUNNING' : 'QUEUED')}
                  </span>
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                  {stage.desc}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
