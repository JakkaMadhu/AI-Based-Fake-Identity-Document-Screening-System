# AI-Based Identity Document Screening System - Frontend

Cybersecurity / biometric verification interface built with **React**, **Vite**, and **Modern Vanilla CSS**.

## Features

- **Live Camera Scanner**: Real-time WebRTC webcam scan with card alignment guide and instant snapshot capture.
- **Drag & Drop Uploader**: Direct file drop with client-side image validation (JPG, JPEG, PNG, max 10MB).
- **Multi-Stage Progress Animation**: 6-stage pipeline tracker illustrating validation, preprocessing, vision AI, OCR, and risk synthesis.
- **Structured Verification Report**: Probability meters, risk assessment badge, parsed identity fields (Name, DOB, Doc Number), and detected signals list.
- **Dashboard & Audit History**: Aggregate metric cards, recent scan logs, full-text search, and multi-parameter filters.

## Running Locally

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Vite Development Server
```bash
npm run dev
```

The application will be accessible at: [http://localhost:5173](http://localhost:5173) (automatically proxied to FastAPI backend on port 8000).
