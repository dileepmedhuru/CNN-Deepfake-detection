// Global variables
let currentPage = 1;
let totalPages = 1;
let allHistory = [];
let filteredHistory = [];

// Initialize history page
async function initHistoryPage() {
    const session = await protectPage();
    if (!session) return;
    
    document.getElementById('user-name').textContent = session.user_name;
    await loadHistory();
}

// Load detection history
async function loadHistory(page = 1) {
    try {
        const response = await apiCall(API_ENDPOINTS.DETECTION.HISTORY + `?page=${page}&per_page=20`);
        const data = await response.json();
        
        allHistory = data.history || [];
        filteredHistory = [...allHistory];
        currentPage = data.current_page || 1;
        totalPages = data.pages || 1;
        
        displayHistory();
        updatePagination();
    } catch (error) {
        console.error('Error loading history:', error);
        showError();
    }
}

// Display history table
function displayHistory() {
    const tbody = document.getElementById('history-tbody');
    const emptyState = document.getElementById('empty-state');
    const pagination = document.getElementById('pagination');
    
    if (filteredHistory.length === 0) {
        tbody.innerHTML = '';
        emptyState.style.display = 'flex';
        pagination.style.display = 'none';
        return;
    }
    
    emptyState.style.display = 'none';
    pagination.style.display = 'flex';
    
    tbody.innerHTML = filteredHistory.map(item => `
        <tr>
            <td>
                <i class="fas fa-${item.file_type === 'image' ? 'image' : 'video'}"></i>
                ${item.file_name}
            </td>
            <td><span class="badge badge-${item.file_type}">${item.file_type}</span></td>
            <td>
                <span class="badge badge-${item.prediction}">
                    ${item.prediction === 'fake' ? '⚠️ Fake' : '✓ Real'}
                </span>
            </td>
            <td class="confidence-cell">
                <div class="mini-progress">
                    <div class="mini-fill ${item.prediction}" style="width: ${item.confidence}%"></div>
                </div>
                <span>${item.confidence}%</span>
            </td>
            <td>${item.processing_time ? item.processing_time.toFixed(2) + 's' : '-'}</td>
            <td>${formatDate(item.created_at)}</td>
            <td>
                <button class="btn-icon" onclick="viewDetails(${item.id})" title="View Details">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// Filter history
function filterHistory() {
    const typeFilter = document.getElementById('filter-type').value;
    const predictionFilter = document.getElementById('filter-prediction').value;
    
    filteredHistory = allHistory.filter(item => {
        const typeMatch = typeFilter === 'all' || item.file_type === typeFilter;
        const predictionMatch = predictionFilter === 'all' || item.prediction === predictionFilter;
        return typeMatch && predictionMatch;
    });
    
    displayHistory();
}

// View detection details
function viewDetails(detectionId) {
    // Store detection ID and redirect to results page
    const detection = allHistory.find(item => item.id === detectionId);
    if (detection) {
        localStorage.setItem('latestDetection', JSON.stringify(detection));
        window.location.href = '/results.html';
    }
}

// Pagination
function updatePagination() {
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const pageInfo = document.getElementById('page-info');
    
    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;
}

function previousPage() {
    if (currentPage > 1) {
        loadHistory(currentPage - 1);
    }
}

function nextPage() {
    if (currentPage < totalPages) {
        loadHistory(currentPage + 1);
    }
}

// Helper function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

// Show error state
function showError() {
    const tbody = document.getElementById('history-tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="7" class="text-center error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Error loading history. Please try again.</p>
            </td>
        </tr>
    `;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initHistoryPage);