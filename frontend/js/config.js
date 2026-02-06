// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

const API_ENDPOINTS = {
    // Auth endpoints
    AUTH: {
        SIGNUP: `${API_BASE_URL}/auth/signup`,
        LOGIN: `${API_BASE_URL}/auth/login`,
        ADMIN_LOGIN: `${API_BASE_URL}/auth/admin-login`,
        LOGOUT: `${API_BASE_URL}/auth/logout`,
        ME: `${API_BASE_URL}/auth/me`,
        CHECK_SESSION: `${API_BASE_URL}/auth/check-session`
    },
    
    // Detection endpoints
    DETECTION: {
        UPLOAD: `${API_BASE_URL}/detection/upload`,
        HISTORY: `${API_BASE_URL}/detection/history`,
        DETAIL: (id) => `${API_BASE_URL}/detection/history/${id}`,
        STATS: `${API_BASE_URL}/detection/stats`
    },
    
    // Admin endpoints
    ADMIN: {
        USERS: `${API_BASE_URL}/admin/users`,
        USER_DETAIL: (id) => `${API_BASE_URL}/admin/users/${id}`,
        DELETE_USER: (id) => `${API_BASE_URL}/admin/users/${id}`,
        TOGGLE_ROLE: (id) => `${API_BASE_URL}/admin/users/${id}/toggle-role`,
        DETECTIONS: `${API_BASE_URL}/admin/detections`,
        DELETE_DETECTION: (id) => `${API_BASE_URL}/admin/detections/${id}`,
        STATS: `${API_BASE_URL}/admin/stats`
    },
    
    // Health check
    HEALTH: `${API_BASE_URL}/health`
};

// Helper function for API calls
async function apiCall(url, options = {}) {
    const defaultOptions = {
        credentials: 'include', // Include cookies for session
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    };
    
    // Don't set Content-Type for FormData
    if (options.body instanceof FormData) {
        delete defaultOptions.headers['Content-Type'];
    }
    
    const response = await fetch(url, { ...defaultOptions, ...options });
    
    // Handle session expiry
    if (response.status === 401) {
        const data = await response.json();
        if (data.redirect) {
            window.location.href = data.redirect;
            return null;
        }
    }
    
    return response;
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API_ENDPOINTS, apiCall };
}