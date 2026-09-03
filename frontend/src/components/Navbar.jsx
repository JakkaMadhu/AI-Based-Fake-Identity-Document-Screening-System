import React from 'react';
import { Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <header className="navbar">
      <div className="navbar-brand">
        <Link to="/dashboard" className="navbar-title">
          Document Screening System
        </Link>
        <span className="navbar-subtitle">
          Ministry of Home Affairs &bull; Border Checkpoint Unit
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', fontWeight: 600, color: 'var(--status-genuine-text)' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--status-genuine-text)', display: 'inline-block' }} />
          <span>SYSTEM ONLINE</span>
        </div>

        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', borderLeft: '1px solid var(--border-color)', paddingLeft: '1rem' }}>
          <span style={{ fontWeight: 600 }}>Officer ID:</span> SSB-CP-0824
        </div>
      </div>
    </header>
  );
}
