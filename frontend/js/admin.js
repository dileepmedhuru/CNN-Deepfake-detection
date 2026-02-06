// Global variables
let allUsers = [];
let allDetections = [];
let currentTab = 'users';

// Initialize admin dashboard
async function initAdminDashboard() {
    const session = await protectPage('admin');
    if (!session) return;
    
    document.getElementById('admin-name').textContent = session.user_name;
    
    await loadSystemStats();
    await loadUsers();
}

// Load system statistics
async function loadSystemStats() {
    try {
        const response = await apiCall(API_ENDPOINTS.ADMIN.STATS);
        const data = await response.json();
        
        // Update statistics
        document.getElementById('total-users').textContent = data.users.total || 0;
        document.getElementById('total-detections').textContent = data.detections.total || 0;
        document.getElementById('fake-count').textContent = data.detections.fake || 0;
        document.getElementById('recent-activity').textContent = data.detections.recent_week || 0;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load all users
async function loadUsers() {
    try {
        const response = await apiCall(API_ENDPOINTS.ADMIN.USERS + '?per_page=100');
        const data = await response.json();
        
        allUsers = data.users || [];
        displayUsers();
    } catch (error) {
        console.error('Error loading users:', error);
        showUsersError();
    }
}

// Display users table
function displayUsers() {
    const tbody = document.getElementById('users-tbody');
    
    if (allUsers.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center">No users found</td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = allUsers.map(user => `
        <tr>
            <td>${user.id}</td>
            <td>${user.name}</td>
            <td>${user.email}</td>
            <td>
                <span class="badge badge-${user.role === 'admin' ? 'admin' : 'user'}">
                    ${user.role}
                </span>
            </td>
            <td>${user.detection_count || 0}</td>
            <td>${formatDate(user.created_at)}</td>
            <td>
                ${user.role !== 'admin' ? `
                    <button class="btn-icon" onclick="toggleUserRole(${user.id})" title="Toggle Role">
                        <i class="fas fa-user-cog"></i>
                    </button>
                    <button class="btn-icon danger" onclick="deleteUser(${user.id}, '${user.name}')" title="Delete User">
                        <i class="fas fa-trash"></i>
                    </button>
                ` : '<span class="text-muted">Admin</span>'}
            </td>
        </tr>
    `).join('');
}

// Search users
function searchUsers() {
    const searchTerm = document.getElementById('user-search').value.toLowerCase();
    
    const filtered = allUsers.filter(user => 
        user.name.toLowerCase().includes(searchTerm) ||
        user.email.toLowerCase().includes(searchTerm)
    );
    
    const tbody = document.getElementById('users-tbody');
    
    if (filtered.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center">No users found matching "${searchTerm}"</td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = filtered.map(user => `
        <tr>
            <td>${user.id}</td>
            <td>${user.name}</td>
            <td>${user.email}</td>
            <td>
                <span class="badge badge-${user.role === 'admin' ? 'admin' : 'user'}">
                    ${user.role}
                </span>
            </td>
            <td>${user.detection_count || 0}</td>
            <td>${formatDate(user.created_at)}</td>
            <td>
                ${user.role !== 'admin' ? `
                    <button class="btn-icon" onclick="toggleUserRole(${user.id})" title="Toggle Role">
                        <i class="fas fa-user-cog"></i>
                    </button>
                    <button class="btn-icon danger" onclick="deleteUser(${user.id}, '${user.name}')" title="Delete User">
                        <i class="fas fa-trash"></i>
                    </button>
                ` : '<span class="text-muted">Admin</span>'}
            </td>
        </tr>
    `).join('');
}

// Toggle user role
async function toggleUserRole(userId) {
    if (!confirm('Are you sure you want to change this user\'s role?')) return;
    
    try {
        const response = await apiCall(API_ENDPOINTS.ADMIN.TOGGLE_ROLE(userId), {
            method: 'PUT'
        });
        
        if (response.ok) {
            await loadUsers();
            alert('User role updated successfully');
        } else {
            const error = await response.json();
            alert('Error: ' + error.error);
        }
    } catch (error) {
        console.error('Error toggling role:', error);
        alert('Failed to update user role');
    }
}

// Delete user
async function deleteUser(userId, userName) {
    if (!confirm(`Are you sure you want to delete user "${userName}"? This action cannot be undone.`)) return;
    
    try {
        const response = await apiCall(API_ENDPOINTS.ADMIN.DELETE_USER(userId), {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await loadUsers();
            await loadSystemStats();
            alert('User deleted successfully');
        } else {
            const error = await response.json();
            alert('Error: ' + error.error);
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        alert('Failed to delete user');
    }
}

// Load all detections
async function loadDetections() {
    try {
        const response = await apiCall(API_ENDPOINTS.ADMIN.DETECTIONS + '?per_page=100');
        const data = await response.json();
        
        allDetections = data.detections || [];
        displayDetections();
    } catch (error) {
        console.error('Error loading detections:', error);
        showDetectionsError();
    }
}

// Display detections table
function displayDetections() {
    const tbody = document.getElementById('detections-tbody');
    
    if (allDetections.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center">No detections found</td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = allDetections.map(det => `
        <tr>
            <td>${det.id}</td>
            <td>${det.user_name}</td>
            <td>
                <i class="fas fa-${det.file_type === 'image' ? 'image' : 'video'}"></i>
                ${det.file_name}
            </td>
            <td><span class="badge badge-${det.file_type}">${det.file_type}</span></td>
            <td>
                <span class="badge badge-${det.prediction}">
                    ${det.prediction === 'fake' ? '⚠️ Fake' : '✓ Real'}
                </span>
            </td>
            <td>${det.confidence}%</td>
            <td>${formatDate(det.created_at)}</td>
            <td>
                <button class="btn-icon danger" onclick="deleteDetection(${det.id})" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// Filter detections
function filterDetections() {
    const filter = document.getElementById('detection-filter').value;
    
    const filtered = filter === 'all' ? allDetections : 
                     allDetections.filter(det => det.prediction === filter);
    
    const tbody = document.getElementById('detections-tbody');
    
    if (filtered.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center">No detections found</td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = filtered.map(det => `
        <tr>
            <td>${det.id}</td>
            <td>${det.user_name}</td>
            <td>
                <i class="fas fa-${det.file_type === 'image' ? 'image' : 'video'}"></i>
                ${det.file_name}
            </td>
            <td><span class="badge badge-${det.file_type}">${det.file_type}</span></td>
            <td>
                <span class="badge badge-${det.prediction}">
                    ${det.prediction === 'fake' ? '⚠️ Fake' : '✓ Real'}
                </span>
            </td>
            <td>${det.confidence}%</td>
            <td>${formatDate(det.created_at)}</td>
            <td>
                <button class="btn-icon danger" onclick="deleteDetection(${det.id})" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// Delete detection
async function deleteDetection(detectionId) {
    if (!confirm('Are you sure you want to delete this detection record?')) return;
    
    try {
        const response = await apiCall(API_ENDPOINTS.ADMIN.DELETE_DETECTION(detectionId), {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await loadDetections();
            await loadSystemStats();
            alert('Detection deleted successfully');
        } else {
            const error = await response.json();
            alert('Error: ' + error.error);
        }
    } catch (error) {
        console.error('Error deleting detection:', error);
        alert('Failed to delete detection');
    }
}

// Switch tabs
function switchTab(tab) {
    currentTab = tab;
    
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[onclick="switchTab('${tab}')"]`).classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`${tab}-tab`).classList.add('active');
    
    // Load data if not already loaded
    if (tab === 'detections' && allDetections.length === 0) {
        loadDetections();
    }
}

// Helper functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

function showUsersError() {
    const tbody = document.getElementById('users-tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="7" class="text-center error">
                Error loading users. Please refresh the page.
            </td>
        </tr>
    `;
}

function showDetectionsError() {
    const tbody = document.getElementById('detections-tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="8" class="text-center error">
                Error loading detections. Please refresh the page.
            </td>
        </tr>
    `;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initAdminDashboard);