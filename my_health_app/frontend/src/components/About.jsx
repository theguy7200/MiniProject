import React from 'react';

export default function About() {
  return (
    <section id="about" className="page-section active">
      <header className="section-header">
        <h2>About Aura Health</h2>
        <p>Bridging the gap in global healthcare access</p>
      </header>
      
      <div className="about-grid">
        <div className="glass-panel text-content" style={{ gridColumn: '1 / -1', marginBottom: '-1rem' }}>
          <h3><i className="fa-solid fa-earth-americas" style={{ color: 'var(--accent-blue)', marginRight: '10px' }}></i> Our Mission</h3>
          <p>In many rural and underserved areas globally, access to medical professionals is severely limited, leading to delayed diagnoses and preventable complications. Aura Health was created to democratize healthcare. By providing an accessible, instant, and highly accurate preliminary diagnosis tool, we empower individuals in remote regions to understand their health risks and seek urgent care when it truly matters.</p>
        </div>

        <div className="glass-panel text-content">
          <h3>Dataset & Features</h3>
          <p>The model was trained on a comprehensive, high-quality clinical dataset sourced from the <strong>UCI Machine Learning Repository</strong>. Multiple validated medical datasets were intelligently combined to ensure broad coverage across various demographics and disease profiles.</p>
          <p>It analyzes <strong>43 features</strong> encompassing base symptoms, targeted indicators (like cyclical chills), vital signs, lab tests, and engineered clinical ratios like Shock Index and NEWS2 severity score.</p>
        </div>
        
        <div className="glass-panel text-content">
          <h3>Model Architecture</h3>
          <p>We train three distinct models: Random Forest, Gradient Boosting, and Logistic Regression. The system automatically evaluates all three and deploys the highest-performing model.</p>
          <div className="metrics-list">
            <div className="metric-item">
              <span className="label">Disease Prediction</span>
              <span className="value text-blue">~87% Accuracy</span>
            </div>
            <div className="metric-item">
              <span className="label">Risk Level Prediction</span>
              <span className="value text-purple">~92% Accuracy</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
