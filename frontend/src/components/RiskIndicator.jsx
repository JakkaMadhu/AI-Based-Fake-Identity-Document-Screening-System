import React from 'react';

export function StatusBadge({ status }) {
  if (!status) return null;

  let badgeClass = 'badge-review';
  if (status === 'Likely Genuine') badgeClass = 'badge-genuine';
  if (status === 'Suspicious') badgeClass = 'badge-suspicious';

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
