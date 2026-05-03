import React, { useState, useEffect } from 'react';

export default function PatientHistory() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const data = JSON.parse(localStorage.getItem('auraHistory') || '[]');
    setHistory(data);
  }, []);

  const clearHistory = () => {
    if (window.confirm('Clear all history?')) {
      localStorage.removeItem('auraHistory');
      setHistory([]);
    }
  };

  const getRiskClass = (risk) => {
    if (!risk) return '';
    if (risk.includes('Low')) return 'text-green';
    if (risk.includes('High') || risk.includes('Critical')) return 'text-red';
    if (risk.includes('Moderate')) return 'text-purple';
    return '';
  };

  return (
    <section id="history" className="page-section active" style={{ padding: 0 }}>
      <header className="section-header">
        <h2>Patient History Dashboard</h2>
        <p>Locally saved prediction results for quick reference.</p>
      </header>
      
      <div className="glass-panel">
        <div className="history-controls">
          <button id="clear-history-btn" className="danger-btn" onClick={clearHistory}>
            <i className="fa-solid fa-trash"></i> Clear History
          </button>
        </div>
        <div className="table-container">
          <table className="history-table">
            <thead>
              <tr>
                <th>Date & Time</th>
                <th>Predicted Disease</th>
                <th>Confidence</th>
                <th>Risk Level</th>
                <th>Severity Score</th>
              </tr>
            </thead>
            <tbody>
              {history.map(item => (
                <tr key={item.id}>
                  <td>{item.date}</td>
                  <td style={{ fontWeight: 600 }}>{item.disease}</td>
                  <td>{item.confidence}</td>
                  <td className={getRiskClass(item.risk)} style={{ fontWeight: 600 }}>
                    {item.risk}
                  </td>
                  <td>{item.severity}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {history.length === 0 && (
            <div id="no-history-msg" className="empty-state" style={{ display: 'flex' }}>
              <i className="fa-solid fa-folder-open"></i>
              <p>No patient history found. Run a prediction to see it here.</p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
