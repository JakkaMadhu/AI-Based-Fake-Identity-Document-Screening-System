import React from 'react';
import { NavLink } from 'react-router-dom';

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-heading">Navigation Menu</div>

      <NavLink 
        to="/dashboard" 
        className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
      >
        Operations Dashboard
      </NavLink>

      <NavLink 
        to="/upload" 
        className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
      >
        Screen New Document
      </NavLink>

      <NavLink 
        to="/history" 
        className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
      >
        Inspection Log & Ledger
      </NavLink>

      <NavLink 
        to="/login" 
        className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
      >
        Officer Authentication
      </NavLink>

      <div style={{ marginTop: 'auto', paddingTop: '1.5rem', borderTop: '1px solid var(--border-color)', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
        <div style={{ fontWeight: 700, color: 'var(--text-secondary)' }}>ICAO DOC 9303 & ELA</div>
        <div>Standard Security Checkpoint</div>
        <div style={{ marginTop: '0.4rem', fontFamily: 'var(--font-mono)' }}>Ver 2.4.0 (SIH-2026)</div>
      </div>
    </aside>
  );
}
