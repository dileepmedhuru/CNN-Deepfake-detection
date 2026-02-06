// Global variables
let selectedFile = null;

// Initialize upload page
async function initUploadPage() {
    const session = await protectPage();
    if (!session) return;
    
    document.getElementById('user-name').textContent = session.user_name;
    setupDropZone();
    setupFileInput();
}

// Setup drag and drop
function setupDropZone() {
    const dropZone = document.getElementById('drop-zone');
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('highlight');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('highlight');
        }, false);
    });
    
    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
}

// Setup file input
function setupFileInput() {
    const fileInput = document.getElementById('file-input');
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
}

// Handle file selection
function handleFileSelect(file) {
    // Validate file type
    const validImageTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp'];
    const validVideoTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/x-flv', 'video/x-ms-wmv'];
    const allValidTypes = [...validImageTypes, ...validVideoTypes];
    
    if (!allValidTypes.includes(file.type)) {
        alert('Invalid file type. Please upload an image or video file.');
        return;
    }
    
    // Validate file size (100MB)
    const maxSize = 100 * 1024 * 1024;
    if (file.size > maxSize) {
        alert('File size exceeds 100MB limit.');
        return;
    }
    
    selectedFile = file;
    displayFilePreview(file);
}

// Display file preview
function displayFilePreview(file) {
    const dropZone = document.getElementById('drop-zone');
    const filePreview = document.getElementById('file-preview');
    const previewContent = document.getElementById('preview-content');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    
    // Hide drop zone, show preview
    dropZone.style.display = 'none';
    filePreview.style.display = 'block';
    
    // Set file info
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    
    // Create preview
    const reader = new FileReader();
    
    if (file.type.startsWith('image/')) {
        reader.onload = (e) => {
            previewContent.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
    } else if (file.type.startsWith('video/')) {
        reader.onload = (e) => {
            previewContent.innerHTML = `
                <video controls>
                    <source src="${e.target.result}" type="${file.type}">
                    Your browser does not support the video tag.
                </video>
            `;
        };
        reader.readAsDataURL(file);
    }
}

// Clear file selection
function clearFile() {
    selectedFile = null;
    document.getElementById('drop-zone').style.display = 'flex';
    document.getElementById('file-preview').style.display = 'none';
    document.getElementById('file-input').value = '';
}

// Upload and analyze file
async function uploadFile() {
    if (!selectedFile) {
        alert('Please select a file first.');
        return;
    }
    
    const uploadBtn = document.getElementById('upload-btn');
    const filePreview = document.getElementById('file-preview');
    const progressContainer = document.getElementById('progress-container');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    // Hide preview, show progress
    filePreview.style.display = 'none';
    progressContainer.style.display = 'block';
    
    // Simulate progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 10;
        if (progress <= 90) {
            progressFill.style.width = progress + '%';
        }
    }, 200);
    
    try {
        progressText.textContent = 'Uploading file...';
        
        // Create FormData
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        // Upload file
        const response = await apiCall(API_ENDPOINTS.DETECTION.UPLOAD, {
            method: 'POST',
            body: formData
        });
        
        clearInterval(progressInterval);
        progressFill.style.width = '100%';
        progressText.textContent = 'Analysis complete!';
        
        if (response.ok) {
            const data = await response.json();
            
            // Store result and redirect
            localStorage.setItem('latestDetection', JSON.stringify(data.detection));
            
            setTimeout(() => {
                window.location.href = '/results.html';
            }, 500);
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }
    } catch (error) {
        clearInterval(progressInterval);
        progressContainer.style.display = 'none';
        filePreview.style.display = 'block';
        
        alert('Error: ' + error.message);
        console.error('Upload error:', error);
    }
}

// Helper function to format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initUploadPage);