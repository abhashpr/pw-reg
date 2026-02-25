<template>
  <div class="container">
    <div class="card">
      <div class="header">
        <h1>Dashboard</h1>
        <button class="btn btn-logout" @click="handleLogout">Logout</button>
      </div>

      <div class="user-info">
        <p><strong>Logged in as:</strong> {{ userEmail }}</p>
      </div>

      <div v-if="loading" class="loading">Loading your registration...</div>

      <div v-else-if="registration">
        <div class="registration-details">
          <h2>Your Registration Details</h2>

          <div class="detail-row">
            <span class="label">Roll Number:</span>
            <span class="value">{{ registration.roll_no }}</span>
          </div>

          <div class="detail-row">
            <span class="label">Name:</span>
            <span class="value">{{ registration.name }}</span>
          </div>

          <div class="detail-row">
            <span class="label">Father's Name:</span>
            <span class="value">{{ registration.father_name }}</span>
          </div>

          <div class="detail-row">
            <span class="label">Medium:</span>
            <span class="value">{{ registration.medium }}</span>
          </div>

          <div class="detail-row">
            <span class="label">Course:</span>
            <span class="value">{{ registration.course }}</span>
          </div>

          <div class="detail-row">
            <span class="label">Exam Date:</span>
            <span class="value">{{ registration.exam_date }}</span>
          </div>

          <div class="detail-row">
            <span class="label">Exam Centre:</span>
            <span class="value">{{ registration.exam_centre }}</span>
          </div>

          <div class="detail-row">
            <span class="label">Last Updated:</span>
            <span class="value">{{ formatDate(registration.updated_at) }}</span>
          </div>
        </div>

        <div class="actions">
          <router-link to="/registration" class="btn btn-secondary">
            Edit Registration
          </router-link>

          <button class="btn btn-success" @click="downloadAdmitCard" :disabled="downloadLoading">
            {{ downloadLoading ? 'Generating...' : 'Download Admit Card' }}
          </button>
        </div>
      </div>

      <div v-else>
        <div class="no-registration">
          <p>You haven't registered yet.</p>
          <router-link to="/registration" class="btn btn-primary">
            Complete Registration
          </router-link>
        </div>
      </div>

      <div v-if="error" class="alert alert-error">{{ error }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { registrationAPI } from '../api/client'
import { authStore } from '../store/auth'

const router = useRouter()
const registration = ref(null)
const userEmail = ref('')
const loading = ref(true)
const downloadLoading = ref(false)
const error = ref('')

onMounted(async () => {
  userEmail.value = authStore.getEmail()

  try {
    const response = await registrationAPI.getRegistration()
    registration.value = response.data
  } catch (err) {
    if (err.response?.status !== 404) {
      error.value = 'Failed to load registration. Please try again.'
      console.error('Load registration error:', err)
    }
  } finally {
    loading.value = false
  }
})

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-IN') + ' ' + date.toLocaleTimeString('en-IN')
}

const downloadAdmitCard = async () => {
  downloadLoading.value = true
  error.value = ''

  try {
    const response = await registrationAPI.downloadAdmitCard()

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url

    const rollNo = registration.value.roll_no
    link.setAttribute('download', `admit_card_${rollNo}.pdf`)

    document.body.appendChild(link)
    link.click()

    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    error.value = 'Failed to generate admit card. Please try again.'
    console.error('Download admit card error:', err)
  } finally {
    downloadLoading.value = false
  }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

// Redirect if not authenticated
if (!authStore.isAuthenticated()) {
  router.push('/login')
}
</script>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.card {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 600px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 20px;
}

h1 {
  color: #333;
  margin: 0;
  font-size: 28px;
}

h2 {
  color: #333;
  font-size: 20px;
  margin: 0 0 20px 0;
  border-bottom: 2px solid #667eea;
  padding-bottom: 10px;
}

.user-info {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
  color: #666;
}

.loading {
  text-align: center;
  color: #666;
  padding: 40px 0;
}

.registration-details {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 5px;
  margin-bottom: 20px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #e0e0e0;
}

.detail-row:last-child {
  border-bottom: none;
}

.label {
  font-weight: 600;
  color: #333;
  width: 40%;
}

.value {
  color: #666;
  text-align: right;
  width: 60%;
}

.no-registration {
  text-align: center;
  padding: 40px 0;
  color: #666;
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 30px;
}

.btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #e0e0e0;
  color: #333;
}

.btn-secondary:hover {
  background: #d0d0d0;
}

.btn-success {
  background: #4caf50;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(76, 175, 80, 0.4);
}

.btn-logout {
  background: #f44336;
  color: white;
  padding: 8px 16px;
  flex: none;
  width: auto;
}

.btn-logout:hover {
  background: #da190b;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.alert {
  padding: 12px;
  border-radius: 5px;
  margin-top: 20px;
  font-size: 14px;
  text-align: center;
}

.alert-error {
  background-color: #fee;
  color: #c33;
  border: 1px solid #fcc;
}

@media (max-width: 600px) {
  .actions {
    flex-direction: column;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
}
</style>
