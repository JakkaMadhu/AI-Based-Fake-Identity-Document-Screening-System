import React from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import UploadDocument from './pages/UploadDocument';
import ScreeningResult from './pages/ScreeningResult';
import ScreeningHistory from './pages/ScreeningHistory';
import Login from './pages/Login';

export default function App() {
  const location = useLocation();
  const isLoginPage = location.pathname === '/login';

  return (
    <div className="app-container">
      {!isLoginPage && <Sidebar />}

      <div className="main-content">
        {!isLoginPage && <Navbar />}

        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload" element={<UploadDocument />} />
          <Route path="/result/:documentId" element={<ScreeningResult />} />
          <Route path="/history" element={<ScreeningHistory />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </div>
    </div>
  );
}
