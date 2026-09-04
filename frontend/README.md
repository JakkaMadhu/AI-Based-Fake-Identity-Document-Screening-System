# AI Border Screening System — Modern Cyber-Defense Verification Portal

[![React 18](https://img.shields.io/badge/React-18.x-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.x-646CFF.svg)](https://vitejs.dev/)
[![Design System](https://img.shields.io/badge/Design-Cyber%20Dark%20Glassmorphism-00e5ff.svg)]()
[![WebRTC](https://img.shields.io/badge/WebRTC-Dual--Stream%20Capture-34A853.svg)]()

The frontend is an enterprise-grade, single-page application (SPA) designed for border control officers, immigration inspection desks, and automated e-Gate kiosks. Built with **React 18**, **Vite**, and a bespoke **Cyber-Defense Glassmorphic CSS System**, it provides real-time dual-camera capture, interactive visual forensics, and an executive decision cockpit.

---

## Table of Contents
1. [User Experience & Design Philosophy](#user-experience--design-philosophy)
2. [Core Interface Components](#core-interface-components)
   - [2.1 Live Camera Scanner (`LiveCameraScanner.jsx`)](#21-live-camera-scanner-livecamerascannerjsx)
   - [2.2 Document Ingestion Engine (`DocumentUploader.jsx`)](#22-document-ingestion-engine-documentuploaderjsx)
   - [2.3 Executive Inspection Cockpit (`ScreeningResult.jsx` & `ResultCard.jsx`)](#23-executive-inspection-cockpit-screeningresultjsx--resultcardjsx)
   - [2.4 Operations Dashboard (`Dashboard.jsx`)](#24-operations-dashboard-dashboardjsx)
   - [2.5 Pipeline Progress Animation (`ScreeningProgress.jsx`)](#25-pipeline-progress-animation-screeningprogressjsx)
3. [Design System & CSS Architecture](#design-system--css-architecture)
4. [State Management & API Integration](#state-management--api-integration)
5. [Local Development & Build Pipeline](#local-development--build-pipeline)
6. [Hardware & Camera Integration](#hardware--camera-integration)

---

## User Experience & Design Philosophy

Identity screening at national border checkpoints demands immediate cognitive clarity without unnecessary cognitive clutter:
- **Cyber-Defense Dark Glassmorphism**: High-contrast, deep space dark background (`#090d16`) with semi-transparent frosted cards (`backdrop-filter: blur(16px)`), luminous neon accents, and subtle borders.
- **Executive Abstracted View**: Complex mathematical weights and raw OCR streams are synthesized into intuitive, scannable checkpoints. Critical directives and hard overrides are surfaced instantly.
- **Micro-Animations & Visual Hierarchy**: Smooth state transitions, glowing status pulses, and progress trackers provide real-time sensory feedback to immigration agents during automated inspection.

---

## Core Interface Components

### 2.1 Live Camera Scanner (`LiveCameraScanner.jsx`)

Provides a native WebRTC video capture interface tailored for self-service e-Gates or manual officer desks:
- **2-Step Live KYC Guided Capture**:
  1. **Step 1 (Credential Capture)**: Displays an illuminated rectangular overlay guide for passport/ID card alignment. Real-time client-side canvas cropping captures high-resolution document frames.
  2. **Step 2 (Live Traveler Selfie)**: Automatically transitions to an oval biometric framing guide to capture the traveler's face under proper lighting and posture.
- **Multi-Camera Device Switching**: Allows operators to switch between overhead document cameras and front-facing biometric webcams via hardware enumeration (`navigator.mediaDevices.enumerateDevices`).

---

### 2.2 Document Ingestion Engine (`DocumentUploader.jsx`)

Supports file-based screening for e-Visa portals and secondary inspection offices:
- **Drag-and-Drop Ingestion**: Accepts high-resolution image formats (`.jpg`, `.jpeg`, `.png`) and multi-page documents (`.pdf`).
- **Client-Side Validation**: Performs instant MIME-type and file size verification (up to 10MB) before payload transmission.
- **Optional Companion Selfie**: Enables uploading a physical document image alongside a live portrait capture for 1:1 cross-verification.

---

### 2.3 Executive Inspection Cockpit (`ScreeningResult.jsx` & `ResultCard.jsx`)

The screening report is engineered for rapid, error-free officer decisioning:

```text
┌───────────────────────────────────────────────────────────────────────────┐
│                                                 [ Scan New Document ]     │
├───────────────────────────────────────────────────────────────────────────┤
│  VERDICT BANNER: LIKELY GENUINE (LOW RISK)             RISK SCORE: 14/100 │
├───────────────────────────────────────────────────────────────────────────┤
│  CHECKPOINT CARDS                                                         │
│  ┌──────────────────┐ ┌──────────────────┐ ┌───────────────┐ ┌──────────┐ │
│  │ Biometric Match  │ │ Forgery Forensics│ │ Identity & OCR│ │ Security │ │
│  │ 92.5% (Match)    │ │ 6% Tampering     │ │ Verified      │ │ ICAO Pass│ │
│  └──────────────────┘ └──────────────────┘ └───────────────┘ └──────────┘ │
├───────────────────────────────────────────────────────────────────────────┤
│  VISUAL EVIDENCE & FORENSIC MAPS       VERIFIED TRAVELER PROFILE          │
│  ┌───────────────────┬───────────────┐ ┌────────────────────────────────┐ │
│  │ Credential Photo  │ Live Selfie   │ │ Holder Name: JOHN DOE          │ │
│  │ [Face Crop]       │ [Live Crop]   │ │ Document No: P83726194         │ │
│  ├───────────────────┴───────────────┤ │ Date of Birth: 1988-04-12      │ │
│  │ Forensic Anomaly Heatmap          │ │ Expiry Date: 2030-05-18        │ │
│  │ [TruFor Jet Overlay]              │ │ Nationality: USA               │ │
│  └───────────────────────────────────┘ └────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────┘
```

#### Key Capabilities:
1. **Dynamic Verdict Banners**:
   - **`Likely Genuine`**: Neon emerald banner indicating low composite risk and complete biometric/ICAO verification.
   - **`Requires Manual Review`**: Amber banner indicating borderline biometric distance, soft focus, or unverified secondary data.
   - **`Suspicious`**: Crimson alert banner highlighting hard overrides (impostor detection, physical splicing, or ICAO checksum tampering).
2. **Four Core Checkpoint Metrics**:
   - **Biometric Match**: Displays Inception-ResNet-V1 match percentage, Euclidean distance, and clarity status.
   - **Deep Forgery Analysis**: Displays TruFor convolutional anomaly probability and pixel-level tampering status.
   - **Identity & OCR**: Displays extraction completeness and vision model confidence.
   - **Rule & Security Checks**: Displays ICAO Doc 9303 checksum results, date validity, and security watchlist clearance.
3. **Synchronized Visual Evidence**:
   - Side-by-side biometric comparison (ID card photo crop vs. live traveler capture).
   - Interactive TruFor anomaly heatmap overlay showing exact modified pixel coordinates.
4. **Verified Identity Profile**: Cleanly formats parsed credentials (Name, Document Number, Date of Birth, Expiration Date, Nationality, Document Type).

---

### 2.4 Operations Dashboard (`Dashboard.jsx`)

Provides real-time situational awareness for border station supervisors:
- **Operational Metrics**: Real-time counters for Total Screened Documents, Likely Genuine (Clear), Requires Manual Review, and Suspicious (Rejected).
- **Pass / Fail Ratios**: Visual distribution meters reflecting automated border control throughput.
- **Live Activity Feed**: Tabular stream of recent inspections with document thumbnails, timestamps, risk scores, and SHA-256 blockchain verification hashes.

---

### 2.5 Pipeline Progress Animation (`ScreeningProgress.jsx`)

Displays an animated multi-stage verification sequence during document processing:
1. File Validation & Metadata Integrity
2. High-DPI Preprocessing & Error Level Analysis (ELA)
3. TruFor Deep Convolutional Forgery Localization
4. Sovereign Vision-Language OCR (Qwen2.5-VL)
5. Biometric Face Alignment & Euclidean Distance Matching
6. Cryptographic Hash Commitment to SHA-256 Ledger

---

## Design System & CSS Architecture

All styles are defined in `src/index.css` using modern CSS variables and utility classes:

```css
:root {
  --bg-primary: #090d16;
  --bg-secondary: #0f172a;
  --bg-card: rgba(15, 23, 42, 0.75);
  --border-color: rgba(255, 255, 255, 0.08);
  
  --accent-primary: #00e5ff;       /* Cyber Cyan */
  --accent-secondary: #3b82f6;     /* Electric Blue */
  
  --status-genuine: #10b981;       /* Emerald */
  --status-warning: #f59e0b;       /* Amber */
  --status-suspicious: #ef4444;    /* Crimson */
  
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
```

- **Glassmorphic Cards**: Rendered with `background: var(--bg-card); backdrop-filter: blur(16px); border: 1px solid var(--border-color);`.
- **Responsive Layout**: Fluid grid architecture scaling from handheld mobile inspection tablets to ultra-wide operations monitors.

---

## State Management & API Integration

The API client in `src/services/api.js` connects to the FastAPI backend:
- **Reverse Proxy**: In `vite.config.js`, requests starting with `/api` and `/uploads` are automatically routed to `http://127.0.0.1:8000`.
- **Multipart Ingestion**: Sends raw file streams and Base64 WebRTC camera payloads.
- **Error Handling**: Gracefully surfaces backend diagnostics (e.g., camera motion blur, corrupt files) into user-friendly UI alerts.

---

## Local Development & Build Pipeline

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Local Development Server
```bash
npm run dev
```
The application will launch at `http://localhost:5173`.

### 3. Build for Production
To create an optimized production build:
```bash
npm run build
```
The compiled assets will be placed in the `dist/` directory, ready for deployment to Nginx, AWS S3, or Cloudflare Pages.

### 4. Preview Production Build
```bash
npm run preview
```

---

## Hardware & Camera Integration

For automated e-Gate kiosks:
- **Resolution**: Recommended webcam resolution is 1080p ($1920 \times 1080$) at 30 FPS.
- **Lighting**: Diffused, non-reflective LED lighting minimizes glare on plastic laminate cards.
- **WebRTC Permissions**: Ensure the browser is granted camera access (`getUserMedia`) over HTTPS or `localhost`.
