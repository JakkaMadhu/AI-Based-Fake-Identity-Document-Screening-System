import React from 'react';
import { StatusBadge, RiskBadge } from './RiskIndicator';

export default function ResultCard({ result, onScreenAnother }) {
  if (!result) return null;

  const ocr = result.ocr_results || {};
  const validation = result.validation_summary || {};
  const tampering = result.tampering_forensics || {};
  const faceMatch = result.face_match || null;

  const truforScore = tampering.trufor_score !== undefined ? tampering.trufor_score : (result.forged_probability || 0);
  const isTruforTampered = tampering.is_tampered !== undefined ? tampering.is_tampered : (truforScore >= 0.50);

  return (
    <div style={{ maxWidth: '1150px', margin: '0 auto' }}>
      
      {/* 1. EXECUTIVE VERDICT BANNER */}
      <div className="card" style={{ 
        borderLeft: result.risk_level === 'Low Risk' 
          ? '6px solid var(--status-genuine-text)' 
          : (result.risk_level === 'High Risk' ? '6px solid var(--status-suspicious-text)' : '6px solid var(--status-review-text)'), 
        marginBottom: '1.25rem',
        padding: '1.25rem 1.5rem'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.06em' }}>
              Ministry of Home Affairs &bull; Border Security Inspection Verdict
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.4rem', flexWrap: 'wrap' }}>
              <span style={{ 
                fontSize: '1.5rem', 
                fontWeight: 900, 
                letterSpacing: '-0.02em', 
                color: result.risk_level === 'Low Risk' 
                  ? 'var(--status-genuine-text)' 
                  : (result.risk_level === 'High Risk' ? 'var(--status-suspicious-text)' : 'var(--status-review-text)') 
              }}>
                VERDICT: {result.screening_status}
              </span>
              <StatusBadge status={result.screening_status} />
              <RiskBadge riskLevel={result.risk_level} />
              <span className="badge badge-neutral">
                RISK SCORE: {result.risk_score || 15} / 100
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 2. 4 CORE EXECUTIVE HEALTH CHECKPOINTS */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.25rem' }}>
        
        {/* Checkpoint 1: Biometric Match */}
        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
            Biometric Identity
          </div>
          <div style={{ fontSize: '1.05rem', fontWeight: 800, marginTop: '0.25rem', color: faceMatch?.face_verified ? 'var(--status-genuine-text)' : (faceMatch?.is_face_clear === false ? 'var(--status-review-text)' : 'var(--status-suspicious-text)') }}>
            {faceMatch 
              ? (faceMatch.face_verified 
                  ? `Verified (${Math.round(faceMatch.match_score * 100)}%)` 
                  : (faceMatch.is_face_clear === false ? 'Inconclusive (Blurry)' : 'Mismatch Alert'))
              : 'Not Performed'}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            {faceMatch?.face_verified ? 'Live face matches document portrait' : (faceMatch?.is_face_clear === false ? 'Degraded selfie resolution/blur' : 'Traveler divergent from portrait')}
          </div>
        </div>

        {/* Checkpoint 2: Document Forgery / Splicing */}
        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
            Document Forgery Check
          </div>
          <div style={{ fontSize: '1.05rem', fontWeight: 800, marginTop: '0.25rem', color: isTruforTampered ? 'var(--status-suspicious-text)' : 'var(--status-genuine-text)' }}>
            {isTruforTampered ? 'Tampering Detected' : 'Authentic Pixel Grid'}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            {isTruforTampered ? 'Pixel splicing or edited text identified' : 'No digital manipulation detected'}
          </div>
        </div>

        {/* Checkpoint 3: Data Extraction Consistency */}
        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
            OCR Data Integrity
          </div>
          <div style={{ fontSize: '1.05rem', fontWeight: 800, marginTop: '0.25rem', color: ocr.name && ocr.document_number ? 'var(--status-genuine-text)' : 'var(--status-review-text)' }}>
            {ocr.name && ocr.document_number ? 'Complete & Extracted' : 'Missing / Incomplete'}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            {ocr.is_clear !== false ? 'All mandatory fields parsed cleanly' : 'Image blur obscured text extraction'}
          </div>
        </div>

        {/* Checkpoint 4: Rules & Security Watchlist */}
        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
            ICAO Rules & Watchlist
          </div>
          <div style={{ fontSize: '1.05rem', fontWeight: 800, marginTop: '0.25rem', color: (validation.watchlist_flagged || validation.is_expired) ? 'var(--status-suspicious-text)' : 'var(--status-genuine-text)' }}>
            {validation.watchlist_flagged ? 'WATCHLIST ALERT' : (validation.is_expired ? 'EXPIRED DOCUMENT' : 'Valid & Clear')}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            {validation.watchlist_flagged ? 'Active national security lookout hit' : (validation.is_expired ? 'Document validity expired' : 'No watchlists or check digit issues')}
          </div>
        </div>
      </div>

      {/* 3. ESSENTIAL TRAVELER IDENTITY PROFILE & VISUAL FRAMES (Side-by-Side) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', marginBottom: '1.25rem' }}>
        
        {/* Left: Traveler Verified Identity (Necessary Data Only) */}
        <div className="card" style={{ padding: '1.25rem' }}>
          <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <span>Verified Traveler Profile</span>
            {ocr.document_type && (
              <span className="badge badge-genuine" style={{ fontWeight: 700 }}>
                {ocr.document_type}
              </span>
            )}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Full Legal Name</span>
              <strong style={{ fontSize: '0.95rem', color: 'var(--text-primary)' }}>{ocr.name || 'Not Available'}</strong>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Document ID Number</span>
              <strong style={{ fontSize: '0.95rem', fontFamily: 'var(--font-mono)', color: 'var(--accent-primary)' }}>{ocr.document_number || 'Not Available'}</strong>
            </div>

            {ocr.father_name && (
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Father's Name</span>
                <span style={{ fontSize: '0.88rem', color: 'var(--text-primary)' }}>{ocr.father_name}</span>
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Date of Birth</span>
              <span style={{ fontSize: '0.88rem', color: 'var(--text-primary)' }}>{ocr.date_of_birth || 'N/A'}</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Nationality</span>
              <span style={{ fontSize: '0.88rem', color: 'var(--text-primary)' }}>{ocr.nationality || 'IND'}</span>
            </div>
          </div>
        </div>

        {/* Right: Visual Inspection (Document Scan vs Live Face) */}
        <div className="card" style={{ padding: '1.25rem' }}>
          <div className="card-title" style={{ marginBottom: '1rem' }}>
            <span>Inspection Visual Frames</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: result.face_preview_url ? '1fr 1fr' : '1fr', gap: '1rem' }}>
            {result.preview_url && (
              <div>
                <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
                  Document Frame
                </div>
                <img
                  src={result.preview_url}
                  alt="Document scan"
                  style={{
                    width: '100%',
                    height: '160px',
                    objectFit: 'cover',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-color)',
                    backgroundColor: '#000'
                  }}
                />
              </div>
            )}

            {result.face_preview_url && (
              <div>
                <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
                  Live Biometric Frame
                </div>
                <img
                  src={result.face_preview_url}
                  alt="Live biometric capture"
                  style={{
                    width: '100%',
                    height: '160px',
                    objectFit: 'cover',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-color)',
                    backgroundColor: '#000'
                  }}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
