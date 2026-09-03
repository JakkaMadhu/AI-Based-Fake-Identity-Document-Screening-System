import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getHistory } from '../services/api';
import { StatusBadge, RiskBadge } from '../components/RiskIndicator';

export default function ScreeningHistory() {
  const [historyItems, setHistoryItems] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [riskFilter, setRiskFilter] = useState('All');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchHistory();
  }, [page, statusFilter, riskFilter]);

  async function fetchHistory() {
    setLoading(true);
    setError(null);
    try {
      const data = await getHistory({
        search: search.trim() || undefined,
        status: statusFilter,
        risk_level: riskFilter,
        page,
        page_size: pageSize
      });
      setHistoryItems(data.items || []);
      setTotalItems(data.total || 0);
      setTotalPages(data.total_pages || 1);
    } catch (err) {
      console.error('Failed to load history:', err);
      setError('Unable to query screening ledger from backend.');
    } finally {
      setLoading(false);
    }
  }

  function handleSearchSubmit(e) {
    e.preventDefault();
    setPage(1);
    fetchHistory();
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Screening Ledger & Audit Trail</h1>
        <p className="page-desc">
          Cryptographically hashed screening transactions & historical document evaluations
        </p>
      </div>

      {error && (
        <div style={{ padding: '0.85rem 1.25rem', backgroundColor: 'var(--status-suspicious-bg)', border: '1px solid var(--status-suspicious-border)', borderRadius: 'var(--radius-sm)', color: 'var(--status-suspicious-text)', marginBottom: '1.5rem', fontSize: '0.88rem', fontWeight: 600 }}>
          {error}
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="card" style={{ marginBottom: '1.5rem', padding: '1rem' }}>
        <form onSubmit={handleSearchSubmit} className="filter-bar" style={{ margin: 0 }}>
          <div style={{ flex: 1, minWidth: '220px' }}>
            <input
              type="text"
              className="form-input"
              style={{ width: '100%' }}
              placeholder="Search by Document ID or filename..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div style={{ minWidth: '180px' }}>
            <select
              className="form-select"
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            >
              <option value="All">All Verdicts</option>
              <option value="Likely Genuine">Likely Genuine</option>
              <option value="Suspicious">Suspicious</option>
              <option value="Requires Manual Review">Requires Manual Review</option>
            </select>
          </div>

          <div style={{ minWidth: '160px' }}>
            <select
              className="form-select"
              value={riskFilter}
              onChange={(e) => { setRiskFilter(e.target.value); setPage(1); }}
            >
              <option value="All">All Risk Levels</option>
              <option value="Low Risk">Low Risk</option>
              <option value="Medium Risk">Medium Risk</option>
              <option value="High Risk">High Risk</option>
            </select>
          </div>

          <button type="submit" className="btn btn-secondary">
            Apply Filters
          </button>
        </form>
      </div>

      {/* History Table */}
      <div className="data-table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Document ID</th>
              <th>File Reference</th>
              <th>Screening Timestamp</th>
              <th>Verdict</th>
              <th>Risk Level</th>
              <th>Ledger Block Hash</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                  <span className="spinner" style={{ marginRight: '0.5rem' }} />
                  Loading ledger transactions...
                </td>
              </tr>
            ) : historyItems.length > 0 ? (
              historyItems.map((item) => (
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
                      {item.block_hash ? `${item.block_hash.slice(0, 14)}...` : 'Chained Block'}
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
                <td colSpan="7" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                  No screening records found matching query parameters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.25rem' }}>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
            Showing page {page} of {totalPages} ({totalItems} total transactions)
          </span>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              className="btn btn-secondary"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              Previous
            </button>
            <button
              className="btn btn-secondary"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
