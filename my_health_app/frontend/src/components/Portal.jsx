import React from 'react';

export default function Portal() {
  return (
    <section id="portal" className="page-section active">
      <div className="auth-container glass-panel">
        <div className="auth-icon"><i className="fa-solid fa-user-doctor"></i></div>
        <h2>Doctor Portal Login</h2>
        <p>Access advanced analytics and patient records.</p>
        <form id="login-form" onSubmit={(e) => e.preventDefault()}>
          <div className="input-group">
            <label>Medical ID / Email</label>
            <input type="text" placeholder="dr.smith@hospital.com" required />
          </div>
          <div className="input-group">
            <label>Password</label>
            <input type="password" placeholder="••••••••" required />
          </div>
          <button type="button" className="primary-btn full-width" onClick={() => alert('Mock Login: In a real app, this would authenticate against a database.')}>Secure Login <i className="fa-solid fa-lock"></i></button>
        </form>
      </div>
    </section>
  );
}
