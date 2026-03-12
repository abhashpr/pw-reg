<template>
  <div class="container">
    <div class="card">
      <div class="header">
        <div class="icon"><icon class="pi pi-search"></icon></div>
        <h1>Check Your Result</h1>
        <p class="subtitle">Enter your details to view your NSAT result</p>
      </div>

      <form @submit.prevent="search">
        <div class="form-row">
          <div class="form-group">
            <label for="name">Name</label>
            <input id="name" v-model="name" type="text" placeholder="Enter your full name" />
          </div>
          <div class="form-group">
            <label for="phone">Phone</label>
            <input id="phone" v-model="phone" type="text" placeholder="Enter phone number" />
          </div>
        </div>

        <div class="actions">
          <button class="btn btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            {{ loading ? 'Searching...' : 'Search Result' }}
          </button>
        </div>
      </form>

      <div v-if="error" class="alert alert-error">
        <span class="alert-icon">⚠️</span> {{ error }}
      </div>

      <div v-if="result" class="results-section">
        <div class="result-card">
          <div class="result-header">
            <span class="result-icon"><icon class="pi pi-bookmark-fill"></icon></span>
            <h2>Your Result</h2>
          </div>
          <div class="result-body">
            <div class="detail-row">
              <span class="label">Name</span>
              <span class="value">{{ result.name }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Phone</span>
              <span class="value">{{ result.phone }}</span>
            </div>
            <div class="detail-row highlight">
              <span class="label">Percentage</span>
              <span class="value percentage">{{ result.percentage }}%</span>
            </div>
            <div class="detail-row highlight">
              <span class="label mr-1"><icon class="pi pi-sparkles"></icon> Rank</span>
              <span class="value rank">#{{ result.rank }}</span>
            </div>
          </div>
        </div>

        <div v-if="result.scholarship" class="scholarship-card">
          <div class="scholarship-header">
            <span class="scholarship-icon">{{ scholarshipEmoji(result.scholarship.scholarship) }}</span>
            <h2>Scholarship Award</h2>
          </div>
          <div class="scholarship-body">
            <div class="scholarship-percentage">
              <span class="big-number">{{ result.scholarship.scholarship }}%</span>
              <span class="label">Scholarship</span>
            </div>
            <div class="scholarship-message">
              {{ result.scholarship.message }}
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { resultsAPI } from '../api/client'

const scholarshipEmoji = (val) => {
  // val is scholarship percentage or code
  if (val == null) return ''
  try {
    const n = Number(val)
    if (isNaN(n)) return '🎁'
    if (n >= 80) return '🏆'
    if (n >= 60) return '🎓'
    if (n >= 40) return '🌟'
    if (n > 0) return '👍'
    return '🙏'
  } catch (e) {
    return '🎁'
  }
}

const name = ref('')
const phone = ref('')
const loading = ref(false)
const error = ref('')
const result = ref(null)

const search = async () => {
  error.value = ''
  result.value = null
  loading.value = true
  try {
    const res = await resultsAPI.searchResult({ name: name.value, phone: phone.value })
    console.log("Result Data", res.data)
    result.value = res.data
  } catch (err) {
    if (err.response?.status === 404) {
      error.value = 'No matching result found.'
    } else {
      error.value = 'Search failed. Try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100vw;
  min-width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  margin: 0;
  overflow-x: hidden;
  box-sizing: border-box;
}

.card {
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  width: 100%;
  max-width: 700px;
}

.header {
  text-align: center;
  margin-bottom: 28px;
}

.header .icon {
  font-size: 20px;
  margin-bottom: 12px;
}

h1 {
  color: #333;
  margin: 0 0 8px 0;
  font-size: 26px;
  font-weight: 700;
}

.subtitle {
  color: #666;
  font-size: 14px;
  margin: 0;
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

.form-group label {
  margin-bottom: 8px;
  color: #444;
  font-weight: 600;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-group input {
  padding: 14px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 15px;
  transition: all 0.2s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102,126,234,0.15);
}

.form-group input::placeholder {
  color: #aaa;
}

.actions {
  margin-top: 24px;
}

.btn {
  width: 100%;
  padding: 16px 24px;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102,126,234,0.4);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.alert {
  padding: 16px 20px;
  border-radius: 10px;
  margin-top: 20px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.alert-error {
  background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
  color: #c53030;
  border: 1px solid #feb2b2;
}

.alert-icon {
  font-size: 18px;
}

.results-section {
  margin-top: 32px;
}

.result-card, .scholarship-card {
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

.result-card {
  border: 2px solid #e8e8e8;
}

.result-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid #e0e0e0;
}

.result-header h2 {
  margin: 0;
  font-size: 14px;
  color: #333;
}

.result-icon {
  font-size: 16px;
  color: #999;
}

.result-body {
  padding: 8px 0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row .label {
  color: #666;
  font-size: 14px;
}

.detail-row .value {
  color: #333;
  font-weight: 600;
  font-size: 15px;
}

.detail-row.highlight {
  background: #fafafa;
}

.detail-row .percentage {
  color: #667eea;
  font-size: 20px;
  font-weight: 700;
}

.detail-row .rank {
  color: #48bb78;
  font-size: 20px;
  font-weight: 700;
}

.scholarship-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.scholarship-header {
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.2);
}

.scholarship-header h2 {
  margin: 0;
  font-size: 20px;
  color: white;
}

.scholarship-icon {
  font-size: 32px;
}

.scholarship-body {
  padding: 24px;
  text-align: center;
}

.scholarship-percentage {
  margin-bottom: 16px;
}

.scholarship-percentage .big-number {
  display: block;
  font-size: 56px;
  font-weight: 800;
  line-height: 1;
  text-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.scholarship-percentage .label {
  font-size: 14px;
  opacity: 0.9;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-top: 8px;
  display: block;
}

.scholarship-message {
  font-size: 16px;
  line-height: 1.6;
  opacity: 0.95;
  padding: 16px 20px;
  background: rgba(255,255,255,0.15);
  border-radius: 10px;
  margin-top: 8px;
}

@media (max-width: 600px) {
  .card {
    padding: 28px 20px;
  }
  .form-row {
    grid-template-columns: 1fr;
  }
  .scholarship-percentage .big-number {
    font-size: 44px;
  }
}
</style>
