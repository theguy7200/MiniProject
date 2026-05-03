import React from 'react';

export default function ResultModal({ data, onClose }) {
  const getRiskClass = (risk) => {
    if (!risk) return '';
    if (risk.includes('Low')) return 'risk-Low';
    if (risk.includes('Moderate')) return 'risk-Moderate';
    if (risk.includes('High')) return 'risk-High';
    if (risk.includes('Critical')) return 'risk-Critical';
    return '';
  };

  const confidenceText = data.disease_confidence 
    ? (parseFloat(data.disease_confidence) * 100).toFixed(1) + "%" 
    : "N/A";

  const diseaseText = data.disease.replace(/_/g, ' ');

  return (
    <div id="results-modal" className="modal-overlay" style={{ display: 'flex' }} onClick={onClose}>
      <div className="modal-content glass-panel" onClick={e => e.stopPropagation()}>
        <button id="close-modal" className="close-btn" onClick={onClose}>
          <i className="fa-solid fa-xmark"></i>
        </button>
        <div className="results-header">
          <h2>Prediction Results</h2>
          <div id="risk-badge" className={`risk-badge ${getRiskClass(data.risk_level)}`}>
            {data.risk_level} Risk
          </div>
        </div>
        
        <div className="results-body">
          <div className="result-card disease-card">
            <div className="icon-wrap"><i className="fa-solid fa-virus-covid"></i></div>
            <div className="info">
              <p className="label">Predicted Condition</p>
              <h3 id="res-disease">{diseaseText}</h3>
              <p className="confidence">Confidence: <span id="res-d-conf">{confidenceText}</span></p>
            </div>
          </div>
          
          <div className="result-card severity-card">
            <div className="icon-wrap"><i className="fa-solid fa-triangle-exclamation"></i></div>
            <div className="info">
              <p className="label">Severity Score</p>
              <h3 id="res-severity">{data.severity_score}</h3>
              <p className="confidence">Out of 20 (NEWS2 Based)</p>
            </div>
          </div>

          <div className="result-card recommendation-card">
            <div className="icon-wrap"><i className="fa-solid fa-user-doctor"></i></div>
            <div className="info">
              <p className="label">Doctor Visit Recommendation</p>
              <p id="res-recommendation" style={{ fontWeight: 500, fontSize: '1.1rem', color: '#f8fafc', marginTop: '0.3rem' }}>
                {data.recommendation}
              </p>
            </div>
          </div>
        </div>
        
        <div className="action-bar">
          <button id="reset-btn" className="secondary-btn" onClick={onClose}>New Patient</button>
        </div>
      </div>
    </div>
  );
}
