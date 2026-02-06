// Password visibility toggle
function togglePassword(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Show/hide loading state
function setLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    } else {
        button.disabled = false;
        button.textContent = button.dataset.originalText || button.textContent;
    }
}

// Show error message
function showError(elementId, message) {
    const errorDiv = document.getElementById(elementId);
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    // Hide after 5 seconds
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// Hide error message
function hideError(elementId) {
    const errorDiv = document.getElementById(elementId);
    errorDiv.style.display = 'none';
}

// Handle signup
async function handleSignup(event) {
    event.preventDefault();
    
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const submitButton = event.target.querySelector('button[type="submit"]');
    
    // Validation
    if (!name || !email || !password || !confirmPassword) {
        showError('error-message', 'All fields are required');
        return;
    }
    
    if (password !== confirmPassword) {
        showError('error-message', 'Passwords do not match');
        return;
    }
    
    if (password.length < 6) {
        showError('error-message', 'Password must be at least 6 characters');
        return;
    }
    
    setLoading(submitButton, true);
    hideError('error-message');
    
    try {
        const response = await apiCall(API_ENDPOINTS.AUTH.SIGNUP, {
            method: 'POST',
            body: JSON.stringify({ name, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store session info in localStorage for verification
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('userName', data.user.name);
            
            // Redirect to dashboard with absolute URL
            window.location.href = 'http://localhost:5000/dashboard.html';
        } else {
            showError('error-message', data.error || 'Signup failed');
        }
    } catch (error) {
        showError('error-message', 'Network error. Please try again.');
        console.error('Signup error:', error);
    } finally {
        setLoading(submitButton, false);
    }
}

// Handle login
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const submitButton = event.target.querySelector('button[type="submit"]');
    
    if (!email || !password) {
        showError('error-message', 'Email and password are required');
        return;
    }
    
    setLoading(submitButton, true);
    hideError('error-message');
    
    try {
        const response = await apiCall(API_ENDPOINTS.AUTH.LOGIN, {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store session info in localStorage for verification
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('userName', data.user.name);
            
            // Small delay to ensure session is set
            setTimeout(() => {
                window.location.href = 'http://localhost:5000/dashboard.html';
            }, 100);
        } else {
            showError('error-message', data.error || 'Login failed');
        }
    } catch (error) {
        showError('error-message', 'Network error. Please try again.');
        console.error('Login error:', error);
    } finally {
        setLoading(submitButton, false);
    }
}

// Handle admin login
async function handleAdminLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const submitButton = event.target.querySelector('button[type="submit"]');
    
    if (!email || !password) {
        showError('error-message', 'Email and password are required');
        return;
    }
    
    setLoading(submitButton, true);
    hideError('error-message');
    
    try {
        const response = await apiCall(API_ENDPOINTS.AUTH.ADMIN_LOGIN, {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store session info
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('isAdmin', 'true');
            localStorage.setItem('userName', data.user.name);
            
            // Redirect to admin dashboard
            setTimeout(() => {
                window.location.href = 'http://localhost:5000/admin-dashboard.html';
            }, 100);
        } else {
            showError('error-message', data.error || 'Admin login failed');
        }
    } catch (error) {
        showError('error-message', 'Network error. Please try again.');
        console.error('Admin login error:', error);
    } finally {
        setLoading(submitButton, false);
    }
}

// Handle logout
async function handleLogout() {
    try {
        const response = await apiCall(API_ENDPOINTS.AUTH.LOGOUT, {
            method: 'POST'
        });
        
        // Clear localStorage
        localStorage.removeItem('isLoggedIn');
        localStorage.removeItem('userName');
        localStorage.removeItem('isAdmin');
        
        if (response.ok) {
            window.location.href = 'http://localhost:5000/index.html';
        }
    } catch (error) {
        console.error('Logout error:', error);
        // Clear localStorage and redirect anyway
        localStorage.clear();
        window.location.href = 'http://localhost:5000/index.html';
    }
}

// Check if user is logged in
async function checkSession() {
    try {
        const response = await apiCall(API_ENDPOINTS.AUTH.CHECK_SESSION);
        const data = await response.json();
        
        if (data.logged_in) {
            // Update localStorage
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('userName', data.user_name);
            return data;
        } else {
            // Clear localStorage if not logged in
            localStorage.removeItem('isLoggedIn');
            localStorage.removeItem('userName');
            localStorage.removeItem('isAdmin');
            return null;
        }
    } catch (error) {
        console.error('Session check error:', error);
        return null;
    }
}

// Protect pages that require authentication
async function protectPage(requiredRole = 'user') {
    const session = await checkSession();
    
    if (!session) {
        // Not logged in - redirect to login
        if (requiredRole === 'admin') {
            window.location.href = 'http://localhost:5000/admin-login.html';
        } else {
            window.location.href = 'http://localhost:5000/login.html';
        }
        return null;
    }
    
    if (requiredRole === 'admin' && session.user_role !== 'admin') {
        // Not admin - redirect to user dashboard
        window.location.href = 'http://localhost:5000/dashboard.html';
        return null;
    }
    
    return session;
}

// Prevent logged-in users from accessing login/signup pages
async function preventAuthPageAccess() {
    const session = await checkSession();
    
    if (session) {
        // User is logged in, redirect to appropriate dashboard
        if (session.user_role === 'admin') {
            window.location.href = 'http://localhost:5000/admin-dashboard.html';
        } else {
            window.location.href = 'http://localhost:5000/dashboard.html';
        }
    }
}

// Initialize auth forms
document.addEventListener('DOMContentLoaded', () => {
    // Check which page we're on
    const signupForm = document.getElementById('signup-form');
    const loginForm = document.getElementById('login-form');
    const adminLoginForm = document.getElementById('admin-login-form');
    
    // If on login/signup page, check if already logged in
    if (loginForm || signupForm || adminLoginForm) {
        preventAuthPageAccess();
    }
    
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    if (adminLoginForm) {
        adminLoginForm.addEventListener('submit', handleAdminLogin);
    }
});