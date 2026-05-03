import React from 'react';

export default function Home({ onNavigate }) {
  return (
    <section id="home" className="page-section active">
      <div className="hero">
        <div className="hero-content">
          <div className="badge">Next-Gen Healthcare AI</div>
          <h1>Predict Diseases With <span>Clinical Precision</span></h1>
          <p>Aura Health harnesses the power of cutting-edge AI to deliver instant, clinic-grade disease predictions. By analyzing complex patterns in your vitals and symptoms, we empower you with actionable health insights in seconds.</p>
          <div className="hero-actions">
            <button className="primary-btn lg" onClick={() => onNavigate('predict')}>
              Start Prediction <i className="fa-solid fa-arrow-right"></i>
            </button>
            <button className="secondary-btn lg" onClick={() => onNavigate('about')}>
              Learn More
            </button>
          </div>
        </div>
        <div className="hero-visual">
          <div className="floating-card c1 glass-panel">
            <i className="fa-solid fa-microscope text-blue"></i>
            <h4>40 Clinical Features</h4>
          </div>
          <div className="floating-card c2 glass-panel">
            <i className="fa-solid fa-bullseye text-purple"></i>
            <h4>92% Risk Accuracy</h4>
          </div>
          <div className="floating-card c3 glass-panel">
            <i className="fa-solid fa-shield-virus text-green"></i>
            <h4>14 Diseases Tracked</h4>
          </div>
        </div>
      </div>

      <div className="how-it-works">
        <h2>How It Works</h2>
        <div className="steps-grid">
          <div className="step-card glass-panel">
            <div className="step-number">1</div>
            <h3>Input Data</h3>
            <p>Enter patient symptoms, vital signs, and lab reports into our secure form.</p>
          </div>
          <div className="step-card glass-panel">
            <div className="step-number">2</div>
            <h3>AI Analysis</h3>
            <p>Our Random Forest and Gradient Boosting models analyze the 40+ clinical indicators.</p>
          </div>
          <div className="step-card glass-panel">
            <div className="step-number">3</div>
            <h3>Get Results</h3>
            <p>Instantly view the predicted disease, confidence score, and NEWS2 severity rating.</p>
          </div>
        </div>
      </div>
    </section>
  );
}
