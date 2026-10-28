/* ==========================================================================
   Central Authentication Module (auth.js)
   Handles API communication, JWT token storage, user session state,
   and authentication headers.
   ========================================================================== */

(() => {
    const API_BASE_URL = "http://localhost:8000";
    const TOKEN_KEY = "ecommerce_token";
    const USER_KEY = "ecommerce_user";

    const auth = {
        API_BASE_URL,

        /**
         * Retrieve the stored JWT token from localStorage.
         * @returns {string|null}
         */
        getToken() {
            return localStorage.getItem(TOKEN_KEY);
        },

        /**
         * Save the JWT token into localStorage.
         * @param {string} token
         */
        setToken(token) {
            if (!token) return;
            localStorage.setItem(TOKEN_KEY, token);
        },

        /**
         * Remove the JWT token from localStorage.
         */
        removeToken() {
            localStorage.removeItem(TOKEN_KEY);
        },

        /**
         * Get the cached user profile object from localStorage.
         * @returns {object|null}
         */
        getCurrentUser() {
            const raw = localStorage.getItem(USER_KEY);
            if (!raw) return null;
            try {
                return JSON.parse(raw);
            } catch (e) {
                console.error("Failed to parse cached user data:", e);
                localStorage.removeItem(USER_KEY);
                return null;
            }
        },

        /**
         * Cache the user profile object in localStorage.
         * @param {object} user
         */
        setCurrentUser(user) {
            if (!user) return;
            localStorage.setItem(USER_KEY, JSON.stringify(user));
        },

        /**
         * Remove the cached user profile from localStorage.
         */
        removeCurrentUser() {
            localStorage.removeItem(USER_KEY);
        },

        /**
         * Clear all authentication state (both token and user profile).
         */
        clearAuth() {
            this.removeToken();
            this.removeCurrentUser();
        },

        /**
         * Check if a token currently exists in storage.
         * @returns {boolean}
         */
        isAuthenticated() {
            return !!this.getToken();
        },

        /**
         * Verify session and retrieve fresh user details from GET /auth/me.
         * Automatically clears auth state if token is expired (401).
         * @returns {Promise<object|null>}
         */
        async fetchCurrentUser() {
            const token = this.getToken();
            if (!token) {
                this.clearAuth();
                return null;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/auth/me`, {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                });

                if (response.status === 401) {
                    console.warn("Session expired or invalid token; clearing auth state.");
                    this.clearAuth();
                    return null;
                }

                if (!response.ok) {
                    throw new Error(`Server returned status ${response.status}`);
                }

                const userData = await response.json();
                this.setCurrentUser(userData);
                return userData;
            } catch (error) {
                console.error("fetchCurrentUser error:", error);
                return null;
            }
        },

        /**
         * Log out current user, clear state, and optionally redirect.
         * @param {string|null} redirectUrl
         */
        logout(redirectUrl = null) {
            this.clearAuth();
            if (redirectUrl) {
                window.location.href = redirectUrl;
            }
        },

        /**
         * Helper to perform authenticated fetch requests.
         * Automatically injects Authorization header and Content-Type.
         * @param {string} endpoint - Relative path (e.g., '/products') or full URL
         * @param {object} options - fetch options
         * @returns {Promise<Response>}
         */
        async authFetch(endpoint, options = {}) {
            const url = endpoint.startsWith("http") ? endpoint : `${API_BASE_URL}${endpoint}`;
            const token = this.getToken();

            const headers = {
                "Content-Type": "application/json",
                ...(options.headers || {})
            };

            if (token) {
                headers["Authorization"] = `Bearer ${token}`;
            }

            const response = await fetch(url, {
                ...options,
                headers
            });

            if (response.status === 401) {
                this.clearAuth();
            }

            return response;
        }
    };

    // Expose globally for vanilla JS multi-page usage
    window.auth = auth;
})();
