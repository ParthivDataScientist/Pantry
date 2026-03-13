/**
 * auth.js — Login and sign-up form handling.
 *
 * Handles form toggling, POST requests to /api/login and /api/register,
 * token storage, and redirect based on role.
 */

document.addEventListener('DOMContentLoaded', () => {
    const loginForm  = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const toggleBtn  = document.getElementById('toggle-btn');
    const toggleText = document.getElementById('toggle-text');
    const errorMsg   = document.getElementById('error-msg');
    const formTitle  = document.querySelector('h2');

    let isLoginView = true;

    // ── Toggle between Login and Sign-Up views ────────────────────────────
    toggleBtn.addEventListener('click', (e) => {
        e.preventDefault();
        isLoginView = !isLoginView;
        errorMsg.classList.add('hidden');

        if (isLoginView) {
            loginForm.classList.remove('hidden');
            signupForm.classList.add('hidden');
            formTitle.textContent    = 'Sign In';
            toggleText.textContent  = "Don't have an account?";
            toggleBtn.textContent   = 'Sign up now';
        } else {
            loginForm.classList.add('hidden');
            signupForm.classList.remove('hidden');
            formTitle.textContent    = 'Create Account';
            toggleText.textContent  = 'Already have an account?';
            toggleBtn.textContent   = 'Sign in instead';
        }
    });

    // ── Login ─────────────────────────────────────────────────────────────
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const credentials = Object.fromEntries(new FormData(loginForm).entries());

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(credentials),
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('token', data.access_token);
                window.location.href = data.redirect_url;
            } else {
                showError('Invalid username or password.');
            }
        } catch {
            showError('Server error. Please try again.');
        }
    });

    // ── Sign Up ───────────────────────────────────────────────────────────
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const credentials = Object.fromEntries(new FormData(signupForm).entries());

        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(credentials),
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('token', data.access_token);
                window.location.href = data.redirect_url;
            } else {
                const errData = await response.json();
                showError(errData.detail || 'Registration failed. Please try again.');
            }
        } catch {
            showError('Server error. Please try again.');
        }
    });

    // ── Helpers ───────────────────────────────────────────────────────────
    function showError(message) {
        errorMsg.textContent = message;
        errorMsg.classList.remove('hidden');
    }
});
