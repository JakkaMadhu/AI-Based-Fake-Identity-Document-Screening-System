import React from 'react';

export default function ImagePreview({ previewUrl, filename, onRemove, onProceed, isUploading }) {
  return (
    <div className="card">
      <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
        <div>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, margin: 0 }}>Document Optical Preview</h3>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{filename || 'Document Image'}</p>
        </div>
        <button className="btn btn-secondary" onClick={onRemove} disabled={isUploading}>
          Remove File
        </button>
      </div>

      <div style={{ textAlign: 'center', padding: '1rem', backgroundColor: 'var(--bg-surface-alt)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
        <img
          src={previewUrl}
          alt="Document Preview"
          style={{
            maxHeight: '340px',
            maxWidth: '100%',
            objectFit: 'contain',
            borderRadius: 'var(--radius-sm)'
          }}
        />
      </div>

      <div style={{ width: '100%', display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1.25rem' }}>
        <button className="btn btn-secondary" onClick={onRemove} disabled={isUploading}>
          Cancel
        </button>
        <button className="btn btn-primary" onClick={onProceed} disabled={isUploading}>
          {isUploading ? (
            <>
              <span className="spinner" style={{ marginRight: '0.5rem' }} />
              Ingesting Image...
            </>
          ) : (
            'Proceed to Verification'
          )}
        </button>
      </div>
    </div>
  );
}
