import React, { useState } from 'react';

const SYMPTOMS = [
  { name: 'symptom_fever', label: 'Fever' },
  { name: 'symptom_headache', label: 'Headache' },
  { name: 'symptom_nausea', label: 'Nausea' },
  { name: 'symptom_vomiting', label: 'Vomiting' },
  { name: 'symptom_fatigue', label: 'Fatigue' },
  { name: 'symptom_joint_pain', label: 'Joint Pain' },
  { name: 'symptom_skin_rash', label: 'Skin Rash' },
  { name: 'symptom_cough', label: 'Cough' },
  { name: 'symptom_weight_loss', label: 'Weight Loss' },
  { name: 'symptom_yellow_eyes', label: 'Yellow Eyes' }
];

const TARGETED = [
  { name: 'symptom_chills_cyclical', label: 'Cyclical Chills' },
  { name: 'symptom_night_sweats', label: 'Night Sweats' },
  { name: 'symptom_dark_urine', label: 'Dark Urine' },
  { name: 'symptom_positional_dizziness', label: 'Dizziness' },
  { name: 'symptom_sudden_weakness', label: 'Sudden Weakness' },
  { name: 'symptom_neck_stiffness', label: 'Neck Stiffness' },
  { name: 'symptom_frequent_urination', label: 'Frequent Urination' },
  { name: 'symptom_shortness_of_breath', label: 'Shortness of Breath' },
  { name: 'symptom_retro_orbital_pain', label: 'Pain Behind Eyes' }
];

export default function PredictionForm({ onSuccess }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const formData = new FormData(e.target);
    const payload = { symptoms: {}, vitals: {}, labs: {} };
    
    // Map symptoms
    [...SYMPTOMS, ...TARGETED].forEach(s => {
      if (formData.get(s.name)) {
        payload.symptoms[s.name.replace('symptom_', '')] = 1;
      }
    });

    // Map vitals
    const vitalsMap = {
      vital_Heart_Rate: 'Heart_Rate',
      vital_Systolic_BP: 'Systolic_BP',
      vital_Respiratory_Rate: 'Respiratory_Rate',
      vital_Oxygen_Saturation: 'Oxygen_Saturation',
      vital_Temperature: 'Temperature',
      vital_O2_Scale: 'O2_Scale',
      vital_On_Oxygen: 'On_Oxygen',
      vital_Consciousness: 'Consciousness'
    };

    Object.entries(vitalsMap).forEach(([formKey, apiKey]) => {
      const val = formData.get(formKey);
      if (apiKey === 'Consciousness') {
        payload.vitals[apiKey] = val || 'A';
      } else if (apiKey === 'On_Oxygen') {
        payload.vitals[apiKey] = val ? 1 : 0;
      } else {
        if (val) payload.vitals[apiKey] = parseFloat(val);
      }
    });

    // Map labs
    const labsMap = {
      lab_ALT_UL: 'ALT_UL',
      lab_WBC_K_uL: 'WBC_K_uL',
      lab_TSH_mIUL: 'TSH_mIUL'
    };

    Object.entries(labsMap).forEach(([formKey, apiKey]) => {
      const val = formData.get(formKey);
      if (val) payload.labs[apiKey] = parseFloat(val);
    });

    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Prediction failed');
      onSuccess(data.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section id="predict" className="page-section active" style={{ padding: 0 }}>
      <header className="section-header">
        <h2>Clinical Assessment Form</h2>
        <p>Fill out the patient details below to generate an AI prediction.</p>
      </header>

      <form id="prediction-form" className="glass-panel" onSubmit={handleSubmit}>
        <div className="form-grid">
          <section className="form-section symptoms-section">
            <h2><i className="fa-solid fa-head-side-cough"></i> Symptoms</h2>
            <p className="section-desc">Select all that apply</p>
            
            <div className="checkbox-grid">
              {SYMPTOMS.map(s => (
                <label key={s.name} className="custom-checkbox">
                  <input type="checkbox" name={s.name} /> 
                  <span className="checkmark"></span> {s.label}
                </label>
              ))}
              
              {TARGETED.map(s => (
                <label key={s.name} className="custom-checkbox targeted">
                  <input type="checkbox" name={s.name} /> 
                  <span className="checkmark"></span> {s.label}
                </label>
              ))}
            </div>
          </section>

          <section className="form-section vitals-section">
            <h2><i className="fa-solid fa-stethoscope"></i> Vitals <span className="optional-badge">Optional</span></h2>
            <div className="input-grid">
              <div className="input-group">
                <label>Heart Rate (bpm)</label>
                <input type="number" name="vital_Heart_Rate" placeholder="e.g. 80" />
              </div>
              <div className="input-group">
                <label>Systolic BP (mmHg)</label>
                <input type="number" name="vital_Systolic_BP" placeholder="e.g. 120" />
              </div>
              <div className="input-group">
                <label>Respiratory Rate</label>
                <input type="number" name="vital_Respiratory_Rate" placeholder="e.g. 18" />
              </div>
              <div className="input-group">
                <label>Oxygen Saturation (%)</label>
                <input type="number" name="vital_Oxygen_Saturation" placeholder="e.g. 98" />
              </div>
              <div className="input-group">
                <label>Temperature (°C)</label>
                <input type="number" step="0.1" name="vital_Temperature" placeholder="e.g. 37.0" />
              </div>
              <div className="input-group">
                <label>O2 Scale</label>
                <input type="number" step="0.1" name="vital_O2_Scale" placeholder="e.g. 1.0" defaultValue="1.0" />
              </div>
              
              <div className="input-group full-width toggle-group">
                <label>Patient on Oxygen?</label>
                <label className="switch">
                  <input type="checkbox" name="vital_On_Oxygen" />
                  <span className="slider round"></span>
                </label>
              </div>

              <div className="input-group full-width">
                <label>Consciousness Level (AVPU)</label>
                <select name="vital_Consciousness">
                  <option value="A">A - Alert</option>
                  <option value="C">C - Confusion (New)</option>
                  <option value="V">V - Voice Responsive</option>
                  <option value="P">P - Pain Responsive</option>
                  <option value="U">U - Unresponsive</option>
                </select>
              </div>
            </div>
          </section>

          <section className="form-section labs-section">
            <h2><i className="fa-solid fa-vial"></i> Lab Tests <span className="optional-badge">Optional</span></h2>
            <div className="input-grid">
              <div className="input-group">
                <label>ALT (U/L) - Liver</label>
                <input type="number" step="0.1" name="lab_ALT_UL" placeholder="e.g. 25.0" />
              </div>
              <div className="input-group">
                <label>WBC (K/uL) - Immunity</label>
                <input type="number" step="0.1" name="lab_WBC_K_uL" placeholder="e.g. 8.0" />
              </div>
              <div className="input-group">
                <label>TSH (mIU/L) - Thyroid</label>
                <input type="number" step="0.1" name="lab_TSH_mIUL" placeholder="e.g. 2.1" />
              </div>
            </div>
          </section>
        </div>

        <div className="form-footer">
          <button type="submit" id="submit-btn" className="primary-btn" disabled={loading}>
            <span className="btn-text">{loading ? 'Processing...' : 'Generate Health Prediction'}</span>
            <i className="fa-solid fa-wand-magic-sparkles"></i>
            {loading && <div className="spinner" style={{ display: 'block' }}></div>}
          </button>
        </div>
        {error && <p style={{ color: 'var(--risk-high)', marginTop: '1rem', textAlign: 'center' }}>{error}</p>}
      </form>
    </section>
  );
}
