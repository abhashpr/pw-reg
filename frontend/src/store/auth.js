/**
 * Authentication store for managing JWT token and auth state.
 */

class AuthStore {
  constructor() {
    this.token = localStorage.getItem('auth_token')
    this.email = localStorage.getItem('user_email')
  }

  /**
   * Set authentication token and email.
   */
  setToken(token, email) {
    this.token = token
    this.email = email
    localStorage.setItem('auth_token', token)
    localStorage.setItem('user_email', email)
  }

  /**
   * Get current token.
   */
  getToken() {
    return this.token
  }

  /**
   * Get authorization header value.
   */
  getAuthHeader() {
    return this.token ? `Bearer ${this.token}` : null
  }

  /**
   * Get user email.
   */
  getEmail() {
    return this.email
  }

  /**
   * Check if user is authenticated.
   */
  isAuthenticated() {
    return !!this.token
  }

  /**
   * Clear token and logout.
   */
  logout() {
    this.token = null
    this.email = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_email')
  }
}

export const authStore = new AuthStore()
