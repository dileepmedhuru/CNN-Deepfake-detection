// Initialize results page
async function initResultsPage() {
    const session = await protectPage();
    if (!session) return;
    
    document.getElementById('user-name').textContent = session.user_name;
    
    // Get detection data from localStorage
    const detectionData = localStorage.getItem('latestDetection');
    
    if (detectionData) {
        const detection = JSON.parse(detectionData);
        displayResults(detection);
        localStorage.removeItem('latestDetection');
    } else {
        // No data, redirect to upload
        window.location.href = '/upload.html';
    }
}

// Display detection results
function displayResults(detection) {
    const loadingState = document.getElementById('loading-state');
    const resultsContent = document.getElementById('results-content');
    
    // Hide loading, show results
    loadingState.style.display = 'none';
    resultsContent.style.display = 'block';
    
    // Prediction result
    const predictionResult = document.getElementById('prediction-result');
    const isFake = detection.prediction === 'fake';
    
    predictionResult.innerHTML = `
        <div class="prediction-badge ${isFake ? 'fake' : 'real'}">
            <i class="fas fa-${isFake ? 'exclamation-triangle' : 'check-circle'}"></i>
            <h2>${isFake ? 'DEEPFAKE DETECTED' : 'AUTHENTIC MEDIA'}</h2>
            <p>${isFake ? 'This file appears to be AI-generated or manipulated' : 'This file appears to be genuine and unmanipulated'}</p>
        </div>
    `;
    
    // Confidence score
    const confidence = detection.confidence || 0;
    const confidenceFill = document.getElementById('confidence-fill');
    const confidenceText = document.getElementById('confidence-text');
    
    confidenceFill.style.width = confidence + '%';
    confidenceFill.className = 'confidence-fill ' + (isFake ? 'red' : 'green');
    confidenceText.textContent = confidence.toFixed(2);
    
    // File details
    document.getElementById('detail-filename').textContent = detection.file_name;
    document.getElementById('detail-type').textContent = detection.file_type.toUpperCase();
    document.getElementById('detail-time').textContent = detection.processing_time ? 
        detection.processing_time.toFixed(2) + 's' : '-';
    document.getElementById('detail-date').textContent = new Date(detection.created_at).toLocaleString();
    
    // Analysis information
    const analysisInfo = document.getElementById('analysis-info');
    
    if (isFake) {
        analysisInfo.innerHTML = `
            <div class="info-box warning">
                <h4>⚠️ Deepfake Indicators Detected</h4>
                <p>Our AI model has identified patterns consistent with AI-generated or manipulated content. 
                With ${confidence.toFixed(2)}% confidence, this media shows signs of forgery.</p>
                <ul>
                    <li>Facial artifacts or inconsistencies may be present</li>
                    <li>Temporal anomalies detected in video frames</li>
                    <li>Compression patterns suggest manipulation</li>
                </ul>
                <p><strong>Recommendation:</strong> Exercise caution when sharing or trusting this content. 
                Verify the source and cross-reference with other reliable sources.</p>
            </div>
        `;
    } else {
        analysisInfo.innerHTML = `
            <div class="info-box success">
                <h4>✓ Authentic Media Detected</h4>
                <p>Our analysis indicates this media is ${confidence.toFixed(2)}% likely to be genuine and unmanipulated.</p>
                <ul>
                    <li>No significant forgery artifacts detected</li>
                    <li>Natural compression patterns observed</li>
                    <li>Temporal consistency maintained throughout</li>
                </ul>
                <p><strong>Note:</strong> While our model shows high confidence in authenticity, 
                no detection system is 100% accurate. Always verify important content from multiple sources.</p>
            </div>
        `;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initResultsPage);