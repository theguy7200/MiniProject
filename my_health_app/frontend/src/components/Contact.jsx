import React from 'react';

export default function Contact() {
  return (
    <section id="contact" className="page-section active">
      <header className="section-header">
        <h2>Get in Touch</h2>
        <p>Have questions about Aura Health API integration?</p>
      </header>
      <div className="contact-grid">
        <div className="glass-panel contact-info">
          <div className="info-item">
            <i className="fa-solid fa-envelope"></i>
            <div>
              <h4>Email Support</h4>
              <p>api@aurahealth.ai</p>
            </div>
          </div>
          <div className="info-item">
            <i className="fa-solid fa-phone"></i>
            <div>
              <h4>Phone</h4>
              <p>+1 (800) 555-0199</p>
            </div>
          </div>
          <div className="info-item">
            <i className="fa-solid fa-location-dot"></i>
            <div>
              <h4>Headquarters</h4>
              <p>100 AI Avenue, Tech Park<br />San Francisco, CA 94107</p>
            </div>
          </div>
        </div>
        <div className="glass-panel">
          <form id="contact-form" onSubmit={(e) => e.preventDefault()}>
            <div className="input-group">
              <label>Name</label>
              <input type="text" placeholder="Your Name" />
            </div>
            <div className="input-group">
              <label>Email</label>
              <input type="email" placeholder="Your Email" />
            </div>
            <div className="input-group">
              <label>Message</label>
              <textarea rows="4" placeholder="How can we help?"></textarea>
            </div>
            <button type="button" className="primary-btn" onClick={() => alert('Message sent! We will get back to you shortly.')}>Send Message</button>
          </form>
        </div>
      </div>
    </section>
  );
}
