import React, { useState } from 'react';
import Home from './components/Home';
import About from './components/About';
import Portal from './components/Portal';
import Contact from './components/Contact';
import PredictionForm from './components/PredictionForm';
import PatientHistory from './components/PatientHistory';
import ResultModal from './components/ResultModal';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [modalData, setModalData] = useState(null);

  const handlePredictionSuccess = (data) => {
    setModalData(data);
    saveToHistory(data);
  };

  const saveToHistory = (data) => {
    const history = JSON.parse(localStorage.getItem('auraHistory') || '[]');
    const record = {
      id: Date.now(),
      date: new Date().toLocaleString(),
      disease: data.disease.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      confidence: data.disease_confidence ? (parseFloat(data.disease_confidence) * 100).toFixed(1) + "%" : "N/A",
      risk: data.risk_level,
      severity: data.severity_score
    };
    history.unshift(record);
    if(history.length > 50) history.pop();
    localStorage.setItem('auraHistory', JSON.stringify(history));
  };

  return (
    <>
      <div className="background-mesh">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
        <div className="blob blob-3"></div>
      </div>

      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-logo" onClick={() => setActiveTab('home')}>
            <i className="fa-solid fa-heart-pulse"></i>
            <span>Aura Health</span>
          </div>
          <div className="nav-links">
            <button className={`nav-btn ${activeTab === 'home' ? 'active' : ''}`} onClick={() => setActiveTab('home')}>Home</button>
            <button className={`nav-btn ${activeTab === 'predict' ? 'active' : ''}`} onClick={() => setActiveTab('predict')}>Predict</button>
            <button className={`nav-btn ${activeTab === 'history' ? 'active' : ''}`} onClick={() => setActiveTab('history')}>History</button>
            <button className={`nav-btn ${activeTab === 'about' ? 'active' : ''}`} onClick={() => setActiveTab('about')}>About</button>
            <button className={`nav-btn ${activeTab === 'portal' ? 'active' : ''}`} onClick={() => setActiveTab('portal')}>Doctor Portal</button>
            <button className={`nav-btn ${activeTab === 'contact' ? 'active' : ''}`} onClick={() => setActiveTab('contact')}>Contact</button>
          </div>
          <div className="mobile-menu-btn">
            <i className="fa-solid fa-bars"></i>
          </div>
        </div>
      </nav>

      <main className="container">
        {activeTab === 'home' && <Home onNavigate={setActiveTab} />}
        {activeTab === 'predict' && <PredictionForm onSuccess={handlePredictionSuccess} />}
        {activeTab === 'history' && <PatientHistory />}
        {activeTab === 'about' && <About />}
        {activeTab === 'portal' && <Portal />}
        {activeTab === 'contact' && <Contact />}
      </main>

      <footer>
        <div className="footer-content">
          <div className="logo">
            <i className="fa-solid fa-heart-pulse"></i>
            <h2>Aura Health</h2>
          </div>
          <p>&copy; 2026 Aura Health AI. All rights reserved.</p>
        </div>
      </footer>

      {modalData && (
        <ResultModal data={modalData} onClose={() => setModalData(null)} />
      )}
    </>
  );
}

export default App;
