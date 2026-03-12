import axios from 'axios'
import { authStore } from '../store/auth'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add token to requests
client.interceptors.request.use((config) => {
  const token = authStore.getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle errors
client.interceptors.response.use(
  (response) => response,
  (error) => {
    // Logout if unauthorized
    if (error.response?.status === 401) {
      const wasAdmin = authStore.isAdmin()
      authStore.logout()
      // Redirect admins to admin login, others to public results
      window.location.href = wasAdmin ? '/admin/login' : '/results'
    }
    return Promise.reject(error)
  }
)

/**
 * Authentication API calls.
 */
export const authAPI = {
  // sendOTP now accepts a payload object: { email, admin?, admin_token? }
  sendOTP: (payload) => client.post('/auth/send-otp', payload),
  verifyOTP: (email, otp) => client.post('/auth/verify-otp', { email, otp }),
  getCurrentUser: () => client.get('/auth/me')
}

/**
 * Registration API calls.
 */
export const registrationAPI = {
  createOrUpdate: (data) => client.post('/registration/', data),
  getRegistration: () => client.get('/registration/'),
  downloadAdmitCard: () => client.get('/registration/admit-card', { responseType: 'blob' })
}

/**
 * Admin API calls.
 */
export const adminAPI = {
  listUsers: () => client.get('/admin/users'),
  downloadAdmitCard: (userId) => client.get(`/admin/users/${userId}/admit-card`, { responseType: 'blob' }),
  sendAdmitCard: (userId) => client.post(`/admin/users/${userId}/send-admit-card`),
  deleteUser: (userId) => client.delete(`/admin/users/${userId}`),
  bulkSendAdmitCards: (userIds) => client.post('/admin/users/bulk-send', { user_ids: userIds }),
  bulkDeleteUsers: (userIds) => client.post('/admin/users/bulk-delete', { user_ids: userIds })
}

/**
 * Results API (admin + public)
 */
export const resultsAPI = {
  uploadResults: (formData) => client.post('/results/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  listResultsAdmin: () => client.get('/results/admin'),
  truncateResults: () => client.delete('/results/admin/truncate'),
  searchResult: (params) => client.get('/results/search', { params })
}

/**
 * Config API calls.
 */
export const configAPI = {
  getExamSlots: () => client.get('/config/exam-slots')
}

export default client
