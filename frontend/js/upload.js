requireAuth();

// Load user info
const user = Storage.getUser();
document.getElementById('user-name').textContent = user.full_name;

// Get elements
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const filePreview = document.getElementById('file-preview');
const imagePreview = document.getElementById('image-preview');
const videoPreview = document.getElementById('video-preview');
const fileInfo = document.getElementById('file-info');
const progressSection = document.getElementById('progress-section');
const resultsSection = document.getElementById('results-section');

let selectedFile = null;
let currentFileType = 'image';

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        currentFileType = btn.dataset.type;
        
        if (currentFileType === 'image') {
            fileInput.accept = 'image/*';
            document.getElementById('file-types').textContent = 'Supported: JPG, PNG, GIF';
        } else {
            fileInput.accept = 'video/*';
            document.getElementById('file-types').textContent = 'Supported: MP4, AVI, MOV, MKV';
        }
        
        resetUpload();
    });
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

// File input change
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// Handle file selection
function handleFileSelect(file) {
    // Validate file type
    const isImage = file.type.startsWith('image/');
    const isVideo = file.type.startsWith('video/');
    
    if (currentFileType === 'image' && !isImage) {
        showError('Please select an image file');
        return;
    }
    
    if (currentFileType === 'video' && !isVideo) {
        showError('Please select a video file');
        return;
    }
    
    // Validate file size (100MB max)
    const maxSize = 100 * 1024 * 1024;
    if (file.size > maxSize) {
        showError('File size must be less than 100MB');
        return;
    }
    
    selectedFile = file;
    showFilePreview(file);
}

// Show file preview
function showFilePreview(file) {
    uploadArea.style.display = 'none';
    filePreview.style.display = 'block';
    
    const reader = new FileReader();
    
    reader.onload = (e) => {
        if (file.type.startsWith('image/')) {
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'block';
            videoPreview.style.display = 'none';
        } else {
            videoPreview.src = e.target.result;
            videoPreview.style.display = 'block';
            imagePreview.style.display = 'none';
        }
    };
    
    reader.readAsDataURL(file);
    
    // Show file info
    const sizeInMB = (file.size / (1024 * 1024)).toFixed(2);
    fileInfo.innerHTML = `
        <p><strong>Filename:</strong> ${file.name}</p>
        <p><strong>Size:</strong> ${sizeInMB} MB</p>
        <p><strong>Type:</strong> ${file.type}</p>
    `;
}

// Reset upload
function resetUpload() {
    selectedFile = null;
    fileInput.value = '';
    uploadArea.style.display = 'block';
    filePreview.style.display = 'none';
    progressSection.style.display = 'none';
    resultsSection.style.display = 'none';
    imagePreview.style.display = 'none';
    videoPreview.style.display = 'none';
    hideMessages();
}

// Analyze file
async function analyzeFile() {
    if (!selectedFile) {
        showError('Please select a file first');
        return;
    }
    
    filePreview.style.display = 'none';
    progressSection.style.display = 'block';
    hideMessages();
    
    try {
        const endpoint = currentFileType === 'image' ? 
            API_CONFIG.ENDPOINTS.UPLOAD_IMAGE : 
            API_CONFIG.ENDPOINTS.UPLOAD_VIDEO;
        
        const response = await API.uploadFile(endpoint, selectedFile, (progress) => {
            updateProgress(progress, 'Uploading file...');
        });
        
        updateProgress(100, 'Analyzing content...');
        
        // Show results
        setTimeout(() => {
            showResults(response);
        }, 500);
        
    } catch (error) {
        progressSection.style.display = 'none';
        filePreview.style.display = 'block';
        showError(error.message || 'Analysis failed. Please try again.');
    }
}

// Update progress
function updateProgress(percent, message) {
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    progressFill.style.width = percent + '%';
    progressText.textContent = message + ' ' + Math.round(percent) + '%';
}

// Show results
function showResults(data) {
    progressSection.style.display = 'none';
    resultsSection.style.display = 'block';
    
    const resultStatus = document.getElementById('result-status');
    const isFake = data.result.toLowerCase() === 'fake';
    
    resultStatus.className = 'result-status ' + (isFake ? 'fake' : 'real');
    resultStatus.innerHTML = `
        <div class="status-icon">${isFake ? '⚠️' : '✅'}</div>
        <h3>${isFake ? 'FAKE DETECTED' : 'AUTHENTIC'}</h3>
        <p>This content appears to be ${isFake ? 'manipulated' : 'genuine'}</p>
    `;
    
    document.getElementById('confidence-value').textContent = data.confidence + '%';
    document.getElementById('processing-time').textContent = data.processing_time + 's';
}

// Utility functions
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

function showSuccess(message) {
    const successDiv = document.getElementById('success-message');
    if (successDiv) {
        successDiv.textContent = message;
        successDiv.style.display = 'block';
    }
}

function hideMessages() {
    const errorDiv = document.getElementById('error-message');
    const successDiv = document.getElementById('success-message');
    if (errorDiv) errorDiv.style.display = 'none';
    if (successDiv) successDiv.style.display = 'none';
}

// Check URL parameters for file type
const urlParams = new URLSearchParams(window.location.search);
const typeParam = urlParams.get('type');
if (typeParam === 'video') {
    document.querySelector('.tab-btn[data-type="video"]').click();
}