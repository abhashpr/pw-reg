/**
 * Authentication store for managing JWT token and auth state.
 */

class AuthStore {
  constructor() {
    this.token = localStorage.getItem('auth_token')
    this.email = localStorage.getItem('user_email')
    this.admin = localStorage.getItem('is_admin') === 'true'
  }

  /**
   * Set authentication token and email.
   */
  setToken(token, email, isAdmin = false) {
    this.token = token
    this.email = email
    this.admin = isAdmin
    localStorage.setItem('auth_token', token)
    localStorage.setItem('user_email', email)
    localStorage.setItem('is_admin', String(isAdmin))
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
   * Check if user is admin.
   */
  isAdmin() {
    return this.admin === true
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
    this.admin = false
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_email')
    localStorage.removeItem('is_admin')
  }
}

export const authStore = new AuthStore()
