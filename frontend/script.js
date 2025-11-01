// Navigation and Smooth Scrolling
document.addEventListener('DOMContentLoaded', function() {
    // Navigation link handling
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));

            // Add active class to clicked link
            this.classList.add('active');

            // Smooth scroll to section
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);

            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Mobile menu toggle
    const mobileToggle = document.querySelector('.mobile-toggle');
    const navMenu = document.querySelector('.nav-menu');

    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }

    // Filter buttons
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            filterButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            const filter = this.getAttribute('data-filter');
            filterPatients(filter);
        });
    });

    // Patient search
    const patientSearch = document.getElementById('patientSearch');
    if (patientSearch) {
        patientSearch.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            filterPatientsBySearch(searchTerm);
        });
    }
});

// Scroll to section helper
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// Form Reset
function resetForm() {
    document.getElementById('patientName').value = '';
    document.getElementById('patientAge').value = '';
    document.getElementById('patientGender').value = '';
    document.getElementById('creatinine').value = '';
    document.getElementById('bun').value = '';
    document.getElementById('gfr').value = '';
    document.getElementById('urineOutput').value = '';
    document.getElementById('diabetes').checked = false;
    document.getElementById('hypertension').checked = false;
}

// Make Prediction
async function makePrediction() {
    // Get form values
    const patientData = {
        name: document.getElementById('patientName').value,
        age: parseFloat(document.getElementById('patientAge').value),
        gender: document.getElementById('patientGender').value,
        creatinine: parseFloat(document.getElementById('creatinine').value),
        bun: parseFloat(document.getElementById('bun').value),
        gfr: parseFloat(document.getElementById('gfr').value),
        urineOutput: parseFloat(document.getElementById('urineOutput').value),
        diabetes: document.getElementById('diabetes').checked ? 1 : 0,
        hypertension: document.getElementById('hypertension').checked ? 1 : 0
    };

    // Validate form
    if (!validateForm(patientData)) {
        alert('Please fill in all required fields with valid values.');
        return;
    }

    // Show loading state
    const predictBtn = event.target;
    const originalText = predictBtn.innerHTML;
    predictBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    predictBtn.disabled = true;

    try {
        // Simulate API call (replace with actual API call when backend is ready)
        const prediction = await simulatePrediction(patientData);

        // Display results
        displayResults(prediction, patientData);

        // Scroll to results
        document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error('Prediction error:', error);
        alert('An error occurred during prediction. Please try again.');
    } finally {
        predictBtn.innerHTML = originalText;
        predictBtn.disabled = false;
    }
}

// Validate Form
function validateForm(data) {
    if (!data.name || !data.age || !data.gender) return false;
    if (!data.creatinine || !data.bun || !data.gfr || !data.urineOutput) return false;
    if (data.age < 18 || data.age > 120) return false;
    if (data.creatinine < 0 || data.bun < 0 || data.gfr < 0 || data.urineOutput < 0) return false;
    return true;
}

// Simulate Prediction (Replace with actual API call)
async function simulatePrediction(data) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Simple rule-based prediction for demo
    // In production, this will call your FastAPI backend
    let riskScore = 0;

    // GFR is the most important feature (60.17%)
    if (data.gfr < 30) riskScore += 0.60;
    else if (data.gfr < 60) riskScore += 0.30;
    else riskScore += 0.05;

    // BUN (23.52%)
    if (data.bun > 40) riskScore += 0.20;
    else if (data.bun > 20) riskScore += 0.10;
    else riskScore += 0.02;

    // Creatinine (12.91%)
    if (data.creatinine > 2.0) riskScore += 0.12;
    else if (data.creatinine > 1.3) riskScore += 0.06;
    else riskScore += 0.01;

    // Other factors
    if (data.urineOutput < 800) riskScore += 0.02;
    if (data.diabetes) riskScore += 0.01;
    if (data.hypertension) riskScore += 0.01;
    if (data.age > 60) riskScore += 0.01;

    // Normalize to 0-1 range
    riskScore = Math.min(riskScore, 1);

    return {
        ckdStatus: riskScore > 0.5 ? 1 : 0,
        riskScore: riskScore,
        confidence: riskScore > 0.5 ? riskScore * 100 : (1 - riskScore) * 100,
        features: {
            gfr: data.gfr,
            bun: data.bun,
            creatinine: data.creatinine,
            urineOutput: data.urineOutput,
            age: data.age,
            diabetes: data.diabetes,
            hypertension: data.hypertension
        }
    };
}

// Display Results
function displayResults(prediction, patientData) {
    // Show results section
    document.getElementById('results').style.display = 'block';

    // Hide prediction section
    // document.getElementById('predict').style.display = 'none';

    // Update result status
    const resultIcon = document.getElementById('resultIcon');
    const resultTitle = document.getElementById('resultTitle');
    const resultStatus = document.getElementById('resultStatus');

    if (prediction.ckdStatus === 1) {
        resultIcon.className = 'result-icon positive';
        resultIcon.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
        resultStatus.textContent = 'CKD Detected';
        resultStatus.style.color = 'var(--danger-color)';
    } else {
        resultIcon.className = 'result-icon negative';
        resultIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
        resultStatus.textContent = 'No CKD Detected';
        resultStatus.style.color = 'var(--success-color)';
    }

    // Update confidence
    const confidenceValue = document.getElementById('confidenceValue');
    const confidenceFill = document.getElementById('confidenceFill');
    confidenceValue.textContent = prediction.confidence.toFixed(1);
    confidenceFill.style.width = prediction.confidence + '%';

    // Update risk assessment
    updateRiskAssessment(prediction.riskScore);

    // Update feature importance
    updateFeatureImportance(prediction.features);

    // Update patient summary
    updatePatientSummary(patientData, prediction);

    // Update recommendations
    updateRecommendations(prediction, patientData);
}

// Update Risk Assessment
function updateRiskAssessment(riskScore) {
    const riskIndicator = document.getElementById('riskIndicator');
    const riskLabel = document.getElementById('riskLabel');
    const riskDescription = document.getElementById('riskDescription');

    // Position indicator (0-100%)
    riskIndicator.style.left = (riskScore * 100) + '%';

    // Determine risk level
    let level, description;
    if (riskScore < 0.3) {
        level = 'Low Risk';
        description = 'Patient shows minimal indicators of kidney disease. Continue regular monitoring.';
    } else if (riskScore < 0.6) {
        level = 'Moderate Risk';
        description = 'Patient shows some indicators of kidney disease. Increased monitoring recommended.';
    } else {
        level = 'High Risk';
        description = 'Patient shows significant indicators of kidney disease. Immediate medical attention recommended.';
    }

    riskLabel.textContent = level;
    riskDescription.textContent = description;
}

// Update Feature Importance
function updateFeatureImportance(features) {
    const featureBars = document.getElementById('featureBars');

    const featureImportance = [
        { name: 'GFR', value: features.gfr, normal: '60-120', weight: 60.17 },
        { name: 'BUN', value: features.bun, normal: '7-20', weight: 23.52 },
        { name: 'Creatinine', value: features.creatinine, normal: '0.7-1.3', weight: 12.91 },
        { name: 'Urine Output', value: features.urineOutput, normal: '800-2000', weight: 1.88 },
        { name: 'Age', value: features.age, normal: '18-120', weight: 1.22 }
    ];

    featureBars.innerHTML = featureImportance.map(feature => `
        <div class="feature-item">
            <span class="feature-name">${feature.name}</span>
            <div class="feature-bar">
                <div class="feature-bar-fill" style="width: ${feature.weight}%"></div>
            </div>
            <span class="feature-value">${feature.value.toFixed(1)}</span>
        </div>
    `).join('');
}

// Update Patient Summary
function updatePatientSummary(patientData, prediction) {
    const summaryGrid = document.getElementById('patientSummary');

    summaryGrid.innerHTML = `
        <div class="summary-item">
            <div class="summary-label">Patient Name</div>
            <div class="summary-value">${patientData.name}</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">Age</div>
            <div class="summary-value">${patientData.age} years</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">Gender</div>
            <div class="summary-value">${patientData.gender}</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">Creatinine Level</div>
            <div class="summary-value">${patientData.creatinine} mg/dL</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">BUN Level</div>
            <div class="summary-value">${patientData.bun} mg/dL</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">GFR Value</div>
            <div class="summary-value">${patientData.gfr} mL/min</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">Urine Output</div>
            <div class="summary-value">${patientData.urineOutput} mL/day</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">Diabetes</div>
            <div class="summary-value">${patientData.diabetes ? 'Yes' : 'No'}</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">Hypertension</div>
            <div class="summary-value">${patientData.hypertension ? 'Yes' : 'No'}</div>
        </div>
    `;
}

// Update Recommendations
function updateRecommendations(prediction, patientData) {
    const recommendationsList = document.getElementById('recommendationsList');
    const recommendations = [];

    if (prediction.ckdStatus === 1) {
        recommendations.push('Immediate consultation with a nephrologist is strongly recommended.');

        if (patientData.gfr < 30) {
            recommendations.push('GFR is critically low. Patient may require dialysis preparation.');
        } else if (patientData.gfr < 60) {
            recommendations.push('GFR indicates Stage 3 CKD or higher. Close monitoring required.');
        }

        if (patientData.bun > 40) {
            recommendations.push('Elevated BUN levels suggest reduced kidney function. Dietary modifications recommended.');
        }

        if (patientData.creatinine > 2.0) {
            recommendations.push('High creatinine levels detected. Further diagnostic tests recommended.');
        }

        if (patientData.diabetes) {
            recommendations.push('Strict blood sugar control is essential to prevent further kidney damage.');
        }

        if (patientData.hypertension) {
            recommendations.push('Blood pressure management is critical for kidney health.');
        }
    } else {
        recommendations.push('No immediate kidney disease detected. Continue regular health monitoring.');
        recommendations.push('Maintain a healthy diet low in sodium and processed foods.');
        recommendations.push('Stay well-hydrated and exercise regularly.');

        if (patientData.diabetes || patientData.hypertension) {
            recommendations.push('Continue managing existing conditions to prevent future kidney complications.');
        }
    }

    recommendationsList.innerHTML = recommendations.map(rec => `
        <div class="recommendation-item">
            <strong><i class="fas fa-check-circle"></i></strong> ${rec}
        </div>
    `).join('');
}

// Hide Results and Show Form
function hideResults() {
    document.getElementById('results').style.display = 'none';
    document.getElementById('predict').scrollIntoView({ behavior: 'smooth' });
}

// Download Report (Placeholder)
function downloadReport() {
    alert('Download report functionality will be implemented with the backend API.');
    // In production, this would generate a PDF report
}

// Save to Database (Placeholder)
async function saveToDatabase() {
    const saveBtn = event.target;
    const originalText = saveBtn.innerHTML;
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    saveBtn.disabled = true;

    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));

        alert('Prediction saved successfully to database!');
        // In production, this would call your FastAPI POST /diagnoses endpoint
    } catch (error) {
        console.error('Save error:', error);
        alert('Failed to save prediction. Please try again.');
    } finally {
        saveBtn.innerHTML = originalText;
        saveBtn.disabled = false;
    }
}

// Filter Patients
function filterPatients(filter) {
    const rows = document.querySelectorAll('#patientsTableBody tr');

    rows.forEach(row => {
        const status = row.querySelector('.badge');
        const riskScore = row.querySelector('.risk-score');

        if (filter === 'all') {
            row.style.display = '';
        } else if (filter === 'ckd' && status.classList.contains('badge-danger')) {
            row.style.display = '';
        } else if (filter === 'no-ckd' && status.classList.contains('badge-success')) {
            row.style.display = '';
        } else if (filter === 'high-risk' && riskScore.classList.contains('high')) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Filter Patients by Search
function filterPatientsBySearch(searchTerm) {
    const rows = document.querySelectorAll('#patientsTableBody tr');

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

// API Integration Functions (To be implemented when backend is ready)

// Fetch latest patient data from API
async function fetchLatestPatient() {
    try {
        const response = await fetch('/api/patients/latest');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching patient data:', error);
        throw error;
    }
}

// Make prediction via API
async function predictViaAPI(patientData) {
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(patientData)
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error making prediction:', error);
        throw error;
    }
}

// Save diagnosis to database via API
async function saveDiagnosisAPI(diagnosisData) {
    try {
        const response = await fetch('/api/diagnoses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(diagnosisData)
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error saving diagnosis:', error);
        throw error;
    }
}

// Fetch all patients from API
async function fetchAllPatients() {
    try {
        const response = await fetch('/api/patients');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching patients:', error);
        throw error;
    }
}

// Animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
        }
    });
}, observerOptions);

// Observe sections
document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        observer.observe(section);
    });
});

// Add smooth reveal animations to cards
window.addEventListener('load', function() {
    const cards = document.querySelectorAll('.form-card, .result-card, .dashboard-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'all 0.6s ease-out';

            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100);
        }, index * 100);
    });
});
