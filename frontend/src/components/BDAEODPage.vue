<template>
  <DashboardLayout>
    <div class="bda-eod-page">
      <!-- Header -->
      <header class="dashboard-header">
        <div class="header-left">
          <h1>EOD Reports</h1>
        </div>
        <div class="header-right">
          <button class="action-btn primary" @click="showEODModal = true">
            <i class="fas fa-plus"></i> New Report
          </button>
        </div>
      </header>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon total">
            <i class="fas fa-file-alt"></i>
          </div>
          <div class="stat-info">
            <h3>{{ stats.totalReports }}</h3>
            <p>Total Reports</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon streak">
            <i class="fas fa-fire"></i>
          </div>
          <div class="stat-info">
            <h3>{{ stats.streak }}</h3>
            <p>Day Streak</p>
          </div>
        </div>
      </div>

      <!-- EOD List -->
      <div class="eod-container">
        <div v-if="loading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading reports...</p>
        </div>

        <div v-else-if="eodReports.length === 0" class="empty-state">
          <i class="fas fa-clipboard-list"></i>
          <p>No EOD reports found</p>
        </div>

        <div v-else class="eod-list">
          <div v-for="report in eodReports" :key="report.id" class="eod-card">
            <div class="eod-header">
              <div class="date-badge">
                <i class="fas fa-calendar-day"></i>
                {{ formatDate(report.report_date) }}
              </div>
              <span class="time-badge">
                <i class="fas fa-clock"></i> {{ formatTime(report.created_at) }}
              </span>
            </div>

            <div class="eod-content">
              <div class="section">
                <h4><i class="fas fa-check-circle"></i> Completed Tasks</h4>
                <p>{{ report.completed_tasks }}</p>
              </div>

              <div class="section">
                <h4><i class="fas fa-hourglass-half"></i> Pending Tasks</h4>
                <p>{{ report.pending_tasks }}</p>
              </div>

              <div class="section">
                <h4><i class="fas fa-calendar-plus"></i> Plan for Tomorrow</h4>
                <p>{{ report.plan_for_tomorrow }}</p>
              </div>

              <div v-if="report.blockers" class="section blockers">
                <h4><i class="fas fa-exclamation-triangle"></i> Blockers</h4>
                <p>{{ report.blockers }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- New EOD Modal -->
      <div v-if="showEODModal" class="modal-overlay" @click.self="showEODModal = false">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Submit EOD Report</h2>
            <button class="close-btn" @click="showEODModal = false">&times;</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitEOD" class="eod-form">
              <div class="form-group">
                <label>Completed Tasks</label>
                <textarea v-model="eodForm.completed_tasks" rows="3" required
                  placeholder="What did you achieve today?"></textarea>
              </div>

              <div class="form-group">
                <label>Pending Tasks</label>
                <textarea v-model="eodForm.pending_tasks" rows="2" required
                  placeholder="What is still in progress?"></textarea>
              </div>

              <div class="form-group">
                <label>Plan for Tomorrow</label>
                <textarea v-model="eodForm.plan_for_tomorrow" rows="3" required
                  placeholder="What will you work on next?"></textarea>
              </div>

              <div class="form-group">
                <label>Blockers (Optional)</label>
                <textarea v-model="eodForm.blockers" rows="2"
                  placeholder="Any issues blocking your progress?"></textarea>
              </div>

              <div class="form-actions">
                <button type="button" class="cancel-btn" @click="showEODModal = false">Cancel</button>
                <button type="submit" class="submit-btn" :disabled="submitting">
                  <i v-if="submitting" class="fas fa-spinner fa-spin"></i>
                  {{ submitting ? 'Submitting...' : 'Submit Report' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'

const loading = ref(false)
const submitting = ref(false)
const showEODModal = ref(false)
const eodReports = ref([])
const bdaId = ref('')

const eodForm = ref({
  completed_tasks: '',
  pending_tasks: '',
  plan_for_tomorrow: '',
  blockers: ''
})

const stats = computed(() => {
  return {
    totalReports: eodReports.value.length,
    streak: calculateStreak(eodReports.value)
  }
})

function calculateStreak(reports) {
  // Simple streak calculation logic
  if (!reports.length) return 0
  // This would need more complex logic for real streak calculation
  return reports.length > 0 ? 'Active' : 0
}

function getAuthToken() {
  return localStorage.getItem('access_token')
}

async function loadUserData() {
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/users/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    bdaId.value = response.data.id
    loadEODReports()
  } catch (error) {
    console.error('Error loading user data:', error)
  }
}

// ...existing code...
async function loadEODReports() {
  loading.value = true
  try {
    const token = getAuthToken()
    // Get current date for end_date and 30 days ago for start_date
    const endDate = new Date().toISOString().split('T')[0]
    const startDate = new Date()
    startDate.setDate(startDate.getDate() - 30)
    const startDateStr = startDate.toISOString().split('T')[0]

    const response = await axios.get('/api/eod/submissions', {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        employee: bdaId.value,
        start_date: startDateStr,
        end_date: endDate,
        page: 1,
        limit: 50
      }
    })

    eodReports.value = (response.data.data || []).map(report => ({
      id: report.id,
      report_date: report.date,
      created_at: `${report.date}T${report.time}`,
      completed_tasks: report.detailed_data?.completed_tasks || '',
      pending_tasks: report.detailed_data?.pending_tasks || '',
      plan_for_tomorrow: report.detailed_data?.plan_for_tomorrow || '',
      blockers: report.detailed_data?.blockers || ''
    }))
  } catch (error) {
    console.error('Error loading EOD reports:', error)
  } finally {
    loading.value = false
  }
}

async function submitEOD() {
  submitting.value = true
  try {
    const token = getAuthToken()
    const now = new Date()
    const payload = {
      employee_id: bdaId.value,
      report_id: `EOD-${now.getTime()}`,
      role: 'bda',
      date: now.toISOString().split('T')[0],
      time: now.toLocaleTimeString('en-US', { hour12: false }),
      data: {
        completed_tasks: eodForm.value.completed_tasks,
        pending_tasks: eodForm.value.pending_tasks,
        plan_for_tomorrow: eodForm.value.plan_for_tomorrow,
        blockers: eodForm.value.blockers
      }
    }

    await axios.post('/api/eod/submit', payload, {
      headers: { Authorization: `Bearer ${token}` }
    })

    alert('EOD Report submitted successfully!')
    showEODModal.value = false
    eodForm.value = { completed_tasks: '', pending_tasks: '', plan_for_tomorrow: '', blockers: '' }
    loadEODReports()
  } catch (error) {
    console.error('Error submitting EOD:', error)
    alert('Failed to submit EOD report')
  } finally {
    submitting.value = false
  }
}
// ...existing code...

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function formatTime(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.bda-eod-page {
  padding: 24px;
  background: #f8f9fa;
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.action-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: transform 0.2s;
}

.action-btn:hover {
  transform: translateY(-2px);
}

/* Stats Cards */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stat-icon.total {
  background: #e3f2fd;
  color: #1976d2;
}

.stat-icon.streak {
  background: #fff3e0;
  color: #f57c00;
}

.stat-info h3 {
  margin: 0;
  font-size: 1.5rem;
  color: #2c3e50;
}

.stat-info p {
  margin: 4px 0 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

/* EOD List */
.eod-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.eod-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #667eea;
}

.eod-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.date-badge {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-badge {
  color: #95a5a6;
  font-size: 0.9rem;
}

.eod-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.section h4 {
  color: #2c3e50;
  margin: 0 0 8px 0;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section h4 i {
  color: #667eea;
}

.section p {
  color: #555;
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
}

.section.blockers h4 i {
  color: #e74c3c;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #2c3e50;
}

.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  outline: none;
  resize: vertical;
  font-family: inherit;
  max-width: -moz-available;
  max-width: -webkit-fill-available;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.cancel-btn {
  padding: 10px 20px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 8px;
  cursor: pointer;
}

.submit-btn {
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>