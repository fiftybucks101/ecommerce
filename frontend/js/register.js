/* ==========================================================================
   Sign-Up / Registration Page Logic (register.js)
   Handles client-side validation, POST /auth/register dispatch,
   alert feedback (success, duplicate email, validation errors),
   and automatic redirection to login.html.
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.getElementById("registerForm");
    const usernameInput = document.getElementById("usernameInput");
    const emailInput = document.getElementById("emailInput");
    const passwordInput = document.getElementById("passwordInput");
    const registerBtn = document.getElementById("registerBtn");
    const alertBox = document.getElementById("alertBox");

    // Standard API base URL fallback from auth helper or default
    const API_BASE_URL = (window.auth && window.auth.API_BASE_URL) 
        ? window.auth.API_BASE_URL 
        : "http://localhost:8000";

    /**
     * Show notification alert
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
     * Validate client-side inputs
     * @returns {boolean}
     */
    function validateForm(username, email, password) {
        if (!username) {
            showAlert("Please enter a username.", "error");
            if (usernameInput) usernameInput.focus();
            return false;
        }

        if (username.length > 100) {
            showAlert("Username cannot exceed 100 characters.", "error");
            if (usernameInput) usernameInput.focus();
            return false;
        }

        if (!email) {
            showAlert("Please enter an email address.", "error");
            if (emailInput) emailInput.focus();
            return false;
        }

        if (!isValidEmail(email)) {
            showAlert("Please enter a valid email address.", "error");
            if (emailInput) emailInput.focus();
            return false;
        }

        if (!password) {
            showAlert("Please enter a password.", "error");
            if (passwordInput) passwordInput.focus();
            return false;
        }

        if (password.length < 8) {
            showAlert("Password must be at least 8 characters long.", "error");
            if (passwordInput) passwordInput.focus();
            return false;
        }

        if (password.length > 128) {
            showAlert("Password cannot exceed 128 characters.", "error");
            if (passwordInput) passwordInput.focus();
            return false;
        }

        return true;
    }

    // Attach submission event
    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            hideAlert();

            const username = usernameInput ? usernameInput.value.trim() : "";
            const email = emailInput ? emailInput.value.trim() : "";
            const password = passwordInput ? passwordInput.value : "";

            if (!validateForm(username, email, password)) {
                return;
            }

            // Set loading state on button
            const originalBtnText = registerBtn ? registerBtn.textContent : "Sign Up";
            if (registerBtn) {
                registerBtn.disabled = true;
                registerBtn.textContent = "Creating account...";
            }

            try {
                const response = await fetch(`${API_BASE_URL}/auth/register`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        name: username,
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

                if (response.status === 201) {
                    showAlert("Account created successfully! Redirecting to login...", "success");
                    // Clear inputs
                    if (usernameInput) usernameInput.value = "";
                    if (emailInput) emailInput.value = "";
                    if (passwordInput) passwordInput.value = "";

                    setTimeout(() => {
                        window.location.href = "login.html";
                    }, 1500);
                } else if (response.status === 409) {
                    const message = (data && data.detail) 
                        ? data.detail 
                        : "Email is already registered. Please log in or use another email.";
                    showAlert(message, "error");
                    if (emailInput) emailInput.focus();
                } else if (response.status === 422) {
                    let message = "Validation failed. Please check your details.";
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
                        : `Registration failed (status ${response.status}). Please try again.`;
                    showAlert(message, "error");
                }
            } catch (networkError) {
                console.error("Network or connection error:", networkError);
                showAlert("Could not connect to the server. Please ensure the backend is running and try again.", "error");
            } finally {
                // Restore button state (unless redirecting on success)
                if (registerBtn && (!alertBox || !alertBox.classList.contains("success"))) {
                    registerBtn.disabled = false;
                    registerBtn.textContent = originalBtnText;
                }
            }
        });
    }
});
