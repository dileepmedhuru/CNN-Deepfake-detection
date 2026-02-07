// Admin Login Form Handler
const adminLoginForm = document.getElementById('admin-login-form');
if (adminLoginForm) {
    adminLoginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value.trim().toLowerCase();
        const password = document.getElementById('password').value;
        
        setLoading(true);
        hideMessages();
        
        try {
            const response = await API.request(API_CONFIG.ENDPOINTS.LOGIN, {
                method: 'POST',
                body: JSON.stringify({
                    email: email,
                    password: password
                }),
                skipAuth: true
            });
            
            console.log('Login response:', response);
            
            // Check if user is admin
            if (!response.user.is_admin) {
                showError('Access denied. Admin privileges required.');
                return;
            }
            
            // Store token and user info
            Storage.setToken(response.token);
            Storage.setUser(response.user);
            
            showSuccess('Admin login successful! Redirecting...');
            
            // Redirect to admin dashboard
            setTimeout(() => {
                window.location.href = '/admin-dashboard.html';
            }, 1000);
            
        } catch (error) {
            showError(error.message || 'Login failed. Please try again.');
        } finally {
            setLoading(false);
        }
    });
}

// Admin Dashboard Logic
if (window.location.pathname.includes('admin-dashboard')) {
    requireAdmin();
    
    const user = Storage.getUser();
    if (document.getElementById('admin-name')) {
        document.getElementById('admin-name').textContent = user.full_name;
    }
    
    // Load dashboard stats
    async function loadDashboardStats() {
        try {
            const data = await API.request(API_CONFIG.ENDPOINTS.ADMIN_DASHBOARD);
            
            document.getElementById('total-users').textContent = data.total_users || 0;
            document.getElementById('total-detections').textContent = data.total_detections || 0;
            document.getElementById('fake-detections').textContent = data.fake_detections || 0;
            document.getElementById('real-detections').textContent = data.real_detections || 0;
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }
    
    // Load users
    async function loadUsers() {
        try {
            const data = await API.request(API_CONFIG.ENDPOINTS.ADMIN_USERS);
            const usersList = document.getElementById('users-list');
            
            if (data.users.length === 0) {
                usersList.innerHTML = '<p class="empty-state">No users found.</p>';
                return;
            }
            
            usersList.innerHTML = `
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Verified</th>
                            <th>Admin</th>
                            <th>Joined</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.users.map(user => `
                            <tr>
                                <td>${user.id}</td>
                                <td>${user.full_name}</td>
                                <td>${user.email}</td>
                                <td>${user.is_verified ? '✅' : '❌'}</td>
                                <td>${user.is_admin ? '👑' : '-'}</td>
                                <td>${new Date(user.created_at).toLocaleDateString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } catch (error) {
            console.error('Failed to load users:', error);
            document.getElementById('users-list').innerHTML = 
                '<p class="error">Failed to load users.</p>';
        }
    }
    
    // Load detections
    async function loadDetections() {
        try {
            const data = await API.request(API_CONFIG.ENDPOINTS.ADMIN_DETECTIONS);
            const detectionsList = document.getElementById('detections-list');
            
            if (data.detections.length === 0) {
                detectionsList.innerHTML = '<p class="empty-state">No detections found.</p>';
                return;
            }
            
            detectionsList.innerHTML = `
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>User</th>
                            <th>File</th>
                            <th>Type</th>
                            <th>Result</th>
                            <th>Confidence</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.detections.map(detection => `
                            <tr>
                                <td>${detection.id}</td>
                                <td>${detection.full_name}</td>
                                <td>${detection.file_name}</td>
                                <td>${detection.file_type}</td>
                                <td><span class="result-badge ${detection.result}">${detection.result.toUpperCase()}</span></td>
                                <td>${detection.confidence}%</td>
                                <td>${new Date(detection.created_at).toLocaleDateString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } catch (error) {
            console.error('Failed to load detections:', error);
            document.getElementById('detections-list').innerHTML = 
                '<p class="error">Failed to load detections.</p>';
        }
    }
    
    // Tab switching
    const tabButtons = document.querySelectorAll('.tab-btn');
    if (tabButtons.length > 0) {
        tabButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                
                btn.classList.add('active');
                const tabName = btn.dataset.tab;
                document.getElementById(tabName + '-tab').classList.add('active');
            });
        });
    }
    
    // Initial load
    loadDashboardStats();
    loadUsers();
    loadDetections();
}

// Utility Functions
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
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

function setLoading(isLoading) {
    const btn = document.querySelector('button[type="submit"]');
    const btnText = document.getElementById('btn-text');
    const btnLoader = document.getElementById('btn-loader');
    
    if (btn) {
        btn.disabled = isLoading;
    }
    
    if (btnText && btnLoader) {
        btnText.style.display = isLoading ? 'none' : 'inline';
        btnLoader.style.display = isLoading ? 'inline-block' : 'none';
    }
}