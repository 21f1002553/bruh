<template>
  <DashboardLayout>
    <div class="hr-applications">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <h1>Applications</h1>
          <p>Review and manage all candidate applications</p>
        </div>
      </div>

      <!-- Stats Overview -->
      <div class="stats-grid">
        <div class="stat-card total">
          <i class="fas fa-file-alt stat-icon"></i>
          <div class="stat-content">
            <h3>{{ stats.totalApplications }}</h3>
            <p>Total Applications</p>
          </div>
        </div>
        <div class="stat-card pending">
          <i class="fas fa-clock stat-icon"></i>
          <div class="stat-content">
            <h3>{{ stats.pendingApplications }}</h3>
            <p>Pending Review</p>
          </div>
        </div>
        <div class="stat-card reviewed">
          <i class="fas fa-check stat-icon"></i>
          <div class="stat-content">
            <h3>{{ stats.reviewedApplications }}</h3>
            <p>Reviewed</p>
          </div>
        </div>
        <div class="stat-card shortlisted">
          <i class="fas fa-star stat-icon"></i>
          <div class="stat-content">
            <h3>{{ stats.shortlistedApplications }}</h3>
            <p>Shortlisted</p>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-section">
        <div class="filter-group">
          <label>Job Position</label>
          <select v-model="filters.jobId" @change="loadApplications">
            <option value="">All Jobs</option>
            <option 
              v-for="job in jobPostings" 
              :key="job.id" 
              :value="job.id"
            >
              {{ job.title }}
            </option>
          </select>
        </div>
        <div class="filter-group">
          <label>Status</label>
          <select v-model="filters.status" @change="loadApplications">
            <option value="">All Statuses</option>
            <option value="applied">Applied</option>
            <option value="under_review">Under Review</option>
            <option value="shortlisted">Shortlisted</option>
            <option value="interviewed">Interviewed</option>
            <option value="selected">Selected</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Search</label>
          <input 
            type="text" 
            v-model="filters.search" 
            placeholder="Search by candidate name..."
            @input="handleSearch"
          />
        </div>
      </div>

      <!-- Applications List -->
      <div class="applications-section">
        <div v-if="loading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading applications...</p>
        </div>

        <div v-else-if="filteredApplications.length === 0" class="empty-state">
          <i class="fas fa-inbox"></i>
          <p>No applications found</p>
        </div>

        <div v-else class="applications-table">
          <table>
            <thead>
              <tr>
                <th>Candidate</th>
                <th>Job Position</th>
                <th>Applied Date</th>
                <th>Status</th>
                <th>Score</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="application in filteredApplications" 
                :key="application.id"
                class="application-row"
              >
                <td>
                  <div class="candidate-info">
                    <div class="candidate-avatar">
                      {{ getInitials(application.candidate_name) }}
                    </div>
                    <div>
                      <div class="candidate-name">{{ application.candidate_name || 'Unknown' }}</div>
                      <div class="candidate-email">{{ application.candidate_email || 'N/A' }}</div>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="job-title">{{ application.job_title || 'N/A' }}</div>
                </td>
                <td>
                  <span class="date">{{ formatDate(application.applied_at) }}</span>
                </td>
                <td>
                  <span 
                    class="status-badge" 
                    :class="application.status"
                  >
                    {{ formatStatus(application.status) }}
                  </span>
                </td>
                <td>
                  <span class="score" v-if="application.score">
                    {{ application.score }}/100
                  </span>
                  <span class="score-na" v-else>N/A</span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button 
                      class="btn-icon" 
                      @click="viewApplication(application)"
                      title="View Details"
                    >
                      <i class="fas fa-eye"></i>
                    </button>
                    <button 
                      class="btn-icon" 
                      @click="updateStatus(application)"
                      title="Update Status"
                    >
                      <i class="fas fa-edit"></i>
                    </button>
                    <button 
                      v-if="application.resume_id"
                      class="btn-icon" 
                      @click="viewResume(application)"
                      title="View Resume"
                    >
                      <i class="fas fa-file-pdf"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Application Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h2>Application Details</h2>
          <button class="close-btn" @click="closeDetailsModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body" v-if="selectedApplication">
          <div class="detail-section">
            <h3>Candidate Information</h3>
            <div class="detail-grid">
              <div class="detail-item">
                <label>Name:</label>
                <span>{{ selectedApplication.candidate_name }}</span>
              </div>
              <div class="detail-item">
                <label>Email:</label>
                <span>{{ selectedApplication.candidate_email }}</span>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h3>Job Information</h3>
            <div class="detail-grid">
              <div class="detail-item">
                <label>Position:</label>
                <span>{{ selectedApplication.job_title }}</span>
              </div>
              <div class="detail-item">
                <label>Applied Date:</label>
                <span>{{ formatDate(selectedApplication.applied_at) }}</span>
              </div>
            </div>
          </div>

          <div class="detail-section" v-if="selectedApplication.cover_letter">
            <h3>Cover Letter</h3>
            <p class="cover-letter">{{ selectedApplication.cover_letter }}</p>
          </div>

          <div class="detail-section">
            <h3>Application Details</h3>
            <div class="detail-grid">
              <div class="detail-item" v-if="selectedApplication.expected_salary">
                <label>Expected Salary:</label>
                <span>${{ selectedApplication.expected_salary }}</span>
              </div>
              <div class="detail-item" v-if="selectedApplication.availability">
                <label>Availability:</label>
                <span>{{ selectedApplication.availability }}</span>
              </div>
              <div class="detail-item" v-if="selectedApplication.source">
                <label>Source:</label>
                <span>{{ selectedApplication.source }}</span>
              </div>
              <div class="detail-item">
                <label>Status:</label>
                <span class="status-badge" :class="selectedApplication.status">
                  {{ formatStatus(selectedApplication.status) }}
                </span>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h3>Update Status</h3>
            <div class="status-update">
              <select v-model="newStatus">
                <option value="applied">Applied</option>
                <option value="under_review">Under Review</option>
                <option value="shortlisted">Shortlisted</option>
                <option value="interviewed">Interviewed</option>
                <option value="selected">Selected</option>
                <option value="rejected">Rejected</option>
              </select>
              <button class="btn-primary" @click="saveStatusUpdate">
                Update Status
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'

const route = useRoute()

// State
const loading = ref(false)
const applications = ref([])
const jobPostings = ref([])
const showDetailsModal = ref(false)
const selectedApplication = ref(null)
const newStatus = ref('')

const filters = ref({
  jobId: '',
  status: '',
  search: ''
})

// Helper Functions
const getAuthToken = () => localStorage.getItem('access_token')

function getInitials(name) {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2)
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

function formatStatus(status) {
  if (!status) return 'Applied'
  return status.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

// Computed
const stats = computed(() => {
  return {
    totalApplications: applications.value.length,
    pendingApplications: applications.value.filter(a => 
      a.status === 'applied' || a.status === 'under_review'
    ).length,
    reviewedApplications: applications.value.filter(a => 
      a.status === 'under_review' || a.status === 'shortlisted'
    ).length,
    shortlistedApplications: applications.value.filter(a => 
      a.status === 'shortlisted'
    ).length
  }
})

const filteredApplications = computed(() => {
  let apps = [...applications.value]
  
  // Filter by job
  if (filters.value.jobId) {
    apps = apps.filter(app => app.job_id === filters.value.jobId)
  }
  
  // Filter by status
  if (filters.value.status) {
    apps = apps.filter(app => app.status === filters.value.status)
  }
  
  // Filter by search
  if (filters.value.search) {
    const searchLower = filters.value.search.toLowerCase()
    apps = apps.filter(app => 
      app.candidate_name?.toLowerCase().includes(searchLower) ||
      app.candidate_email?.toLowerCase().includes(searchLower)
    )
  }
  
  return apps
})

// API Functions
async function loadJobPostings() {
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/jobs/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    jobPostings.value = response.data || []
  } catch (error) {
    console.error('Error loading job postings:', error)
  }
}

async function loadApplications() {
  loading.value = true
  try {
    const token = getAuthToken()
    let url = '/api/applications/'
    
    // If job_id is in query params or filter, use it
    const jobId = filters.value.jobId || route.query.job_id
    if (jobId) {
      url += `?job_id=${jobId}`
    }
    
    const response = await axios.get(url, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    applications.value = response.data.applications || []
    
    // Load candidate and job details for each application
    for (const app of applications.value) {
      await loadApplicationDetails(app)
    }
  } catch (error) {
    console.error('Error loading applications:', error)
    alert('Failed to load applications')
  } finally {
    loading.value = false
  }
}

async function loadApplicationDetails(application) {
  try {
    const token = getAuthToken()
    
    // Load candidate details
    if (application.candidate_id) {
      const candidateResponse = await axios.get(`/api/users/${application.candidate_id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      application.candidate_name = candidateResponse.data.name
      application.candidate_email = candidateResponse.data.email
    }
    
    // Load job details
    if (application.job_id) {
      const jobResponse = await axios.get(`/api/jobs/${application.job_id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      application.job_title = jobResponse.data.title
    }
  } catch (error) {
    console.error('Error loading application details:', error)
  }
}

async function saveStatusUpdate() {
  if (!selectedApplication.value || !newStatus.value) return

  try {
    const token = getAuthToken()
    await axios.put(`/api/applications/${selectedApplication.value.id}/status`, {
      status: newStatus.value
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })

    alert('Status updated successfully')
    closeDetailsModal()
    await loadApplications()
  } catch (error) {
    console.error('Error updating status:', error)
    alert('Failed to update status')
  }
}

// Action Functions
function viewApplication(application) {
  selectedApplication.value = application
  newStatus.value = application.status || 'applied'
  showDetailsModal.value = true
}

function updateStatus(application) {
  viewApplication(application)
}

async function viewResume(application) {
  try {
    const token = getAuthToken()
    const response = await axios.get(`/api/files/${application.resume_id}/download`, {
      headers: { Authorization: `Bearer ${token}` },
      responseType: 'blob'
    })

    const blob = new Blob([response.data], { type: response.headers['content-type'] })
    const url = window.URL.createObjectURL(blob)
    window.open(url, '_blank')
    
    setTimeout(() => window.URL.revokeObjectURL(url), 100)
  } catch (error) {
    console.error('Error viewing resume:', error)
    alert('Failed to view resume')
  }
}

function closeDetailsModal() {
  showDetailsModal.value = false
  selectedApplication.value = null
}

function handleSearch() {
  // Debounce if needed
}

// Load data on mount
onMounted(async () => {
  // Check if job_id is in query params
  if (route.query.job_id) {
    filters.value.jobId = route.query.job_id
  }
  
  await loadJobPostings()
  await loadApplications()
})
</script>

<style scoped>
.hr-applications {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Page Header */
.page-header {
  margin-bottom: 30px;
}

.header-content h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 8px;
}

.header-content p {
  color: #7f8c8d;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 2.5rem;
  opacity: 0.8;
}

.stat-card.total .stat-icon {
  color: #3498db;
}

.stat-card.pending .stat-icon {
  color: #ffc107;
}

.stat-card.reviewed .stat-icon {
  color: #17a2b8;
}

.stat-card.shortlisted .stat-icon {
  color: #28a745;
}

.stat-content h3 {
  font-size: 2rem;
  margin: 0;
  color: #2c3e50;
}

.stat-content p {
  margin: 4px 0 0 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

/* Filters */
.filters-section {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-width: 200px;
}

.filter-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

.filter-group select,
.filter-group input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s ease;
}

.filter-group select:focus,
.filter-group input:focus {
  border-color: #667eea;
}

/* Loading & Empty States */
.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  color: #7f8c8d;
}

.loading-state i,
.empty-state i {
  font-size: 3rem;
  margin-bottom: 16px;
  opacity: 0.5;
}

/* Applications Table */
.applications-table {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

th {
  padding: 16px;
  text-align: left;
  font-weight: 600;
  font-size: 0.9rem;
}

tbody tr {
  border-bottom: 1px solid #ecf0f1;
  transition: background 0.3s ease;
}

tbody tr:hover {
  background: #f8f9fa;
}

td {
  padding: 16px;
}

.candidate-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.candidate-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.candidate-name {
  font-weight: 600;
  color: #2c3e50;
}

.candidate-email {
  font-size: 0.85rem;
  color: #7f8c8d;
}

.job-title {
  color: #2c3e50;
  font-weight: 500;
}

.date {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.applied {
  background: #e3f2fd;
  color: #1976d2;
}

.status-badge.under_review {
  background: #fff3cd;
  color: #856404;
}

.status-badge.shortlisted {
  background: #d4edda;
  color: #155724;
}

.status-badge.interviewed {
  background: #d1ecf1;
  color: #0c5460;
}

.status-badge.selected {
  background: #d4edda;
  color: #155724;
}

.status-badge.rejected {
  background: #f8d7da;
  color: #721c24;
}

.score {
  color: #28a745;
  font-weight: 600;
}

.score-na {
  color: #7f8c8d;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-icon {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 6px;
  background: #f8f9fa;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.btn-icon:hover {
  background: #667eea;
  color: white;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 16px;
  max-width: 700px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px;
  border-bottom: 1px solid #ecf0f1;
}

.modal-header h2 {
  margin: 0;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #7f8c8d;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #ecf0f1;
  color: #e74c3c;
}

.modal-body {
  padding: 30px;
}

.detail-section {
  margin-bottom: 25px;
}

.detail-section h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 1.1rem;
  border-bottom: 2px solid #667eea;
  padding-bottom: 8px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item label {
  font-weight: 600;
  color: #7f8c8d;
  font-size: 0.85rem;
}

.detail-item span {
  color: #2c3e50;
}

.cover-letter {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #667eea;
  line-height: 1.6;
  color: #555;
}

.status-update {
  display: flex;
  gap: 15px;
  align-items: center;
}

.status-update select {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
}

.btn-primary {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* Responsive */
@media (max-width: 768px) {
  .applications-table {
    overflow-x: auto;
  }

  table {
    min-width: 800px;
  }
}
</style>
