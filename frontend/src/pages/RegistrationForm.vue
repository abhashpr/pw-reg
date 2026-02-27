<template>
  <div class="container">
    <div class="card">
      <h1>Registration Form</h1>
      <p class="subtitle">Fill in your details below</p>

      <div v-if="slotsLoading" class="loading">Loading form configuration...</div>

      <form v-else @submit.prevent="handleSubmit">

        <!-- Row 1: Name + Father Name -->
        <div class="form-row">
          <div class="form-group">
            <label for="name">Name of Student *</label>
            <input id="name" v-model="form.name" type="text" placeholder="Full name" required :disabled="loading" />
          </div>
          <div class="form-group">
            <label for="father_name">Father's Name *</label>
            <input id="father_name" v-model="form.father_name" type="text" placeholder="Father's full name" required :disabled="loading" />
          </div>
        </div>

        <!-- Row 2: Medium + Course -->
        <div class="form-row">
          <div class="form-group">
            <label for="medium">Medium *</label>
            <select id="medium" v-model="form.medium" required :disabled="loading">
              <option value="" disabled>Select medium</option>
              <option value="Hindi">Hindi</option>
              <option value="English">English</option>
            </select>
          </div>
          <div class="form-group">
            <label for="course">Course Opted for *</label>
            <select id="course" v-model="form.course" required :disabled="loading">
              <option value="" disabled>Select course</option>
              <option value="Engineering (JEE)">Engineering (JEE)</option>
              <option value="Medical (NEET)">Medical (NEET)</option>
              <option value="Foundation (Class 6-10)">Foundation (Class 6-10)</option>
            </select>
          </div>
        </div>

        <!-- Exam Centre -->
        <div class="form-group full-width">
          <label for="exam_centre">Exam Centre *</label>
          <select id="exam_centre" v-model="form.exam_centre" required :disabled="loading" @change="onCentreChange">
            <option value="" disabled>Select exam centre</option>
            <option v-for="centre in centres" :key="centre" :value="centre">{{ centre }}</option>
          </select>
        </div>

        <!-- Date of Exam -->
        <div class="form-group full-width" v-if="availableDates.length">
          <label for="exam_date">Date of Exam *</label>
          <select id="exam_date" v-model="form.exam_date" required :disabled="loading" @change="onDateChange">
            <option value="" disabled>Select date</option>
            <option v-for="date in availableDates" :key="date" :value="date">{{ date }}</option>
          </select>
        </div>

        <!-- Exam Time Slot -->
        <div class="form-group full-width" v-if="availableSlots.length">
          <label for="exam_time">Exam Time Slot *</label>
          <select id="exam_time" v-model="form.exam_time" required :disabled="loading">
            <option value="" disabled>Select time slot</option>
            <option v-for="slot in availableSlots" :key="slot" :value="slot">{{ slot }}</option>
          </select>
          <div v-if="availableSlots.length === 1" class="hint">Only one slot available for this date at this centre.</div>
        </div>

        <!-- Summary -->
        <div v-if="form.exam_centre && form.exam_date && form.exam_time" class="selection-summary">
          <div class="summary-row"><span class="summary-label">Centre:</span>&nbsp;{{ form.exam_centre }}</div>
          <div class="summary-row"><span class="summary-label">Date:</span>&nbsp;{{ form.exam_date }}</div>
          <div class="summary-row"><span class="summary-label">Time:</span>&nbsp;{{ form.exam_time }}</div>
        </div>

        <div class="button-group">
          <button type="submit" class="btn btn-primary" :disabled="loading || !form.exam_time">
            {{ loading ? 'Saving...' : isUpdate ? 'Update Form' : 'Save Form' }}
          </button>
          <router-link to="/dashboard" class="btn btn-secondary">Go to Dashboard</router-link>
        </div>

        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { registrationAPI, configAPI } from '../api/client'
import { authStore } from '../store/auth'

const router = useRouter()

const form = reactive({
  name: '',
  father_name: '',
  medium: '',
  course: '',
  exam_centre: '',
  exam_date: '',
  exam_time: ''
})

const loading = ref(false)
const slotsLoading = ref(true)
const error = ref('')
const success = ref('')
const isUpdate = ref(false)
const examSlots = ref({})

const centres = computed(() => Object.keys(examSlots.value?.centres || {}))

const availableDates = computed(() => {
  if (!form.exam_centre || !examSlots.value?.centres) return []
  return Object.keys(examSlots.value.centres[form.exam_centre]?.dates || {})
})

const availableSlots = computed(() => {
  if (!form.exam_centre || !form.exam_date || !examSlots.value?.centres) return []
  return examSlots.value.centres[form.exam_centre]?.dates[form.exam_date]?.slots || []
})

const onCentreChange = () => {
  form.exam_date = ''
  form.exam_time = ''
  if (availableDates.value.length === 1) {
    form.exam_date = availableDates.value[0]
    onDateChange()
  }
}

const onDateChange = () => {
  form.exam_time = ''
  if (availableSlots.value.length === 1) {
    form.exam_time = availableSlots.value[0]
  }
}

onMounted(async () => {
  try {
    const slotsResponse = await configAPI.getExamSlots()
    examSlots.value = slotsResponse.data
  } catch (err) {
    error.value = 'Failed to load exam configuration. Please refresh.'
  } finally {
    slotsLoading.value = false
  }

  try {
    const response = await registrationAPI.getRegistration()
    if (response.data) {
      form.name = response.data.name
      form.father_name = response.data.father_name
      form.medium = response.data.medium
      form.course = response.data.course
      form.exam_centre = response.data.exam_centre
      form.exam_date = response.data.exam_date
      form.exam_time = response.data.exam_time || ''
      isUpdate.value = true
    }
  } catch (err) {
    isUpdate.value = false
  }
})

const handleSubmit = async () => {
  if (!form.exam_centre || !form.exam_date || !form.exam_time) {
    error.value = 'Please select an exam centre, date and time slot.'
    return
  }
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    await registrationAPI.createOrUpdate(form)
    success.value = 'Form saved successfully!'
    isUpdate.value = true
    setTimeout(() => { router.push('/dashboard') }, 1500)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to save form. Please try again.'
  } finally {
    loading.value = false
  }
}

if (!authStore.isAuthenticated()) { router.push('/login') }
</script>

<style scoped>
.container { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; }
.card { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); width: 100%; max-width: 640px; }
h1 { color: #333; margin: 0 0 10px 0; text-align: center; font-size: 28px; }
.subtitle { color: #666; text-align: center; margin: 0 0 30px 0; font-size: 14px; }
.loading { text-align: center; color: #888; padding: 40px 0; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
.form-group { display: flex; flex-direction: column; margin-bottom: 20px; }
.form-group.full-width { width: 100%; }
label { margin-bottom: 8px; color: #333; font-weight: 500; font-size: 14px; }
input, select { padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; transition: border-color 0.3s; background: white; color: #333; }
input:focus, select:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.1); }
input:disabled, select:disabled { background-color: #f5f5f5; color: #999; cursor: not-allowed; }
.hint { font-size: 12px; color: #888; margin-top: 4px; }
.selection-summary { background: linear-gradient(135deg, #f0f4ff, #f8f0ff); border: 1px solid #c5d0f5; border-radius: 8px; padding: 14px 18px; margin-bottom: 20px; }
.summary-row { padding: 4px 0; font-size: 14px; color: #444; }
.summary-label { font-weight: 600; color: #333; }
.button-group { display: flex; gap: 10px; margin-top: 10px; }
.btn { flex: 1; padding: 12px; border: none; border-radius: 5px; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s; text-decoration: none; text-align: center; display: flex; align-items: center; justify-content: center; }
.btn-primary { background: #667eea; color: white; }
.btn-primary:hover:not(:disabled) { background: #5568d3; transform: translateY(-2px); box-shadow: 0 5px 20px rgba(102,126,234,0.4); }
.btn-secondary { background: #e0e0e0; color: #333; }
.btn-secondary:hover { background: #d0d0d0; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.alert { padding: 12px; border-radius: 5px; margin-top: 20px; font-size: 14px; text-align: center; }
.alert-error { background-color: #fee; color: #c33; border: 1px solid #fcc; }
.alert-success { background-color: #efe; color: #3c3; border: 1px solid #cfc; }
@media (max-width: 600px) { .form-row { grid-template-columns: 1fr; } .button-group { flex-direction: column; } }
</style>
