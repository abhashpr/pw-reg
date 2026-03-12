<template>
  <div class="container">
    <div class="card">
      <div class="header">
        <div class="header-content">
          <span class="header-icon"><i class="pi pi-sliders-v"></i></span>
          <div>
            <h1>Results Administration</h1>
            <p class="subtitle">Upload and manage student results</p>
          </div>
        </div>
        <router-link to="/admin" class="btn btn-secondary">← Back to Admin</router-link>
      </div>

      <div class="upload-section">
        <div class="section-header">
          <span class="section-icon"><i class="pi pi-upload"></i></span>
          <h3>Upload Results</h3>
        </div>
        <form @submit.prevent="handleUpload" class="upload-form">
          <div class="form-row">
            <div class="form-group">
              <label>Excel File <span class="required">*</span></label>
              <div class="file-input-wrapper">
                <input type="file" ref="excel" accept=".xlsx,.xls" required />
                <span class="file-hint">Accepts .xlsx or .xls files</span>
              </div>
            </div>
            <div class="form-group">
              <label>JSON Mapping Config <span class="optional">(optional)</span></label>
              <div class="file-input-wrapper">
                <input type="file" ref="config" accept="application/json" />
                <span class="file-hint">Custom column mapping</span>
              </div>
            </div>
          </div>
          <div class="actions">
            <button class="btn btn-primary" :disabled="loading">
              <span v-if="loading" class="spinner"></span>
              {{ loading ? 'Uploading...' : 'Upload Results' }}
            </button>
            <button class="btn btn-secondary" type="button" @click="fetchResults"><i class="pi pi-refresh"></i> Refresh</button>
            <button class="btn btn-danger" type="button" @click="truncateResults" :disabled="loading || results.length === 0">
              <i class="pi pi-trash"></i> Truncate All Records
            </button>
          </div>
        </form>
      </div>

      <div v-if="error" class="alert alert-error">
        <span class="alert-icon"><i class="pi pi-warning"></i></span> {{ error }}
      </div>

      <div v-if="results.length" class="results-section">
        <div class="section-header">
          <span class="section-icon"><i class="pi pi-table"></i></span>
          <h3>Imported Results</h3>
          <span class="badge">{{ results.length }} records</span>
        </div>
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th class="col-num">#</th>
                <th class="col-name">Name</th>
                <th class="col-phone">Phone</th>
                <th class="col-pct">Percentage</th>
                <th class="col-rank">Rank</th>
                <th class="col-source">Source</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(r, i) in paginatedResults" :key="r.id">
                <td class="col-num">{{ (currentPage - 1) * pageSize + i + 1 }}</td>
                <td class="col-name">{{ r.name }}</td>
                <td class="col-phone">{{ r.phone }}</td>
                <td class="col-pct"><span class="pct-badge">{{ r.percentage }}%</span></td>
                <td class="col-rank"><span class="rank-badge">#{{ r.rank }}</span></td>
                <td class="col-source"><span class="source-tag">{{ r.source_file }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="pagination">
          <button class="btn-page" :disabled="currentPage === 1" @click="currentPage--">← Prev</button>
          <div class="page-info">
            Page <select v-model="currentPage" class="page-select">
              <option v-for="p in totalPages" :key="p" :value="p">{{ p }}</option>
            </select> of {{ totalPages }}
          </div>
          <div class="page-size-select">
            <label>Show:</label>
            <select v-model="pageSize" @change="currentPage = 1">
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
          </div>
          <button class="btn-page" :disabled="currentPage === totalPages" @click="currentPage++">Next →</button>
        </div>
      </div>

      <div v-else-if="!loading" class="empty-state">
        <span class="empty-icon">📭</span>
        <p>No results imported yet</p>
        <span class="empty-hint">Upload an Excel file to get started</span>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { resultsAPI } from '../api/client'

const results = ref([])
const loading = ref(false)
const error = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

const totalPages = computed(() => Math.max(1, Math.ceil(results.value.length / pageSize.value)))

const paginatedResults = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return results.value.slice(start, start + pageSize.value)
})

const fetchResults = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await resultsAPI.listResultsAdmin()
    results.value = res.data
    if (currentPage.value > totalPages.value) {
      currentPage.value = totalPages.value
    }
  } catch (err) {
    error.value = 'Failed to fetch results.'
  } finally {
    loading.value = false
  }
}

const truncateResults = async () => {
  if (!confirm(`Delete all ${results.value.length} imported result record(s)?\nThis cannot be undone.`)) {
    return
  }

  loading.value = true
  error.value = ''
  try {
    await resultsAPI.truncateResults()
    results.value = []
    currentPage.value = 1
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to remove all results.'
  } finally {
    loading.value = false
  }
}

const handleUpload = async () => {
  const excelEl = document.querySelector('input[ref]')
  // fallback to refs not available easily here
  const excel = document.querySelector('input[ref="excel"]') || document.querySelector('input[type=file]')
  const config = document.querySelector('input[ref="config"]')

  if (!excel || !excel.files || excel.files.length === 0) {
    error.value = 'Select an Excel file to upload.'
    return
  }

  const formData = new FormData()
  formData.append('excel_file', excel.files[0])
  if (config && config.files && config.files.length) formData.append('config_file', config.files[0])

  loading.value = true
  error.value = ''
  try {
    const res = await resultsAPI.uploadResults(formData)
    await fetchResults()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Upload failed.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchResults)
</script>

<style scoped>
.container {
  width: 100vw;
  min-width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
  margin: 0;
  overflow-x: hidden;
  box-sizing: border-box;
}

.card {
  background: white;
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  max-width: 1100px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  font-size: 20px;
}

h1 {
  color: #333;
  margin: 0;
  font-size: 24px;
  font-weight: 700;
}

.subtitle {
  color: #666;
  font-size: 14px;
  margin: 4px 0 0 0;
}

.btn {
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102,126,234,0.4);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f5f5f5;
  color: #444;
  border: 1px solid #e0e0e0;
}

.btn-secondary:hover {
  background: #eaeaea;
}

.btn-danger {
  background: #fff1f2;
  color: #be123c;
  border: 1px solid #fecdd3;
}

.btn-danger:hover:not(:disabled) {
  background: #e11d48;
  color: white;
  border-color: #e11d48;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.upload-section {
  background: #fafafa;
  border: 2px dashed #e0e0e0;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.section-icon {
  font-size: 14px;
}

.badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  margin-left: auto;
}

.upload-form .form-row {
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
}

.required {
  color: #e53e3e;
}

.optional {
  color: #999;
  font-weight: 400;
}

.file-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.file-input-wrapper input[type="file"] {
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.file-input-wrapper input[type="file"]:hover {
  border-color: #667eea;
}

.file-hint {
  font-size: 12px;
  color: #888;
}

.actions {
  display: flex;
  gap: 12px;
}

.alert {
  padding: 16px 20px;
  border-radius: 10px;
  margin-bottom: 24px;
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
  margin-top: 8px;
}

.table-wrapper {
  overflow-x: auto;
  border-radius: 12px;
  border: 1px solid #e8e8e8;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table thead {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.data-table th {
  padding: 14px 16px;
  text-align: left;
  font-weight: 600;
  color: #444;
  border-bottom: 2px solid #e0e0e0;
  white-space: nowrap;
}

.data-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #f0f0f0;
  color: #333;
}

.data-table tbody tr:hover {
  background: #fafafa;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.col-num {
  width: 50px;
  text-align: center;
  color: #999;
}

.col-name {
  font-weight: 600;
}

.col-phone {
  font-family: monospace;
  color: #666;
}

.pct-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 13px;
}

.rank-badge {
  background: #48bb78;
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 13px;
}

.source-tag {
  background: #edf2f7;
  color: #4a5568;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-family: monospace;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #888;
}

.empty-icon {
  font-size: 64px;
  display: block;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 18px;
  color: #555;
  margin: 0 0 8px 0;
}

.empty-hint {
  font-size: 14px;
  color: #999;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .upload-form .form-row {
    grid-template-columns: 1fr;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .data-table {
    font-size: 13px;
  }
  
  .data-table th,
  .data-table td {
    padding: 10px 12px;
  }
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 0 0 12px 12px;
  margin-top: 16px;
}

.btn-page {
  padding: 10px 18px;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  background: white;
  color: #333;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-page:hover:not(:disabled) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #555;
}

.page-select {
  padding: 6px 12px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.page-size-select {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #666;
}

.page-size-select select {
  padding: 6px 10px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
}
</style>
