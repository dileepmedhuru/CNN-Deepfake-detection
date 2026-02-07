// Signup Form Handler - Simple registration
if (document.getElementById('signup-form')) {
    document.getElementById('signup-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const fullName = document.getElementById('full_name').value.trim();
        const email = document.getElementById('email').value.trim().toLowerCase();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm_password').value;
        
        // Validate passwords match
        if (password !== confirmPassword) {
            showError('Passwords do not match');
            return;
        }
        
        setLoading(true);
        hideMessages();
        
        try {
            const response = await API.request(API_CONFIG.ENDPOINTS.SIGNUP, {
                method: 'POST',
                body: JSON.stringify({
                    full_name: fullName,
                    email: email,
                    password: password
                }),
                skipAuth: true
            });
            
            // Store token and user info directly
            Storage.setToken(response.token);
            Storage.setUser(response.user);
            
            showSuccess('Registration successful! Redirecting...');
            
            // Redirect to dashboard
            setTimeout(() => {
                if (response.user.is_admin) {
                    Redirect.toAdminDashboard();
                } else {
                    Redirect.toDashboard();
                }
            }, 1000);
            
        } catch (error) {
            showError(error.message || 'Signup failed. Please try again.');
        } finally {
            setLoading(false);
        }
    });
}

// Login Form Handler - Simple login
if (document.getElementById('login-form')) {
    document.getElementById('login-form').addEventListener('submit', async (e) => {
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
            
            // Store token and user info directly
            Storage.setToken(response.token);
            Storage.setUser(response.user);
            
            showSuccess('Login successful! Redirecting...');
            
            // Redirect to dashboard
            setTimeout(() => {
                if (response.user.is_admin) {
                    Redirect.toAdminDashboard();
                } else {
                    Redirect.toDashboard();
                }
            }, 1000);
            
        } catch (error) {
            showError(error.message || 'Login failed. Please try again.');
        } finally {
            setLoading(false);
        }
    });
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