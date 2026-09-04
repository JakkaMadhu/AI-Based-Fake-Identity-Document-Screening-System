import React from 'react';
import { NavLink } from 'react-router-dom';

export default function Sidebar({ isOpen, onClose }) {
  return (
    <>
      {/* Backdrop overlay */}
      {isOpen && (
        <div 
          className="sidebar-backdrop" 
          onClick={onClose} 
          aria-hidden="true" 
        />
      )}

      {/* Slide-out Drawer */}
      <aside className={`sidebar-drawer ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-heading">Navigation Menu</div>
          <button 
            type="button" 
            className="sidebar-close-btn" 
            onClick={onClose}
            aria-label="Close navigation menu"
          >
            &times;
          </button>
        </div>

        <nav className="sidebar-nav">
          <NavLink 
            to="/dashboard" 
            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            onClick={onClose}
          >
            Operations Dashboard
          </NavLink>

          <NavLink 
            to="/upload" 
            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            onClick={onClose}
          >
            Screen New Document
          </NavLink>
        </nav>

        <div className="sidebar-footer">
          <div style={{ fontWeight: 700, color: 'var(--text-secondary)' }}>
            AI Document Screening System
          </div>
          <div>Sovereign Vision OCR & Biometrics</div>
          <div style={{ marginTop: '0.4rem', fontFamily: 'var(--font-mono)', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            Ver 2.5.0 &bull; Multi-Spectral Inspection
          </div>
        </div>
      </aside>
    </>
  );
}
