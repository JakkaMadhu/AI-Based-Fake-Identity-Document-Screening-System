import React, { useEffect, useState, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getDashboardStats, getHistory } from '../services/api';
import { StatusBadge, RiskBadge } from '../components/RiskIndicator';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loadingStats, setLoadingStats] = useState(true);
  const [error, setError] = useState(null);

  // Search & Table States
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [riskFilter, setRiskFilter] = useState('All');
  const [page, setPage] = useState(1);
  const pageSize = 8;

  const [historyItems, setHistoryItems] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const navigate = useNavigate();

  // Load Dashboard Aggregate Statistics
  useEffect(() => {
    async function loadStats() {
      setLoadingStats(true);
      try {
        const data = await getDashboardStats();
        setStats(data);
      } catch (err) {
        console.error('Failed to load dashboard statistics:', err);
        setError('Unable to connect to backend service. Ensure FastAPI server is running.');
      } finally {
        setLoadingStats(false);
      }
    }
    loadStats();
  }, []);

  // Load Filterable Screening Ledger
  const fetchLedger = useCallback(async () => {
    setLoadingHistory(true);
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
      console.error('Failed to query ledger transactions:', err);
    } finally {
      setLoadingHistory(false);
    }
  }, [search, statusFilter, riskFilter, page, pageSize]);

  useEffect(() => {
    fetchLedger();
  }, [fetchLedger]);

  function handleSearchSubmit(e) {
    e.preventDefault();
    setPage(1);
    fetchLedger();
  }

  function handleClearFilters() {
    setSearch('');
    setStatusFilter('All');
    setRiskFilter('All');
    setPage(1);
  }

  return (
    <div className="page-container">
      {/* Page Header */}
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 className="page-title">Screening Operations Dashboard</h1>
          <p className="page-desc">
            Real-time Verification Metrics & Cryptographic Inspection Ledger
          </p>
        </div>
        <Link to="/upload" className="btn btn-primary" style={{ padding: '0.65rem 1.4rem' }}>
          Screen New Document
        </Link>
      </div>

      {error && (
        <div style={{
          padding: '0.85rem 1.25rem',
          backgroundColor: 'var(--status-suspicious-bg)',
          border: '1px solid var(--status-suspicious-border)',
          borderRadius: 'var(--radius-sm)',
          color: 'var(--status-suspicious-text)',
          marginBottom: '1.5rem',
          fontSize: '0.88rem',
          fontWeight: 600
        }}>
          {error}
        </div>
      )}

      {/* Metrics Row */}
      <div className="metrics-row" style={{ marginBottom: '2rem' }}>
        <div className="metric-card">
          <div className="metric-label">Total Screened</div>
          <div className="metric-value">{stats ? stats.total_screened : (loadingStats ? '...' : 0)}</div>
        </div>

        <div className="metric-card genuine">
          <div className="metric-label">Likely Genuine</div>
          <div className="metric-value" style={{ color: 'var(--status-genuine-text)' }}>
            {stats ? stats.likely_genuine : (loadingStats ? '...' : 0)}
          </div>
        </div>

        <div className="metric-card suspicious">
          <div className="metric-label">Suspicious / Tampered</div>
          <div className="metric-value" style={{ color: 'var(--status-suspicious-text)' }}>
            {stats ? stats.suspicious : (loadingStats ? '...' : 0)}
          </div>
        </div>

        <div className="metric-card review">
          <div className="metric-label">Requires Manual Review</div>
          <div className="metric-value" style={{ color: 'var(--status-review-text)' }}>
            {stats ? stats.requires_manual_review : (loadingStats ? '...' : 0)}
          </div>
        </div>
      </div>

      {/* LEDGER & SEARCH SECTION */}
      <div className="card" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div>
            <h2 className="card-title" style={{ margin: 0, border: 'none', padding: 0, fontSize: '1.15rem' }}>
              Screening Inspection Ledger
            </h2>
            <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Showing {historyItems.length} of {totalItems} recorded screening records
            </p>
          </div>

          {(search || statusFilter !== 'All' || riskFilter !== 'All') && (
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={handleClearFilters}
              style={{ fontSize: '0.78rem', padding: '0.35rem 0.75rem' }}
            >
              Reset Filters
            </button>
          )}
        </div>

        {/* Search & Filter Controls below stats */}
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '240px' }}>
            <input
              type="text"
              className="form-input"
              style={{ width: '100%', padding: '0.55rem 0.85rem' }}
              placeholder="Search by Document ID or filename..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div style={{ minWidth: '170px' }}>
            <select
              className="form-select"
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
              style={{ width: '100%', padding: '0.55rem 0.85rem' }}
            >
              <option value="All">All Verdicts</option>
              <option value="Likely Genuine">Likely Genuine</option>
              <option value="Suspicious">Suspicious</option>
              <option value="Requires Manual Review">Requires Manual Review</option>
            </select>
          </div>

          <div style={{ minWidth: '150px' }}>
            <select
              className="form-select"
              value={riskFilter}
              onChange={(e) => { setRiskFilter(e.target.value); setPage(1); }}
              style={{ width: '100%', padding: '0.55rem 0.85rem' }}
            >
              <option value="All">All Risk Levels</option>
              <option value="Low Risk">Low Risk</option>
              <option value="Medium Risk">Medium Risk</option>
              <option value="High Risk">High Risk</option>
            </select>
          </div>

          <button type="submit" className="btn btn-primary" style={{ padding: '0.55rem 1.1rem', textTransform: 'uppercase', fontSize: '0.78rem' }}>
            Search
          </button>
        </form>

        {/* Data Table */}
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
                <th style={{ textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {historyItems.length > 0 ? (
                historyItems.map((item) => (
                  <tr key={item.document_id}>
                    <td>
                      <span className="table-code">{item.document_id}</span>
                    </td>
                    <td>
                      <strong style={{ fontSize: '0.85rem' }}>{item.filename}</strong>
                    </td>
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
                    <td style={{ textAlign: 'right' }}>
                      <button
                        type="button"
                        className="btn btn-secondary"
                        style={{ padding: '0.3rem 0.75rem', fontSize: '0.75rem' }}
                        onClick={() => navigate(`/result/${item.document_id}`)}
                      >
                        View Dossier
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '3rem 1.5rem', color: 'var(--text-muted)' }}>
                    {loadingHistory ? (
                      <div>Querying cryptographic inspection records...</div>
                    ) : (
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '0.35rem', color: 'var(--text-secondary)' }}>
                          No Matching Screening Records Found
                        </div>
                        <div style={{ fontSize: '0.8rem' }}>
                          Try adjusting your search query or verdict filters, or screen a new document.
                        </div>
                      </div>
                    )}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)', fontSize: '0.82rem' }}>
            <span style={{ color: 'var(--text-muted)' }}>
              Page <strong>{page}</strong> of <strong>{totalPages}</strong> ({totalItems} total items)
            </span>

            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                type="button"
                className="btn btn-secondary"
                disabled={page <= 1 || loadingHistory}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                style={{ padding: '0.35rem 0.85rem', fontSize: '0.75rem' }}
              >
                &larr; Previous
              </button>

              <button
                type="button"
                className="btn btn-secondary"
                disabled={page >= totalPages || loadingHistory}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                style={{ padding: '0.35rem 0.85rem', fontSize: '0.75rem' }}
              >
                Next &rarr;
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
