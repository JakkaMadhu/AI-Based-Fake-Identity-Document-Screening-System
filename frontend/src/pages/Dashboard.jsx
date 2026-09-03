import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getDashboardStats } from '../services/api';
import { StatusBadge, RiskBadge } from '../components/RiskIndicator';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchStats();
  }, []);

  async function fetchStats() {
    setLoading(true);
    try {
      const data = await getDashboardStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load stats:', err);
      setError('Unable to connect to screening services. Ensure FastAPI backend is active.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-container">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 className="page-title">Operations & Screening Dashboard</h1>
          <p className="page-desc">
            Sashastra Seema Bal &bull; Border Checkpoint Inspection Analytics & Cryptographic Ledger
          </p>
        </div>
        <Link to="/upload" className="btn btn-primary">
          Screen New Document
        </Link>
      </div>

      {error && (
        <div style={{ padding: '0.85rem 1.25rem', backgroundColor: 'var(--status-suspicious-bg)', border: '1px solid var(--status-suspicious-border)', borderRadius: 'var(--radius-sm)', color: 'var(--status-suspicious-text)', marginBottom: '1.5rem', fontSize: '0.88rem', fontWeight: 600 }}>
          {error}
        </div>
      )}

      {/* Metrics Row */}
      <div className="metrics-row">
        <div className="metric-card">
          <div className="metric-label">Total Screened</div>
          <div className="metric-value">{stats ? stats.total_screened : (loading ? '...' : 0)}</div>
        </div>

        <div className="metric-card genuine">
          <div className="metric-label">Likely Genuine</div>
          <div className="metric-value" style={{ color: 'var(--status-genuine-text)' }}>
            {stats ? stats.likely_genuine : (loading ? '...' : 0)}
          </div>
        </div>

        <div className="metric-card suspicious">
          <div className="metric-label">Suspicious / Tampered</div>
          <div className="metric-value" style={{ color: 'var(--status-suspicious-text)' }}>
            {stats ? stats.suspicious : (loading ? '...' : 0)}
          </div>
        </div>

        <div className="metric-card review">
          <div className="metric-label">Requires Manual Review</div>
          <div className="metric-value" style={{ color: 'var(--status-review-text)' }}>
            {stats ? stats.requires_manual_review : (loading ? '...' : 0)}
          </div>
        </div>
      </div>

      {/* Recent Screening Activity */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <h2 className="card-title" style={{ margin: 0, border: 'none', padding: 0 }}>
            Recent Screening Transactions
          </h2>
          <Link to="/history" style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-primary)', textDecoration: 'none' }}>
            View Full Inspection Ledger
          </Link>
        </div>

        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Document ID</th>
                <th>File Reference</th>
                <th>Inspection Timestamp</th>
                <th>Screening Verdict</th>
                <th>Risk Classification</th>
                <th>Ledger SHA-256 Hash</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {stats && stats.recent_activity && stats.recent_activity.length > 0 ? (
                stats.recent_activity.map((item) => (
                  <tr key={item.document_id}>
                    <td><span className="table-code">{item.document_id}</span></td>
                    <td><strong>{item.filename}</strong></td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      {item.screening_date ? new Date(item.screening_date).toLocaleString() : 'N/A'}
                    </td>
                    <td>
                      <StatusBadge status={item.status} />
                    </td>
                    <td>
                      <RiskBadge riskLevel={item.risk_level} />
                    </td>
                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        {item.block_hash ? `${item.block_hash.slice(0, 12)}...` : 'Chained Block'}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn btn-secondary"
                        style={{ padding: '0.25rem 0.65rem', fontSize: '0.75rem' }}
                        onClick={() => navigate(`/result/${item.document_id}`)}
                      >
                        View Report
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--text-muted)' }}>
                    {loading ? 'Querying records...' : 'No active records. Initiate document screening to generate transactions.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
