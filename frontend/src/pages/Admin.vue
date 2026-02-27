<template>
  <div class="admin-container">
    <div class="admin-card">

      <!-- Header -->
      <div class="header">
        <div class="header-left">
          <h1>Admin Panel</h1>
          <span class="badge">PWNSAT 2026</span>
        </div>
        <div class="header-right">
          <span class="admin-email">{{ userEmail }}</span>
          <router-link to="/dashboard" class="btn btn-secondary">Dashboard</router-link>
          <button class="btn btn-logout" @click="handleLogout">Logout</button>
        </div>
      </div>

      <!-- Stats bar -->
      <div class="stats-bar">
        <div class="stat">
          <span class="stat-value">{{ users.length }}</span>
          <span class="stat-label">Total Users</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ registeredCount }}</span>
          <span class="stat-label">Registered</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ unregisteredCount }}</span>
          <span class="stat-label">Pending</span>
        </div>
      </div>

      <!-- Search -->
      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by name, email, roll no, course, centre..."
          class="search-input"
        />
        <span class="search-count">{{ filteredUsers.length }} results</span>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading">Loading users...</div>

      <!-- Error -->
      <div v-if="error" class="alert alert-error">{{ error }}</div>

      <!-- Toast notification -->
      <div v-if="toast" class="toast" :class="toast.type">{{ toast.message }}</div>

      <!-- Table -->
      <div v-if="!loading" class="table-wrapper">
        <table class="users-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Email</th>
              <th>Roll No.</th>
              <th>Name</th>
              <th>Father's Name</th>
              <th>Medium</th>
              <th>Course</th>
              <th>Exam Date</th>
              <th>Exam Centre</th>
              <th>Exam Time</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(user, index) in filteredUsers" :key="user.id">
              <td class="td-index">{{ index + 1 }}</td>
              <td class="td-email">{{ user.email }}</td>
              <template v-if="user.registration">
                <td class="td-roll">{{ user.registration.roll_no }}</td>
                <td>{{ user.registration.name }}</td>
                <td>{{ user.registration.father_name }}</td>
                <td>{{ user.registration.medium }}</td>
                <td>{{ user.registration.course }}</td>
                <td>{{ user.registration.exam_date }}</td>
                <td>{{ user.registration.exam_centre }}</td>
                <td>{{ user.registration.exam_time || '-' }}</td>
                <td class="td-actions">
                  <button
                    class="btn-action btn-download"
                    :disabled="actionLoading[user.id]"
                    @click="downloadCard(user)"
                    title="Download Admit Card"
                  >
                    ⬇ Download
                  </button>
                  <button
                    class="btn-action btn-send"
                    :disabled="actionLoading[user.id]"
                    @click="sendCard(user)"
                    title="Send Admit Card via Email"
                  >
                    {{ actionLoading[user.id] === 'send' ? 'Sending...' : '✉ Send' }}
                  </button>
                </td>
              </template>
              <template v-else>
                <td colspan="7" class="td-no-reg">— Not Registered —</td>
                <td></td>
              </template>
            </tr>
            <tr v-if="filteredUsers.length === 0">
              <td colspan="10" class="td-empty">No users found.</td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { adminAPI } from '../api/client'
import { authStore } from '../store/auth'

const router = useRouter()
const users = ref([])
const searchQuery = ref('')
const loading = ref(true)
const error = ref('')
const userEmail = ref('')
const actionLoading = reactive({})
const toast = ref(null)

// Redirect non-admins
if (!authStore.isAdmin()) {
  router.push('/dashboard')
}

onMounted(async () => {
  userEmail.value = authStore.getEmail()
  await loadUsers()
})

const loadUsers = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await adminAPI.listUsers()
    users.value = response.data
  } catch (err) {
    error.value = 'Failed to load users. Please try again.'
    console.error('Admin load users error:', err)
  } finally {
    loading.value = false
  }
}

const registeredCount = computed(() =>
  users.value.filter(u => u.registration).length
)

const unregisteredCount = computed(() =>
  users.value.filter(u => !u.registration).length
)

const filteredUsers = computed(() => {
  const q = searchQuery.value.toLowerCase().trim()
  if (!q) return users.value
  return users.value.filter(u => {
    const r = u.registration
    return (
      u.email.toLowerCase().includes(q) ||
      (r && r.name.toLowerCase().includes(q)) ||
      (r && r.roll_no.toLowerCase().includes(q)) ||
      (r && r.course.toLowerCase().includes(q)) ||
      (r && r.exam_centre.toLowerCase().includes(q)) ||
      (r && r.father_name.toLowerCase().includes(q))
    )
  })
})

const showToast = (message, type = 'success') => {
  toast.value = { message, type }
  setTimeout(() => { toast.value = null }, 3500)
}

const downloadCard = async (user) => {
  actionLoading[user.id] = 'download'
  try {
    const response = await adminAPI.downloadAdmitCard(user.id)
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `admit_card_${user.registration.roll_no}.pdf`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    showToast('Failed to download admit card.', 'error')
    console.error('Download error:', err)
  } finally {
    delete actionLoading[user.id]
  }
}

const sendCard = async (user) => {
  actionLoading[user.id] = 'send'
  try {
    await adminAPI.sendAdmitCard(user.id)
    showToast(`Admit card sent to ${user.email}`, 'success')
  } catch (err) {
    showToast('Failed to send admit card.', 'error')
    console.error('Send error:', err)
  } finally {
    delete actionLoading[user.id]
  }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 20px;
}

.admin-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  overflow: hidden;
}

/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  color: white;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h1 {
  margin: 0;
  font-size: 24px;
  color: white;
}

.badge {
  background: #ff6b35;
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-email {
  color: #aaa;
  font-size: 13px;
}

/* Stats bar */
.stats-bar {
  display: flex;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.stat {
  flex: 1;
  padding: 16px;
  text-align: center;
  border-right: 1px solid #e9ecef;
}

.stat:last-child {
  border-right: none;
}

.stat-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
}

.stat-label {
  font-size: 12px;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Search */
.search-bar {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  gap: 16px;
  border-bottom: 1px solid #e9ecef;
}

.search-input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
}

.search-count {
  font-size: 13px;
  color: #888;
  white-space: nowrap;
}

/* Table */
.table-wrapper {
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.users-table thead tr {
  background: #f1f3f5;
}

.users-table th {
  padding: 12px 14px;
  text-align: left;
  font-weight: 700;
  color: #555;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
}

.users-table tbody tr {
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.15s;
}

.users-table tbody tr:hover {
  background: #f8f9ff;
}

.users-table td {
  padding: 11px 14px;
  color: #444;
  vertical-align: middle;
}

.td-index {
  color: #aaa;
  font-size: 12px;
  width: 36px;
}

.td-email {
  color: #555;
  font-size: 12px;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.td-roll {
  font-family: monospace;
  font-weight: 700;
  color: #1a1a2e;
}

.td-no-reg {
  color: #bbb;
  font-style: italic;
  text-align: center;
}

.td-empty {
  text-align: center;
  color: #bbb;
  padding: 40px;
}

.td-actions {
  display: flex;
  gap: 6px;
  white-space: nowrap;
}

/* Action Buttons */
.btn-action {
  padding: 6px 12px;
  border: none;
  border-radius: 5px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-download {
  background: #e8f4fd;
  color: #1976d2;
  border: 1px solid #bbdefb;
}

.btn-download:hover:not(:disabled) {
  background: #1976d2;
  color: white;
}

.btn-send {
  background: #e8f5e9;
  color: #388e3c;
  border: 1px solid #c8e6c9;
}

.btn-send:hover:not(:disabled) {
  background: #388e3c;
  color: white;
}

/* Generic buttons */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  transition: all 0.2s;
}

.btn-secondary {
  background: rgba(255,255,255,0.15);
  color: white;
  border: 1px solid rgba(255,255,255,0.3);
}

.btn-secondary:hover {
  background: rgba(255,255,255,0.25);
}

.btn-logout {
  background: #ef5350;
  color: white;
}

.btn-logout:hover {
  background: #c62828;
}

/* Alerts */
.loading {
  text-align: center;
  padding: 40px;
  color: #888;
}

.alert {
  margin: 16px 24px;
  padding: 12px 16px;
  border-radius: 6px;
  font-size: 14px;
}

.alert-error {
  background: #fee;
  color: #c33;
  border: 1px solid #fcc;
}

/* Toast */
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 14px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  z-index: 9999;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  animation: slideIn 0.3s ease;
}

.toast.success {
  background: #4caf50;
  color: white;
}

.toast.error {
  background: #f44336;
  color: white;
}

@keyframes slideIn {
  from { transform: translateX(100px); opacity: 0; }
  to   { transform: translateX(0);     opacity: 1; }
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .stats-bar {
    flex-wrap: wrap;
  }

  .stat {
    min-width: 50%;
  }
}
</style>
