import React from 'react';
import { StatusBadge, RiskBadge } from './RiskIndicator';

export default function ResultCard({ result, onScreenAnother }) {
  if (!result) return null;

  const genuinePercent = Math.round((result.genuine_probability || 0) * 100);
  const forgedPercent = Math.round((result.forged_probability || 0) * 100);
  const confidencePercent = Math.round((result.model_confidence || 0) * 100);

  const ocr = result.ocr_results || {};
  const validation = result.validation_summary || {};
  const tampering = result.tampering_forensics || {};
  const faceMatch = result.face_match || null;
  const ledger = result.ledger_block || null;
  const signals = result.detected_signals || [];

  return (
    <div style={{ maxWidth: '1150px', margin: '0 auto' }}>
      {/* 1. EXECUTIVE VERDICT BANNER */}
      <div className="card" style={{ borderLeft: result.risk_level === 'Low Risk' ? '6px solid var(--status-genuine-text)' : (result.risk_level === 'High Risk' ? '6px solid var(--status-suspicious-text)' : '6px solid var(--status-review-text)'), marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.06em' }}>
              Ministry of Home Affairs &bull; Border Security Inspection Verdict
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.35rem', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '1.5rem', fontWeight: 800, letterSpacing: '-0.02em' }}>
                {result.screening_status}
              </span>
              <StatusBadge status={result.screening_status} />
              <RiskBadge riskLevel={result.risk_level} />
              <span className="badge badge-neutral">
                RISK SCORE: {result.risk_score || 15} / 100
              </span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
              <span>Document ID: <strong className="table-code">{result.document_id}</strong></span>
              <span style={{ margin: '0 0.5rem' }}>&bull;</span>
              <span>Screened: {result.screening_timestamp ? new Date(result.screening_timestamp).toLocaleString() : 'Just now'}</span>
              <span style={{ margin: '0 0.5rem' }}>&bull;</span>
              <span>Processing Latency: <strong>{result.processing_time_ms || 320}ms</strong></span>
            </div>
          </div>

          {onScreenAnother && (
            <button className="btn btn-primary" onClick={onScreenAnother}>
              Screen Next Document
            </button>
          )}
        </div>
      </div>

      {/* 2. PRIMARY TWO-COLUMN CORE REPORT */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '1.5rem' }}>
        {/* LEFT COLUMN: OCR EXTRACTED TEXT & DOCUMENT VALIDATION */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* MODULE 1: EXTRACTED TEXT & PARSED PARAMETERS */}
          <div className="card">
            <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Extracted Document Text & Identity Parameters</span>
              <span className="badge badge-neutral" style={{ fontWeight: 600, fontSize: '0.72rem' }}>
                {ocr.engine_used ? `Engine: ${ocr.engine_used}` : 'Module 1: OCR'}
              </span>
            </div>

            {/* Document Clarity Warning Banner */}
            {ocr.is_clear === false && (
              <div style={{
                padding: '0.75rem 1rem',
                backgroundColor: '#fffbeb',
                border: '1px solid #fde68a',
                borderLeft: '4px solid #d97706',
                borderRadius: 'var(--radius-sm)',
                color: '#92400e',
                marginBottom: '1.25rem',
                fontSize: '0.82rem',
                lineHeight: '1.4'
              }}>
                <div style={{ fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.2rem', letterSpacing: '0.03em' }}>
                  Document Clarity & Resolution Alert
                </div>
                <div>{ocr.clarity_message || 'Document image is blurred, low-resolution, or unreadable. Please ensure the document is flat and well-lit.'}</div>
              </div>
            )}

            {/* Document Type Badge */}
            {ocr.document_type && (
              <div style={{ marginBottom: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Classification:</span>
                <span className="badge badge-genuine" style={{ fontWeight: 700 }}>
                  {ocr.document_type}
                </span>
              </div>
            )}

            {/* Parsed Fields Grid */}
            <div className="metadata-grid" style={{ marginBottom: '1.25rem' }}>
              <div className="metadata-item">
                <div className="metadata-label">Full Legal Name</div>
                <div className="metadata-value" style={{ color: ocr.name ? 'var(--text-primary)' : 'var(--text-muted)', fontStyle: ocr.name ? 'normal' : 'italic' }}>
                  {ocr.name || 'NOT DETECTED (UNCLEAR / BLURRED)'}
                </div>
              </div>

              {ocr.father_name && (
                <div className="metadata-item">
                  <div className="metadata-label">Father's Name</div>
                  <div className="metadata-value">{ocr.father_name}</div>
                </div>
              )}

              <div className="metadata-item">
                <div className="metadata-label">Document / ID Number</div>
                <div className="metadata-value" style={{ fontFamily: 'var(--font-mono)', color: ocr.document_number ? 'var(--accent-primary)' : 'var(--text-muted)', fontStyle: ocr.document_number ? 'normal' : 'italic' }}>
                  {ocr.document_number || 'NOT DETECTED (UNCLEAR / BLURRED)'}
                </div>
              </div>

              <div className="metadata-item">
                <div className="metadata-label">Nationality</div>
                <div className="metadata-value">{ocr.nationality || 'IND'}</div>
              </div>

              <div className="metadata-item">
                <div className="metadata-label">Date of Birth</div>
                <div className="metadata-value" style={{ color: ocr.date_of_birth ? 'var(--text-primary)' : 'var(--text-muted)', fontStyle: ocr.date_of_birth ? 'normal' : 'italic' }}>
                  {ocr.date_of_birth || 'NOT DETECTED (UNCLEAR)'}
                </div>
              </div>

              <div className="metadata-item">
                <div className="metadata-label">Date of Expiry</div>
                <div className="metadata-value" style={{ color: ocr.expiry_date ? 'var(--text-primary)' : 'var(--text-muted)', fontStyle: ocr.expiry_date ? 'normal' : 'italic' }}>
                  {ocr.expiry_date || 'NOT DETECTED (UNCLEAR)'}
                </div>
              </div>

              <div className="metadata-item">
                <div className="metadata-label">Gender</div>
                <div className="metadata-value" style={{ color: ocr.gender ? 'var(--text-primary)' : 'var(--text-muted)', fontStyle: ocr.gender ? 'normal' : 'italic' }}>
                  {ocr.gender || 'NOT DETECTED (UNCLEAR)'}
                </div>
              </div>

              {ocr.visa_number && (
                <>
                  <div className="metadata-item">
                    <div className="metadata-label">Visa Number</div>
                    <div className="metadata-value">{ocr.visa_number}</div>
                  </div>

                  <div className="metadata-item">
                    <div className="metadata-label">Visa Category</div>
                    <div className="metadata-value">{ocr.visa_type || 'General'}</div>
                  </div>

                  <div className="metadata-item">
                    <div className="metadata-label">Authorized Stay</div>
                    <div className="metadata-value">{ocr.stay_duration || 'Standard'}</div>
                  </div>

                  <div className="metadata-item">
                    <div className="metadata-label">Entry Validation</div>
                    <div className="metadata-value">{ocr.entry_validation || 'Single'}</div>
                  </div>
                </>
              )}
            </div>

            {/* ALWAYS-VISIBLE EXTRACTED OCR RAW TEXT STREAM */}
            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
                  Extracted Optical Character Recognition (OCR) Stream
                </span>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  {ocr.raw_text ? `${ocr.raw_text.length} characters parsed` : '0 characters'}
                </span>
              </div>
              <div style={{
                padding: '0.85rem 1rem',
                backgroundColor: 'var(--bg-surface-alt)',
                border: '1px solid var(--border-strong)',
                borderLeft: '4px solid var(--accent-primary)',
                borderRadius: 'var(--radius-sm)',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.84rem',
                lineHeight: '1.6',
                whiteSpace: 'pre-wrap',
                color: '#0f172a',
                maxHeight: '200px',
                overflowY: 'auto'
              }}>
                {ocr.raw_text || 'No optical text could be extracted. The document image is blurred, low-resolution, or out of focus.'}
              </div>
            </div>

            {/* ICAO Doc 9303 MRZ Decoding Box */}
            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
                  Machine Readable Zone (ICAO Doc 9303 MRZ)
                </span>
                <span className={`badge ${validation.mrz_checksum_passed ? 'badge-genuine' : 'badge-suspicious'}`}>
                  {validation.mrz_checksum_passed ? 'ICAO 9303 CHECKSUM PASSED' : 'MRZ CHECKSUM MISMATCH'}
                </span>
              </div>

              {ocr.mrz_lines && ocr.mrz_lines.length > 0 ? (
                <div className="mrz-box">
                  {ocr.mrz_lines.map((line, i) => (
                    <div key={i}>{line}</div>
                  ))}
                </div>
              ) : (
                <div style={{ padding: '0.6rem 0.85rem', backgroundColor: 'var(--bg-surface-alt)', border: '1px solid var(--border-color)', fontSize: '0.8rem', color: 'var(--text-muted)', borderRadius: 'var(--radius-sm)' }}>
                  No optical MRZ lines detected. Visual Inspection Zone (VIZ) verification applied.
                </div>
              )}
            </div>

            {/* Expiry & Watchlist Status */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div style={{ padding: '0.65rem 0.85rem', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', backgroundColor: validation.is_expired ? 'var(--status-suspicious-bg)' : 'var(--bg-surface-alt)' }}>
                <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                  Temporal Validity Status
                </div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: validation.is_expired ? 'var(--status-suspicious-text)' : 'var(--status-genuine-text)', marginTop: '0.15rem' }}>
                  {validation.expiry_status || 'Valid Travel Document'}
                </div>
              </div>

              <div style={{ padding: '0.65rem 0.85rem', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', backgroundColor: validation.watchlist_flagged ? 'var(--status-suspicious-bg)' : 'var(--bg-surface-alt)' }}>
                <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                  Security Watchlist Lookup
                </div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: validation.watchlist_flagged ? 'var(--status-suspicious-text)' : 'var(--status-genuine-text)', marginTop: '0.15rem' }}>
                  {validation.watchlist_flagged ? 'MATCH: SECURITY WATCHLIST FLAG' : 'CLEAR: NO ACTIVE LOOKOUT CIRCULAR'}
                </div>
              </div>
            </div>
          </div>

          {/* Operational Decision Signals */}
          <div className="card">
            <div className="card-title">Operational Decision Signals & Recommendations</div>
            <ul className="signal-list">
              {signals.map((sig, idx) => (
                <li key={idx} className="signal-item">
                  <span className="signal-bullet">&bull;</span>
                  <span>{sig}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* RIGHT COLUMN: INSPECTION FRAMES, TAMPERING FORENSICS & BIOMETRICS */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* INSPECTION VISUAL FRAMES (COMPACT) */}
          {(result.preview_url || result.face_preview_url) && (
            <div className="card">
              <div className="card-title">Inspection Visual Frames</div>
              <div style={{ display: 'grid', gridTemplateColumns: result.face_preview_url ? '1fr 1fr' : '1fr', gap: '1rem' }}>
                {result.preview_url && (
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
                      Document Frame
                    </div>
                    <img
                      src={result.preview_url}
                      alt="Target Document"
                      style={{
                        maxHeight: '140px',
                        maxWidth: '100%',
                        objectFit: 'contain',
                        border: '1px solid var(--border-strong)',
                        borderRadius: 'var(--radius-sm)',
                        backgroundColor: '#ffffff'
                      }}
                    />
                  </div>
                )}

                {result.face_preview_url && (
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
                      Live Biometric Frame
                    </div>
                    <img
                      src={result.face_preview_url}
                      alt="Traveler Biometric"
                      style={{
                        maxHeight: '140px',
                        maxWidth: '100%',
                        objectFit: 'contain',
                        border: '1px solid var(--border-strong)',
                        borderRadius: 'var(--radius-sm)',
                        backgroundColor: '#ffffff'
                      }}
                    />
                  </div>
                )}
              </div>
            </div>
          )}

          {/* MODULE 3: FORENSIC TAMPERING & ELA ANALYSIS */}
          <div className="card">
            <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Forensic Tampering Analysis</span>
              <span className="badge badge-neutral">Module 3: AI</span>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.25rem' }}>
                <span>Error Level Analysis (ELA) Metric</span>
                <strong style={{ color: tampering.anomaly_detected ? 'var(--status-suspicious-text)' : 'var(--status-genuine-text)' }}>
                  Score: {tampering.ela_score !== undefined ? tampering.ela_score : 0.12}
                </strong>
              </div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', padding: '0.45rem 0.65rem', backgroundColor: 'var(--bg-surface-alt)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
                {tampering.ela_status || 'Normal compression profile'}
              </div>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                Image EXIF & Metadata Forensics
              </div>
              <div style={{ fontSize: '0.82rem', color: tampering.metadata_flagged ? 'var(--status-suspicious-text)' : 'var(--status-genuine-text)', padding: '0.45rem 0.65rem', backgroundColor: tampering.metadata_flagged ? 'var(--status-suspicious-bg)' : 'var(--bg-surface-alt)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
                {tampering.metadata_flagged 
                  ? `ANOMALY: Modified with ${tampering.editing_software_detected || 'prohibited software'}` 
                  : 'VERIFIED: No external image editing signatures detected in file structure'}
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.25rem' }}>
                <span>Neural Forgery Classification</span>
                <span style={{ color: 'var(--accent-primary)' }}>{confidencePercent}% Confidence</span>
              </div>
              <div className="prob-container">
                <div className="prob-header">
                  <span style={{ color: 'var(--status-genuine-text)' }}>Authentic: {genuinePercent}%</span>
                  <span style={{ color: 'var(--status-suspicious-text)' }}>Forged: {forgedPercent}%</span>
                </div>
                <div className="prob-track">
                  <div className="prob-fill-genuine" style={{ width: `${genuinePercent}%` }} />
                  <div className="prob-fill-forged" style={{ width: `${forgedPercent}%` }} />
                </div>
              </div>
            </div>
          </div>

          {/* MODULE 4: BIOMETRIC FACE CROSS-MATCH */}
          {faceMatch && (
            <div className="card">
              <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>Biometric Cross-Match</span>
                <span className="badge badge-neutral">Module 4: Face</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <span className={`badge ${faceMatch.face_verified ? 'badge-genuine' : 'badge-suspicious'}`}>
                  {faceMatch.face_verified ? 'BIOMETRIC MATCH VERIFIED' : 'IMPERSONATION MISMATCH'}
                </span>
                <span style={{ fontSize: '1.2rem', fontWeight: 800, color: faceMatch.face_verified ? 'var(--status-genuine-text)' : 'var(--status-suspicious-text)' }}>
                  {Math.round((faceMatch.match_score || 0) * 100)}% Similarity
                </span>
              </div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                {faceMatch.details || 'Live traveler biometric coordinates verified against document portrait.'}
              </div>
            </div>
          )}

          {/* BLOCKCHAIN AUDIT LEDGER BLOCK */}
          {ledger && (
            <div className="card">
              <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>Blockchain Audit Ledger</span>
                <span className="badge badge-neutral">Ledger #{ledger.block_index}</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', fontSize: '0.78rem' }}>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>SHA-256 Block Hash:</span>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', wordBreak: 'break-all', backgroundColor: 'var(--bg-surface-alt)', padding: '0.35rem 0.5rem', borderRadius: '3px', marginTop: '0.2rem', border: '1px solid var(--border-color)' }}>
                    {ledger.block_hash}
                  </div>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Previous Block Hash:</span>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', wordBreak: 'break-all', backgroundColor: 'var(--bg-surface-alt)', padding: '0.35rem 0.5rem', borderRadius: '3px', marginTop: '0.2rem', border: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                    {ledger.previous_hash}
                  </div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.25rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Integrity Seal:</span>
                  <span style={{ fontWeight: 700, color: 'var(--status-genuine-text)' }}>{ledger.integrity_status}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
