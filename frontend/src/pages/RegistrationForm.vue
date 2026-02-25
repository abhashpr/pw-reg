<template>
  <div class="container">
    <div class="card">
      <h1>Registration Form</h1>
      <p class="subtitle">Fill in your details below</p>

      <form @submit.prevent="handleSubmit">
        <div class="form-row">
          <div class="form-group">
            <label for="name">Name of Student *</label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              placeholder="Full name"
              required
              :disabled="loading"
            />
          </div>

          <div class="form-group">
            <label for="father_name">Father's Name *</label>
            <input
              id="father_name"
              v-model="form.father_name"
              type="text"
              placeholder="Father's full name"
              required
              :disabled="loading"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="medium">Medium *</label>
            <input
              id="medium"
              v-model="form.medium"
              type="text"
              placeholder="e.g., English, Hindi"
              required
              :disabled="loading"
            />
          </div>

          <div class="form-group">
            <label for="course">Course Opted for *</label>
            <input
              id="course"
              v-model="form.course"
              type="text"
              placeholder="e.g., Engineering, Science"
              required
              :disabled="loading"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="exam_date">Date of Exam *</label>
            <input
              id="exam_date"
              v-model="form.exam_date"
              type="date"
              required
              :disabled="loading"
            />
          </div>

          <div class="form-group">
            <label for="exam_centre">Exam Centre *</label>
            <input
              id="exam_centre"
              v-model="form.exam_centre"
              type="text"
              placeholder="e.g., Centre A, New Delhi"
              required
              :disabled="loading"
            />
          </div>
        </div>

        <div class="button-group">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Saving...' : isUpdate ? 'Update Form' : 'Save Form' }}
          </button>
          <router-link to="/dashboard" class="btn btn-secondary">
            Go to Dashboard
          </router-link>
        </div>

        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { registrationAPI } from '../api/client'
import { authStore } from '../store/auth'

const router = useRouter()
const form = reactive({
  name: '',
  father_name: '',
  medium: '',
  course: '',
  exam_date: '',
  exam_centre: ''
})

const loading = ref(false)
const error = ref('')
const success = ref('')
const isUpdate = ref(false)

onMounted(async () => {
  // Check if already has registration
  try {
    const response = await registrationAPI.getRegistration()
    if (response.data) {
      form.name = response.data.name
      form.father_name = response.data.father_name
      form.medium = response.data.medium
      form.course = response.data.course
      form.exam_date = response.data.exam_date
      form.exam_centre = response.data.exam_centre
      isUpdate.value = true
    }
  } catch (err) {
    // No existing registration
    isUpdate.value = false
  }
})

const handleSubmit = async () => {
  error.value = ''
  success.value = ''
  loading.value = true

  try {
    await registrationAPI.createOrUpdate(form)
    success.value = 'Form saved successfully!'
    isUpdate.value = true

    setTimeout(() => {
      router.push('/dashboard')
    }, 1500)
  } catch (err) {
    const message = err.response?.data?.detail || 'Failed to save form. Please try again.'
    error.value = message
    console.error('Save form error:', err)
  } finally {
    loading.value = false
  }
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

label {
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
  font-size: 14px;
}

input {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
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

.button-group {
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

.btn-primary:hover:not(:disabled) {
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

@media (max-width: 600px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .button-group {
    flex-direction: column;
  }
}
</style>
