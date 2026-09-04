import React from 'react';
import { Link } from 'react-router-dom';

export default function Navbar({ onToggleSidebar }) {
  return (
    <header className="navbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {/* Three Bars Hamburger Icon */}
        <button 
          type="button" 
          className="hamburger-btn" 
          onClick={onToggleSidebar}
          aria-label="Toggle Navigation Menu"
          title="Open Menu"
        >
          <span className="hamburger-line" />
          <span className="hamburger-line" />
          <span className="hamburger-line" />
        </button>

        <div className="navbar-brand">
          <Link to="/dashboard" className="navbar-title">
            Document Screening System
          </Link>
          <span className="navbar-subtitle">
            Identity Verification & Forgery Screening
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', fontSize: '0.78rem', fontWeight: 600, color: 'var(--status-genuine-text)' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--status-genuine-text)', display: 'inline-block' }} />
          <span>SYSTEM ONLINE</span>
        </div>
      </div>
    </header>
  );
}
