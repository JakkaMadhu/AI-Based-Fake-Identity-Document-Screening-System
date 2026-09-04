import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ResultCard from '../components/ResultCard';
import { getDocumentResult } from '../services/api';

export default function ScreeningResult() {
  const { documentId } = useParams();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (documentId) {
      loadResult(documentId);
    }
  }, [documentId]);

  async function loadResult(id) {
    setLoading(true);
    setError(null);
    try {
      const data = await getDocumentResult(id);
      setResult(data);
    } catch (err) {
      console.error('Failed to load result:', err);
      setError(err.message || 'Unable to retrieve screening report.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', marginBottom: '1.25rem' }}>
        <button 
          className="btn btn-primary" 
          onClick={() => navigate('/upload')} 
          style={{ padding: '0.45rem 1.1rem', fontSize: '0.85rem', fontWeight: 700, borderRadius: '6px' }}
        >
          Scan New Document
        </button>
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: '4rem 1rem' }}>
          <span className="spinner" style={{ width: '28px', height: '28px', borderWidth: '3px', marginBottom: '0.75rem' }} />
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Retrieving inspection record {documentId}...
          </p>
        </div>
      )}

      {error && (
        <div className="card" style={{ maxWidth: '600px', margin: '2rem auto', textAlign: 'center', padding: '2.5rem' }}>
          <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--status-suspicious-text)', marginBottom: '0.5rem' }}>
            RECORD NOT FOUND
          </div>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
            {error}
          </p>
          <button className="btn btn-primary" onClick={() => navigate('/upload')}>
            Screen New Document
          </button>
        </div>
      )}

      {!loading && !error && result && (
        <ResultCard
          result={result}
          onScreenAnother={() => navigate('/upload')}
        />
      )}
    </div>
  );
}
