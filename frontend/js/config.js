// API Configuration - Using relative URL since frontend and backend are on same server
const API_CONFIG = {
    BASE_URL: '/api',  // Relative URL - same server
    ENDPOINTS: {
        // Auth endpoints (Simple - No OTP, No Google)
        SIGNUP: '/auth/signup',
        LOGIN: '/auth/login',
        VERIFY_TOKEN: '/auth/verify-token',
        
        // Detection endpoints
        UPLOAD_IMAGE: '/detection/upload-image',
        UPLOAD_VIDEO: '/detection/upload-video',
        HISTORY: '/detection/history',
        USER_STATS: '/detection/stats',
        DETECTION_DETAIL: '/detection/detection',
        
        // Admin endpoints
        ADMIN_USERS: '/admin/users',
        ADMIN_DETECTIONS: '/admin/detections',
        ADMIN_STATS: '/admin/stats',
        ADMIN_DASHBOARD: '/admin/dashboard-stats',
        ADMIN_USER_DETAIL: '/admin/user'
    }
};

// Utility functions
const API = {
    async request(endpoint, options = {}) {
        const url = `${API_CONFIG.BASE_URL}${endpoint}`;
        const token = localStorage.getItem('token');
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (token && !options.skipAuth) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        try {
            const response = await fetch(url, {
                ...options,
                headers
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    
    async uploadFile(endpoint, file, onProgress) {
        const url = `${API_CONFIG.BASE_URL}${endpoint}`;
        const token = localStorage.getItem('token');
        
        const formData = new FormData();
        formData.append('file', file);
        
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            // Track upload progress
            if (onProgress) {
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        onProgress(percentComplete);
                    }
                });
            }
            
            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    resolve(JSON.parse(xhr.responseText));
                } else {
                    const error = JSON.parse(xhr.responseText);
                    reject(new Error(error.error || 'Upload failed'));
                }
            });
            
            xhr.addEventListener('error', () => {
                reject(new Error('Network error'));
            });
            
            xhr.open('POST', url);
            xhr.setRequestHeader('Authorization', `Bearer ${token}`);
            xhr.send(formData);
        });
    }
};

// Storage utilities
const Storage = {
    setToken(token) {
        localStorage.setItem('token', token);
    },
    
    getToken() {
        return localStorage.getItem('token');
    },
    
    removeToken() {
        localStorage.removeItem('token');
    },
    
    setUser(user) {
        localStorage.setItem('user', JSON.stringify(user));
    },
    
    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },
    
    removeUser() {
        localStorage.removeItem('user');
    },
    
    clear() {
        localStorage.clear();
    },
    
    isAuthenticated() {
        return !!this.getToken();
    },
    
    isAdmin() {
        const user = this.getUser();
        return user && user.is_admin;
    }
};

// Redirect utilities
const Redirect = {
    toLogin() {
        window.location.href = '/login.html';
    },
    
    toDashboard() {
        window.location.href = '/dashboard.html';
    },
    
    toAdminDashboard() {
        window.location.href = '/admin-dashboard.html';
    }
};

// Check authentication on protected pages
function requireAuth() {
    if (!Storage.isAuthenticated()) {
        Redirect.toLogin();
        return false;
    }
    return true;
}

// Check admin authentication
function requireAdmin() {
    if (!Storage.isAuthenticated() || !Storage.isAdmin()) {
        Redirect.toLogin();
        return false;
    }
    return true;
}

// Logout function
function logout() {
    Storage.clear();
    Redirect.toLogin();
}

// Log configuration on load
console.log('🔧 API Configuration Loaded');
console.log('📡 API Base URL:', API_CONFIG.BASE_URL);
console.log('🔐 Auth:', Storage.isAuthenticated() ? 'Authenticated' : 'Not authenticated');