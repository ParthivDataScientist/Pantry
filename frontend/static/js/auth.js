
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const toggleBtn = document.getElementById('toggle-btn');
    const toggleText = document.getElementById('toggle-text');
    const errorMsg = document.getElementById('error-msg');
    const title = document.querySelector('h2'); // "Sign In" header

    let isLogin = true;

    toggleBtn.addEventListener('click', (e) => {
        e.preventDefault();
        isLogin = !isLogin;

        if (isLogin) {
            loginForm.classList.remove('hidden');
            signupForm.classList.add('hidden');
            title.textContent = 'Sign In';
            toggleText.textContent = "Don't have an account?";
            toggleBtn.textContent = 'Sign up now';
        } else {
            loginForm.classList.add('hidden');
            signupForm.classList.remove('hidden');
            title.textContent = 'Create Account';
            toggleText.textContent = "Already have an account?";
            toggleBtn.textContent = 'Sign in instead';
        }
        errorMsg.classList.add('hidden');
    });

    // Login Handler
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(loginForm);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const data = await response.json();
                console.log("Login successful, token received:", data);
                localStorage.setItem('token', data.access_token);

                if (data.redirect_url) {
                    console.log("Redirecting to:", data.redirect_url);
                    window.location.href = data.redirect_url;
                } else {
                    // Fallback
                    if (data.role === 'pantry') {
                        window.location.href = '/pantry';
                    } else {
                        window.location.href = '/order';
                    }
                }
            } else {
                console.error("Login failed", response.status);
                showError('Invalid username or password');
            }
        } catch (err) {
            console.error("Login error:", err);
            showError('Server error. Please try again.');
        }
    });

    // Sign Up Handler
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = new FormData(signupForm);
        const data = Object.fromEntries(form.entries());

        try {
            // Register endpoint likely expects JSON based on schema
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const data = await response.json();
                // Auto login logic
                localStorage.setItem('token', data.access_token);
                window.location.href = '/order';
            } else {
                const errData = await response.json();
                showError(errData.detail || 'Registration failed');
            }
        } catch (err) {
            showError('Server error. Please try again.');
        }
    });

    function showError(msg) {
        errorMsg.textContent = msg;
        errorMsg.classList.remove('hidden');
        errorMsg.classList.add('block');
    }
});
