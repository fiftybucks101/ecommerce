/* ==========================================================================
   Login Page Logic (login.js)
   Handles credentials validation, POST /auth/login dispatch,
   session storage via auth.js, GET /auth/me user profile retrieval,
   alert handling (invalid credentials, validation errors),
   and redirection to store home (../index.html).
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const emailInput = document.getElementById("emailInput");
    const passwordInput = document.getElementById("passwordInput");
    const forgotPasswordLink = document.getElementById("forgotPasswordLink");
    const loginBtn = document.getElementById("loginBtn");
    const alertBox = document.getElementById("alertBox");

    // Standard API base URL fallback from auth helper or default
    const API_BASE_URL = (window.auth && window.auth.API_BASE_URL) 
        ? window.auth.API_BASE_URL 
        : "http://localhost:8000";

    /**
     * Display alert notification message
     * @param {string} message 
     * @param {"error"|"success"} type 
     */
    function showAlert(message, type = "error") {
        if (!alertBox) return;
        alertBox.textContent = message;
        alertBox.className = `auth-alert show ${type}`;
        alertBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    /**
     * Clear and hide alert
     */
    function hideAlert() {
        if (!alertBox) return;
        alertBox.textContent = "";
        alertBox.className = "auth-alert";
    }

    /**
     * Email format regex validation
     * @param {string} email 
     * @returns {boolean}
     */
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Validate login input fields
     * @returns {boolean}
     */
    function validateForm(email, password) {
        if (!email) {
            showAlert("Please enter your email address.", "error");
            if (emailInput) emailInput.focus();
            return false;
        }

        if (!isValidEmail(email)) {
            showAlert("Please enter a valid email address.", "error");
            if (emailInput) emailInput.focus();
            return false;
        }

        if (!password) {
            showAlert("Please enter your password.", "error");
            if (passwordInput) passwordInput.focus();
            return false;
        }

        return true;
    }

    // Helper handler for forgot password link
    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener("click", (e) => {
            e.preventDefault();
            showAlert("Password reset is not yet configured for this demo.", "error");
        });
    }

    // Attach submission event
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            hideAlert();

            const email = emailInput ? emailInput.value.trim() : "";
            const password = passwordInput ? passwordInput.value : "";

            if (!validateForm(email, password)) {
                return;
            }

            // Set loading state on button
            const originalBtnText = loginBtn ? loginBtn.textContent : "Sign In";
            if (loginBtn) {
                loginBtn.disabled = true;
                loginBtn.textContent = "Signing in...";
            }

            try {
                const response = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                });

                let data = null;
                try {
                    data = await response.json();
                } catch (parseError) {
                    console.warn("Response body could not be parsed as JSON:", parseError);
                }

                if (response.status === 200 && data && data.access_token) {
                    // Store JWT access token
                    if (window.auth && typeof window.auth.setToken === "function") {
                        window.auth.setToken(data.access_token);
                    } else {
                        localStorage.setItem("ecommerce_token", data.access_token);
                    }

                    // Retrieve user profile and cache in localStorage
                    if (window.auth && typeof window.auth.fetchCurrentUser === "function") {
                        await window.auth.fetchCurrentUser();
                    }

                    showAlert("Signed in successfully! Redirecting to store...", "success");

                    setTimeout(() => {
                        window.location.href = "../index.html";
                    }, 800);
                } else if (response.status === 401) {
                    showAlert("Invalid email or password. Please try again.", "error");
                    if (passwordInput) {
                        passwordInput.value = "";
                        passwordInput.focus();
                    }
                } else if (response.status === 422) {
                    let message = "Invalid email or password format.";
                    if (data && data.detail) {
                        if (Array.isArray(data.detail) && data.detail.length > 0) {
                            message = data.detail.map(err => err.msg || "Invalid field").join(", ");
                        } else if (typeof data.detail === "string") {
                            message = data.detail;
                        }
                    }
                    showAlert(message, "error");
                } else {
                    const message = (data && data.detail) 
                        ? data.detail 
                        : `Login failed (status ${response.status}). Please try again.`;
                    showAlert(message, "error");
                }
            } catch (networkError) {
                console.error("Network or connection error:", networkError);
                showAlert("Could not connect to the server. Please ensure the backend is running and try again.", "error");
            } finally {
                // Restore button state (unless redirecting on success)
                if (loginBtn && (!alertBox || !alertBox.classList.contains("success"))) {
                    loginBtn.disabled = false;
                    loginBtn.textContent = originalBtnText;
                }
            }
        });
    }
});
