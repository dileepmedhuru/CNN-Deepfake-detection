requireAuth();

// Load user info
const user = Storage.getUser();
document.getElementById('user-name').textContent = user.full_name;

let allHistory = [];
let filteredHistory = [];
let currentPage = 0;
const itemsPerPage = 20;

// Load history
async function loadHistory() {
    try {
        const data = await API.request(API_CONFIG.ENDPOINTS.HISTORY + '?limit=100');
        allHistory = data.history;
        applyFilters();
    } catch (error) {
        console.error('Failed to load history:', error);
        document.getElementById('history-list').innerHTML = 
            '<p class="error">Failed to load history. Please try again.</p>';
    }
}

// Apply filters
function applyFilters() {
    const typeFilter = document.getElementById('filter-type').value;
    const resultFilter = document.getElementById('filter-result').value;
    
    filteredHistory = allHistory.filter(item => {
        const typeMatch = typeFilter === 'all' || item.file_type === typeFilter;
        const resultMatch = resultFilter === 'all' || item.result === resultFilter;
        return typeMatch && resultMatch;
    });
    
    currentPage = 0;
    displayHistory();
}

// Display history
function displayHistory() {
    const historyList = document.getElementById('history-list');
    const loadMoreContainer = document.getElementById('load-more-container');
    
    if (filteredHistory.length === 0) {
        historyList.innerHTML = '<p class="empty-state">No detections found.</p>';
        loadMoreContainer.style.display = 'none';
        return;
    }
    
    const start = 0;
    const end = (currentPage + 1) * itemsPerPage;
    const itemsToShow = filteredHistory.slice(start, end);
    
    historyList.innerHTML = itemsToShow.map(detection => {
        const date = new Date(detection.created_at);
        const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        
        return `
            <div class="history-card">
                <div class="history-icon">${detection.file_type === 'image' ? '🖼️' : '🎥'}</div>
                <div class="history-details">
                    <h3>${detection.file_name}</h3>
                    <div class="history-info">
                        <span class="result-badge ${detection.result}">
                            ${detection.result.toUpperCase()}
                        </span>
                        <span class="confidence">Confidence: ${detection.confidence}%</span>
                        <span class="time">Processing: ${detection.processing_time}s</span>
                    </div>
                    <p class="timestamp">${formattedDate}</p>
                </div>
                <div class="history-actions">
                    <button class="btn btn-sm btn-secondary" onclick="viewDetails(${detection.id})">
                        View Details
                    </button>
                </div>
            </div>
        `;
    }).join('');
    
    // Show/hide load more button
    if (end < filteredHistory.length) {
        loadMoreContainer.style.display = 'block';
    } else {
        loadMoreContainer.style.display = 'none';
    }
}

// Load more
document.getElementById('load-more-btn').addEventListener('click', () => {
    currentPage++;
    displayHistory();
});

// Filter event listeners
document.getElementById('filter-type').addEventListener('change', applyFilters);
document.getElementById('filter-result').addEventListener('change', applyFilters);

// View details
function viewDetails(id) {
    window.location.href = `results.html?id=${id}`;
}

// Initial load
loadHistory();