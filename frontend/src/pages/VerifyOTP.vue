<template>
  <div class="container">
    <div class="card">
      <h1>Verify OTP</h1>
      <p class="subtitle">Enter the 6-digit code sent to your email</p>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="email">Email Address</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="Enter your email"
            required
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="otp">OTP Code</label>
          <input
            id="otp"
            v-model="otp"
            type="text"
            placeholder="000000"
            maxlength="6"
            @input="otp = otp.replace(/[^0-9]/g, '')"
            required
            :disabled="loading"
          />
          <div class="otp-hint">Enter 6 digits</div>
        </div>

        <button type="submit" class="btn btn-primary" :disabled="loading || otp.length !== 6">
          {{ loading ? 'Verifying...' : 'Verify OTP' }}
        </button>

        <button type="button" class="btn btn-secondary" @click="goBack" :disabled="loading">
          Back to Login
        </button>

        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>
      </form>

      <p class="hint">
        Didn't receive an OTP? <router-link to="/login">Send another one</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '../api/client'
import { authStore } from '../store/auth'

const router = useRouter()
const email = ref('')
const otp = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

onMounted(() => {
  // Get email from session storage
  const pendingEmail = sessionStorage.getItem('pending_email')
  if (pendingEmail) {
    email.value = pendingEmail
  } else {
    router.push('/login')
  }
})

const handleSubmit = async () => {
  error.value = ''
  success.value = ''
  loading.value = true

  try {
    const response = await authAPI.verifyOTP(email.value, otp.value)
    const token = response.data.access_token

    success.value = 'OTP verified! Redirecting...'
    authStore.setToken(token, email.value)
    sessionStorage.removeItem('pending_email')

    setTimeout(() => {
      router.push('/dashboard')
    }, 1500)
  } catch (err) {
    const message = err.response?.data?.detail || 'Failed to verify OTP. Please try again.'
    error.value = message
    console.error('Verify OTP error:', err)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  sessionStorage.removeItem('pending_email')
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
  max-width: 400px;
}

h1 {
  color: #333;
  margin: 0 0 10px 0;
  text-align: center;
  font-size: 28px;
}

.subtitle {
  color: #666;
  text-align: center;
  margin: 0 0 30px 0;
  font-size: 14px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
  font-size: 14px;
}

input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  box-sizing: border-box;
  transition: border-color 0.3s;
  letter-spacing: 2px;
  text-align: center;
  font-family: monospace;
}

input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

input:disabled {
  background-color: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

.otp-hint {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 10px;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #e0e0e0;
  color: #333;
}

.btn-secondary:hover:not(:disabled) {
  background: #d0d0d0;
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

.alert-success {
  background-color: #efe;
  color: #3c3;
  border: 1px solid #cfc;
}

.hint {
  text-align: center;
  color: #999;
  font-size: 12px;
  margin-top: 20px;
}

.hint a {
  color: #667eea;
  text-decoration: none;
}

.hint a:hover {
  text-decoration: underline;
}
</style>
