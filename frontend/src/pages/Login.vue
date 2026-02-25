<template>
  <div class="container">
    <div class="card">
      <h1>PWNSAT Registration</h1>
      <p class="subtitle">Login with your email to continue</p>

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

        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? 'Sending...' : 'Send OTP' }}
        </button>

        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>
      </form>

      <p class="hint">
        A 6-digit OTP will be sent to your email. It will expire in 5 minutes.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '../api/client'
import { authStore } from '../store/auth'

const router = useRouter()
const email = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

const handleSubmit = async () => {
  error.value = ''
  success.value = ''
  loading.value = true

  try {
    await authAPI.sendOTP(email.value)
    success.value = 'OTP sent! Check your email.'
    
    // Store email for next step
    sessionStorage.setItem('pending_email', email.value)
    
    // Redirect to OTP verification
    setTimeout(() => {
      router.push('/verify-otp')
    }, 1500)
  } catch (err) {
    const message = err.response?.data?.detail || 'Failed to send OTP. Please try again.'
    error.value = message
    console.error('Send OTP error:', err)
  } finally {
    loading.value = false
  }
}

// If already logged in, redirect to dashboard
if (authStore.isAuthenticated()) {
  router.push('/dashboard')
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

.btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
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
</style>
