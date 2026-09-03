const API_BASE = '/api';

export async function uploadDocumentFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(errorData.detail || 'Failed to upload document');
  }

  return res.json();
}

export async function uploadLiveCapture(documentBase64, faceBase64 = null, filename = 'live_kyc_scan.jpg') {
  const res = await fetch(`${API_BASE}/documents/upload-live`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      document_base64: documentBase64,
      face_base64: faceBase64,
      image_base64: documentBase64,
      filename: filename
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Live capture upload failed' }));
    throw new Error(errorData.detail || 'Failed to register live camera snapshots');
  }

  return res.json();
}

export async function screenDocument(documentId) {
  const res = await fetch(`${API_BASE}/documents/${documentId}/screen`, {
    method: 'POST',
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Screening failed' }));
    throw new Error(errorData.detail || 'Document screening pipeline failed');
  }

  return res.json();
}

export async function getDocumentResult(documentId) {
  const res = await fetch(`${API_BASE}/documents/${documentId}/result`);

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Result not found' }));
    throw new Error(errorData.detail || 'Could not retrieve screening result');
  }

  return res.json();
}

export async function getHistory(params = {}) {
  const query = new URLSearchParams();
  if (params.search) query.append('search', params.search);
  if (params.status && params.status !== 'All') query.append('status', params.status);
  if (params.risk_level && params.risk_level !== 'All') query.append('risk_level', params.risk_level);
  if (params.page) query.append('page', params.page);
  if (params.page_size) query.append('page_size', params.page_size);

  const res = await fetch(`${API_BASE}/documents/history?${query.toString()}`);

  if (!res.ok) {
    throw new Error('Failed to fetch screening history');
  }

  return res.json();
}

export async function getDashboardStats() {
  const res = await fetch(`${API_BASE}/documents/stats`);

  if (!res.ok) {
    throw new Error('Failed to fetch dashboard statistics');
  }

  return res.json();
}

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
