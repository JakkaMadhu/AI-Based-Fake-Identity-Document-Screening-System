import React from 'react';

export function StatusBadge({ status }) {
  if (!status) return null;

  let badgeClass = 'badge-review';
  const sUpper = status.toUpperCase();
  if (sUpper.includes('REAL') || sUpper.includes('GENUINE')) badgeClass = 'badge-genuine';
  else if (sUpper.includes('FAKE') || sUpper.includes('FORGED') || sUpper.includes('SUSPICIOUS') || sUpper.includes('INVALID')) badgeClass = 'badge-suspicious';
  else if (sUpper.includes('REVIEW')) badgeClass = 'badge-review';

  return (
    <span className={`badge ${badgeClass}`}>
      {status}
    </span>
  );
}

export function RiskBadge({ riskLevel }) {
  if (!riskLevel) return null;

  let badgeClass = 'badge-review';
  if (riskLevel === 'Low Risk') badgeClass = 'badge-genuine';
  if (riskLevel === 'High Risk') badgeClass = 'badge-suspicious';

  return (
    <span className={`badge ${badgeClass}`}>
      {riskLevel}
    </span>
  );
}
