document.addEventListener('DOMContentLoaded', () => {
    // --- SPA Navigation Logic ---
    const navButtons = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.page-section');

    window.switchTab = function(targetId) {
        // Update nav buttons
        navButtons.forEach(btn => {
            if(btn.dataset.target === targetId) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Update sections
        sections.forEach(sec => {
            if(sec.id === targetId) {
                sec.classList.add('active');
                if(targetId === 'history') loadHistory();
            } else {
                sec.classList.remove('active');
            }
        });
        
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.target));
    });

    // --- Prediction Logic ---
    const form = document.getElementById('prediction-form');
    const submitBtn = document.getElementById('submit-btn');
    const modal = document.getElementById('results-modal');
    const closeModalBtn = document.getElementById('close-modal');
    const resetBtn = document.getElementById('reset-btn');

    // UI Elements for results
    const riskBadge = document.getElementById('risk-badge');
    const resDisease = document.getElementById('res-disease');
    const resDConf = document.getElementById('res-d-conf');
    const resSeverity = document.getElementById('res-severity');
    const resRecommendation = document.getElementById('res-recommendation');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Form Validation - remove previous error states
        document.querySelectorAll('.input-error').forEach(el => el.classList.remove('input-error'));
        
        // Gather data
        const formData = new FormData(form);
        const payload = { symptoms: {}, vitals: {}, labs: {} };

        // Extract and parse
        for (let [key, value] of formData.entries()) {
            if (key.startsWith('symptom_')) {
                const symName = key.replace('symptom_', '');
                payload.symptoms[symName] = 1;
            } else if (key.startsWith('vital_')) {
                const vitName = key.replace('vital_', '');
                if (vitName === 'Consciousness') {
                    payload.vitals[vitName] = value;
                } else if (vitName === 'On_Oxygen') {
                    payload.vitals[vitName] = value === 'on' ? 1 : 0;
                } else {
                    if (value !== "") {
                        payload.vitals[vitName] = parseFloat(value);
                    }
                }
            } else if (key.startsWith('lab_')) {
                const labName = key.replace('lab_', '');
                if (value) payload.labs[labName] = parseFloat(value);
            }
        }

        if (!payload.vitals['On_Oxygen']) payload.vitals['On_Oxygen'] = 0;

        // UI Loading state
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (!response.ok) {
                // Formatting the validation error nicely if possible
                let errorMsg = 'Failed to get prediction';
                if(Array.isArray(result.detail)) {
                    errorMsg = result.detail.map(e => `${e.loc.join('.')} - ${e.msg}`).join(', ');
                } else if (result.detail) {
                    errorMsg = result.detail;
                }
                throw new Error(errorMsg);
            }

            displayResults(result.data);
            saveToHistory(result.data);

        } catch (error) {
            alert('Error: ' + error.message);
        } finally {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    });

    function displayResults(data) {
        const riskLevel = data.risk_level;
        if (riskLevel === "N/A") {
            riskBadge.textContent = "Risk N/A";
            riskBadge.className = 'risk-badge';
            riskBadge.style.background = 'rgba(255, 255, 255, 0.1)';
            riskBadge.style.color = '#cbd5e1';
        } else {
            riskBadge.style.background = '';
            riskBadge.style.color = '';
            riskBadge.textContent = riskLevel + " Risk";
            riskBadge.className = 'risk-badge';
            
            if (riskLevel.includes('Low')) riskBadge.classList.add('risk-Low');
            else if (riskLevel.includes('Moderate')) riskBadge.classList.add('risk-Moderate');
            else if (riskLevel.includes('High')) riskBadge.classList.add('risk-High');
            else if (riskLevel.includes('Critical')) riskBadge.classList.add('risk-Critical');
            else riskBadge.classList.add('risk-Moderate');
        }

        resDisease.textContent = data.disease.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        if (data.disease_confidence) {
            resDConf.textContent = (parseFloat(data.disease_confidence) * 100).toFixed(1) + "%";
        } else {
            resDConf.textContent = "N/A";
        }
        
        resSeverity.textContent = data.severity_score;
        if (data.recommendation) {
            resRecommendation.textContent = data.recommendation;
        } else {
            resRecommendation.textContent = "Please consult a healthcare professional.";
        }
        modal.classList.remove('hidden');
    }

    function closeModal() { modal.classList.add('hidden'); }
    closeModalBtn.addEventListener('click', closeModal);
    resetBtn.addEventListener('click', () => {
        closeModal();
        form.reset();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // --- History Logic ---
    function saveToHistory(data) {
        let history = JSON.parse(localStorage.getItem('auraHistory') || '[]');
        
        const record = {
            id: Date.now(),
            date: new Date().toLocaleString(),
            disease: data.disease.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            confidence: data.disease_confidence ? (parseFloat(data.disease_confidence) * 100).toFixed(1) + "%" : "N/A",
            risk: data.risk_level,
            severity: data.severity_score
        };
        
        history.unshift(record); // add to top
        if(history.length > 50) history.pop(); // keep last 50
        
        localStorage.setItem('auraHistory', JSON.stringify(history));
    }

    function loadHistory() {
        const tbody = document.getElementById('history-body');
        const emptyMsg = document.getElementById('no-history-msg');
        const table = document.querySelector('.history-table');
        
        let history = JSON.parse(localStorage.getItem('auraHistory') || '[]');
        
        tbody.innerHTML = '';
        
        if(history.length === 0) {
            emptyMsg.classList.remove('hidden');
            table.style.display = 'none';
            return;
        }
        
        emptyMsg.classList.add('hidden');
        table.style.display = 'table';
        
        history.forEach(item => {
            const tr = document.createElement('tr');
            
            // Risk color class
            let riskClass = 'text-blue';
            let riskText = item.risk + " Risk";
            if(item.risk === 'N/A') {
                riskClass = '';
                riskText = 'N/A';
            } else {
                if(item.risk.includes('Low')) riskClass = 'text-green';
                if(item.risk.includes('High') || item.risk.includes('Critical')) riskClass = 'text-red'; // using custom inline or default red
                if(item.risk.includes('Moderate')) riskClass = 'text-purple';
            }

            tr.innerHTML = `
                <td>${item.date}</td>
                <td style="font-weight:600">${item.disease}</td>
                <td>${item.confidence}</td>
                <td class="${riskClass}" style="font-weight:600">${riskText}</td>
                <td>${item.severity}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    document.getElementById('clear-history-btn').addEventListener('click', () => {
        if(confirm('Are you sure you want to clear all patient history from your browser?')) {
            localStorage.removeItem('auraHistory');
            loadHistory();
        }
    });
});
