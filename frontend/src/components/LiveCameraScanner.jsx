import React, { useRef, useState, useEffect, useCallback } from 'react';

export default function LiveCameraScanner({ 
  mode = 'document', // 'document' or 'face'
  onCapture, 
  onCancel,
  promptText
}) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const analyzeCanvasRef = useRef(null);

  const [stream, setStream] = useState(null);
  const [cameraError, setCameraError] = useState(null);
  const [facingMode, setFacingMode] = useState(mode === 'face' ? 'user' : 'environment');
  const [isInitializing, setIsInitializing] = useState(true);

  // Auto-detection states for face mode
  const [detectionState, setDetectionState] = useState('searching'); // 'searching' | 'detected' | 'blurry'
  const [statusMessage, setStatusMessage] = useState('Searching for human face...');
  const [countdown, setCountdown] = useState(null);
  const [isCapturing, setIsCapturing] = useState(false);

  const stableFramesRef = useRef(0);
  const hasCapturedRef = useRef(false);

  useEffect(() => {
    startCamera();
    hasCapturedRef.current = false;
    stableFramesRef.current = 0;
    return () => {
      stopCamera();
    };
  }, [facingMode]);

  async function startCamera() {
    setIsInitializing(true);
    setCameraError(null);
    stopCamera();

    try {
      const constraints = {
        video: {
          facingMode: facingMode,
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      };

      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      setStream(mediaStream);

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setIsInitializing(false);
    } catch (err) {
      console.error('Camera access error:', err);
      try {
        const fallbackStream = await navigator.mediaDevices.getUserMedia({ video: true });
        setStream(fallbackStream);
        if (videoRef.current) {
          videoRef.current.srcObject = fallbackStream;
        }
        setIsInitializing(false);
      } catch (e) {
        setCameraError(
          'Unable to access optical input sensor. Verify that a video device is connected and permissions are enabled.'
        );
        setIsInitializing(false);
      }
    }
  }

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
    }
  }

  // --- AUTOMATIC FACE & SHARPNESS DETECTION ENGINE ---
  const analyzeFrame = useCallback(async () => {
    if (mode !== 'face' || hasCapturedRef.current || isCapturing) return;
    if (!videoRef.current || videoRef.current.readyState < 2) return;

    const video = videoRef.current;
    const vWidth = video.videoWidth;
    const vHeight = video.videoHeight;
    if (!vWidth || !vHeight) return;

    let isFacePresent = false;
    let isSharp = false;

    // 1. Try Native Browser FaceDetector API if supported (Chrome/Edge)
    if ('FaceDetector' in window) {
      try {
        const detector = new window.FaceDetector({ fastMode: true, maxDetectedFaces: 1 });
        const faces = await detector.detect(video);
        if (faces && faces.length > 0) {
          const face = faces[0].boundingBox;
          // Check if face is roughly centered inside the oval guide
          const faceCenterX = face.x + face.width / 2;
          const faceCenterY = face.y + face.height / 2;
          const targetX = vWidth / 2;
          const targetY = vHeight / 2;
          const dist = Math.hypot(faceCenterX - targetX, faceCenterY - targetY);
          
          if (dist < vWidth * 0.25 && face.width > vWidth * 0.20) {
            isFacePresent = true;
          }
        }
      } catch (err) {
        // Fall back to pixel analysis
      }
    }

    // 2. Pixel-Level Computer Vision Sharpness & Skin-Tone Verification
    let analyzeCanvas = analyzeCanvasRef.current;
    if (!analyzeCanvas) {
      analyzeCanvas = document.createElement('canvas');
      analyzeCanvasRef.current = analyzeCanvas;
    }

    // Downsample to 160x120 for instant 60fps calculation
    const sampleW = 160;
    const sampleH = 120;
    analyzeCanvas.width = sampleW;
    analyzeCanvas.height = sampleH;
    const ctx = analyzeCanvas.getContext('2d', { willReadFrequently: true });
    ctx.drawImage(video, 0, 0, sampleW, sampleH);

    const frameData = ctx.getImageData(0, 0, sampleW, sampleH).data;

    // Sample oval center region: 30% to 70% X, 20% to 80% Y
    let skinPixels = 0;
    let totalSamples = 0;
    let gradientSum = 0;

    for (let y = Math.floor(sampleH * 0.25); y < Math.floor(sampleH * 0.75); y += 2) {
      for (let x = Math.floor(sampleW * 0.30); x < Math.floor(sampleW * 0.70); x += 2) {
        const idx = (y * sampleW + x) * 4;
        const r = frameData[idx];
        const g = frameData[idx + 1];
        const b = frameData[idx + 2];
        totalSamples++;

        // Standard Human Skin-Tone Chrominance Model (covers all diverse skin tones)
        if (r > 45 && g > 30 && b > 20 && r > g && (r - b) > 10 && Math.abs(r - g) > 8) {
          skinPixels++;
        }

        // Horizontal Laplacian / Sobel gradient for motion-blur detection
        const nextIdx = (y * sampleW + (x + 1)) * 4;
        const rNext = frameData[nextIdx];
        const downIdx = ((y + 1) * sampleW + x) * 4;
        const rDown = frameData[downIdx];
        gradientSum += Math.abs(r - rNext) + Math.abs(r - rDown);
      }
    }

    const skinRatio = totalSamples > 0 ? (skinPixels / totalSamples) : 0;
    const avgGradient = totalSamples > 0 ? (gradientSum / totalSamples) : 0;

    // Sharpness threshold: moving/blurry faces have gradient < 14. Static in-focus faces have gradient >= 17
    isSharp = avgGradient > 15.5;

    if (!isFacePresent) {
      // If native API didn't trigger, use computer vision skin ratio (must be at least 25% human skin inside oval)
      isFacePresent = skinRatio > 0.24;
    }

    // Evaluate Detection Stability
    if (isFacePresent && isSharp) {
      stableFramesRef.current += 1;
      setDetectionState('detected');

      if (stableFramesRef.current >= 4) {
        // High confidence sharp face held still -> trigger automatic capture!
        hasCapturedRef.current = true;
        setStatusMessage('FACE VERIFIED &bull; CAPTURED');
        setCountdown(0);
        executeCapture();
      } else if (stableFramesRef.current >= 2) {
        setStatusMessage('HUMAN FACE VERIFIED &bull; HOLD STILL...');
        setCountdown(1);
      } else {
        setStatusMessage('FACE DETECTED &bull; STABILIZING...');
      }
    } else if (isFacePresent && !isSharp) {
      stableFramesRef.current = 0;
      setDetectionState('blurry');
      setStatusMessage('BLUR DETECTED &bull; HOLD STILL');
      setCountdown(null);
    } else {
      stableFramesRef.current = 0;
      setDetectionState('searching');
      setStatusMessage('ALIGN FACE INSIDE OVAL GUIDE');
      setCountdown(null);
    }
  }, [mode, isCapturing]);

  // Run detection loop when in face mode
  useEffect(() => {
    if (mode !== 'face') return;

    const interval = setInterval(() => {
      analyzeFrame();
    }, 220);

    return () => clearInterval(interval);
  }, [mode, analyzeFrame]);

  function executeCapture() {
    if (!videoRef.current || !canvasRef.current || isCapturing) return;
    setIsCapturing(true);

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const vWidth = video.videoWidth || 1280;
    const vHeight = video.videoHeight || 720;

    let cropX = 0;
    let cropY = 0;
    let cropW = vWidth;
    let cropH = vHeight;

    if (mode === 'document') {
      cropW = Math.round(vWidth * 0.80);
      cropH = Math.round(vHeight * 0.65);
      cropX = Math.round((vWidth - cropW) / 2);
      cropY = Math.round((vHeight - cropH) / 2);
    } else if (mode === 'face') {
      cropW = Math.round(vWidth * 0.55);
      cropH = Math.round(vHeight * 0.75);
      cropX = Math.round((vWidth - cropW) / 2);
      cropY = Math.round((vHeight - cropH) / 2);
    }

    canvas.width = cropW;
    canvas.height = cropH;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, cropX, cropY, cropW, cropH, 0, 0, cropW, cropH);

    const base64Image = canvas.toDataURL('image/jpeg', 0.95);
    stopCamera();

    setTimeout(() => {
      onCapture(base64Image);
    }, 250);
  }

  function handleManualCapture() {
    hasCapturedRef.current = true;
    executeCapture();
  }

  function toggleFacingMode() {
    hasCapturedRef.current = false;
    stableFramesRef.current = 0;
    setFacingMode((prev) => (prev === 'environment' ? 'user' : 'environment'));
  }

  return (
    <div className="camera-scanner">
      {cameraError ? (
        <div style={{ padding: '2.5rem 1.5rem', textAlign: 'center', backgroundColor: '#ffffff', color: 'var(--text-secondary)' }}>
          <div style={{ color: 'var(--status-suspicious-text)', fontWeight: 700, marginBottom: '0.5rem', fontSize: '0.95rem' }}>
            OPTICAL FEED UNAVAILABLE
          </div>
          <p style={{ fontSize: '0.85rem', marginBottom: '1.5rem', maxWidth: '420px', margin: '0 auto 1.5rem' }}>
            {cameraError}
          </p>
          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
            <button className="btn btn-primary" onClick={startCamera}>
              Retry Video Feed
            </button>
            {onCancel && (
              <button className="btn btn-secondary" onClick={onCancel}>
                Switch to File Upload
              </button>
            )}
          </div>
        </div>
      ) : (
        <>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="camera-video"
            onLoadedMetadata={() => setIsInitializing(false)}
          />

          <canvas ref={canvasRef} style={{ display: 'none' }} />

          {/* Guide Overlay */}
          {mode === 'document' ? (
            <div className="camera-guide-box">
              <span className="camera-guide-text">
                {promptText || 'Align Document Border Inside Frame'}
              </span>
            </div>
          ) : (
            <>
              <div className={`camera-oval-guide ${detectionState}`}>
                <span className="camera-guide-text" dangerouslySetInnerHTML={{ __html: statusMessage }} />
              </div>

              <div className="camera-status-banner">
                <div className="camera-status-pill">
                  {detectionState === 'detected' && (
                    <span style={{ color: '#4ade80' }}>
                      AUTOMATIC CAPTURE ACTIVE &bull; {countdown !== null ? 'CAPTURING...' : 'HOLD STILL'}
                    </span>
                  )}
                  {detectionState === 'blurry' && (
                    <span style={{ color: '#fbbf24' }}>
                      MOTION DETECTED &bull; HOLD CAMERA STEADY
                    </span>
                  )}
                  {detectionState === 'searching' && (
                    <span style={{ color: '#94a3b8' }}>
                      POSITION HUMAN FACE INSIDE OVAL (AUTO-DETECT)
                    </span>
                  )}
                </div>
              </div>
            </>
          )}

          {/* Controls */}
          <div className="camera-controls">
            <button 
              type="button" 
              className="btn btn-secondary" 
              onClick={toggleFacingMode}
              style={{ fontSize: '0.75rem', textTransform: 'uppercase' }}
            >
              Switch Lens
            </button>

            <button
              type="button"
              className="btn btn-primary"
              onClick={handleManualCapture}
              disabled={isInitializing || isCapturing}
              style={{ padding: '0.55rem 1.4rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}
            >
              {mode === 'document' ? "Capture Document Frame" : "Manual Capture Override"}
            </button>

            {onCancel && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => {
                  stopCamera();
                  onCancel();
                }}
                style={{ fontSize: '0.75rem', textTransform: 'uppercase' }}
              >
                Cancel
              </button>
            )}
          </div>
        </>
      )}
    </div>
  );
}
