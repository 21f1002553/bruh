<template>
  <DashboardLayout>
    <div class="hr-job-postings">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <h1>Job Postings</h1>
          <p>Manage all job postings and create new opportunities</p>
        </div>
        <div class="header-actions">
          <button class="btn-primary" @click="openJobPostModal">
            <i class="fas fa-plus"></i>
            Post New Job
          </button>
        </div>
      </div>

      <!-- Stats Overview -->
      <div class="stats-grid">
        <div class="stat-card active">
          <i class="fas fa-briefcase stat-icon"></i>
          <div class="stat-content">
            <h3>{{ stats.activeJobs }}</h3>
            <p>Active Jobs</p>
          </div>
        </div>
        <div class="stat-card draft">
          <i class="fas fa-file-alt stat-icon"></i>
          <div class="stat-content">
            <h3>{{ stats.draftJobs }}</h3>
            <p>Draft Jobs</p>
          </div>
        </div>
        <div class="stat-card applications">
          <i class="fas fa-users stat-icon"></i>
          <div class="stat-content">
            <h3>{{ stats.totalApplications }}</h3>
            <p>Total Applications</p>
          </div>
        </div>
        <div class="stat-card closed">
          <i class="fas fa-check-circle stat-icon"></i>
          <div class="stat-content">
            <h3>{{ stats.closedJobs }}</h3>
            <p>Closed Jobs</p>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-section">
        <div class="filter-group">
          <label>Status</label>
          <select v-model="filters.status" @change="loadJobPostings">
            <option value="">All Statuses</option>
            <option value="active">Active</option>
            <option value="draft">Draft</option>
            <option value="closed">Closed</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Search</label>
          <input 
            type="text" 
            v-model="filters.search" 
            placeholder="Search by title or location..."
            @input="handleSearch"
          />
        </div>
      </div>

      <!-- Job Postings List -->
      <div class="job-postings-section">
        <div v-if="loading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading job postings...</p>
        </div>

        <div v-else-if="filteredJobs.length === 0" class="empty-state">
          <i class="fas fa-briefcase"></i>
          <p>No job postings found</p>
          <button class="btn-primary" @click="openJobPostModal">
            <i class="fas fa-plus"></i>
            Create Your First Job Post
          </button>
        </div>

        <div v-else class="jobs-grid">
          <div 
            v-for="job in filteredJobs" 
            :key="job.id"
            class="job-card"
          >
            <div class="job-header">
              <div class="job-title-section">
                <h3>{{ job.title }}</h3>
                <p class="job-meta">
                  <i class="fas fa-map-marker-alt"></i>
                  {{ job.location || 'Remote' }}
                </p>
              </div>
              <span 
                class="status-badge" 
                :class="job.status"
              >
                {{ formatStatus(job.status) }}
              </span>
            </div>

            <div class="job-details">
              <p class="job-description">
                {{ truncateText(job.description, 150) }}
              </p>

              <div class="job-info-grid">
                <div class="info-item">
                  <i class="fas fa-graduation-cap"></i>
                  <span>{{ job.level || 'Not specified' }}</span>
                </div>
                <div class="info-item">
                  <i class="fas fa-building"></i>
                  <span>{{ job.school || 'Not specified' }}</span>
                </div>
                <div class="info-item">
                  <i class="fas fa-calendar"></i>
                  <span>Posted {{ formatDate(job.posted_at) }}</span>
                </div>
                <div class="info-item">
                  <i class="fas fa-users"></i>
                  <span>{{ job.application_count || 0 }} Applications</span>
                </div>
              </div>
            </div>

            <div class="job-actions">
              <button 
                class="btn-secondary"
                @click="viewJobDetails(job)"
              >
                <i class="fas fa-eye"></i>
                View Details
              </button>
              <button 
                class="btn-secondary"
                @click="editJob(job)"
              >
                <i class="fas fa-edit"></i>
                Edit
              </button>
              <button 
                class="btn-secondary"
                @click="viewApplications(job)"
              >
                <i class="fas fa-file-alt"></i>
                Applications ({{ job.application_count || 0 }})
              </button>
              <button 
                v-if="job.status === 'active'"
                class="btn-danger"
                @click="closeJob(job.id)"
              >
                <i class="fas fa-times-circle"></i>
                Close
              </button>
              <button 
                v-else-if="job.status === 'closed'"
                class="btn-success"
                @click="reopenJob(job.id)"
              >
                <i class="fas fa-redo"></i>
                Reopen
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Job Post Modal -->
    <JobPostModal 
      v-if="showJobPostModal"
      :job="selectedJob"
      @close="closeJobPostModal"
      @job-posted="handleJobPosted"
    />
  </DashboardLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'
import JobPostModal from './JobPostModal.vue'

const router = useRouter()

// State
const loading = ref(false)
const jobPostings = ref([])
const showJobPostModal = ref(false)
const selectedJob = ref(null)
const filters = ref({
  status: '',
  search: ''
})

// Helper Functions
const getAuthToken = () => localStorage.getItem('access_token')

function formatDate(dateString) {
  if (!dateString) return 'Recently'
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function formatStatus(status) {
  if (!status) return 'Active'
  return status.charAt(0).toUpperCase() + status.slice(1)
}

function truncateText(text, maxLength) {
  if (!text) return 'No description available'
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// Computed
const stats = computed(() => {
  return {
    activeJobs: jobPostings.value.filter(j => j.status === 'active').length,
    draftJobs: jobPostings.value.filter(j => j.status === 'draft').length,
    closedJobs: jobPostings.value.filter(j => j.status === 'closed').length,
    totalApplications: jobPostings.value.reduce((sum, j) => sum + (j.application_count || 0), 0)
  }
})

const filteredJobs = computed(() => {
  let jobs = [...jobPostings.value]
  
  // Filter by status
  if (filters.value.status) {
    jobs = jobs.filter(job => job.status === filters.value.status)
  }
  
  // Filter by search
  if (filters.value.search) {
    const searchLower = filters.value.search.toLowerCase()
    jobs = jobs.filter(job => 
      job.title?.toLowerCase().includes(searchLower) ||
      job.location?.toLowerCase().includes(searchLower) ||
      job.description?.toLowerCase().includes(searchLower)
    )
  }
  
  return jobs
})

// API Functions
async function loadJobPostings() {
  loading.value = true
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/jobs/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    jobPostings.value = response.data || []
    
    // Load application counts for each job
    for (const job of jobPostings.value) {
      await loadApplicationCount(job)
    }
  } catch (error) {
    console.error('Error loading job postings:', error)
    alert('Failed to load job postings')
  } finally {
    loading.value = false
  }
}

async function loadApplicationCount(job) {
  try {
    const token = getAuthToken()
    const response = await axios.get(`/api/applications/?job_id=${job.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    job.application_count = response.data.applications?.length || 0
  } catch (error) {
    console.error('Error loading application count:', error)
    job.application_count = 0
  }
}

async function closeJob(jobId) {
  if (!confirm('Are you sure you want to close this job posting?')) {
    return
  }

  try {
    const token = getAuthToken()
    await axios.put(`/api/jobs/${jobId}`, {
      status: 'closed'
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })

    alert('Job posting closed successfully')
    await loadJobPostings()
  } catch (error) {
    console.error('Error closing job:', error)
    alert('Failed to close job posting')
  }
}

async function reopenJob(jobId) {
  if (!confirm('Are you sure you want to reopen this job posting?')) {
    return
  }

  try {
    const token = getAuthToken()
    await axios.put(`/api/jobs/${jobId}`, {
      status: 'active'
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })

    alert('Job posting reopened successfully')
    await loadJobPostings()
  } catch (error) {
    console.error('Error reopening job:', error)
    alert('Failed to reopen job posting')
  }
}

// Modal Functions
function openJobPostModal() {
  selectedJob.value = null
  showJobPostModal.value = true
}

function closeJobPostModal() {
  showJobPostModal.value = false
  selectedJob.value = null
}

async function handleJobPosted() {
  closeJobPostModal()
  await loadJobPostings()
}

// Action Functions
function viewJobDetails(job) {
  // You can implement a detail view modal or navigate to a detail page
  alert('Job Details: ' + JSON.stringify(job, null, 2))
}

function editJob(job) {
  selectedJob.value = job
  showJobPostModal.value = true
}

function viewApplications(job) {
  router.push(`/hr/applications?job_id=${job.id}`)
}

function handleSearch() {
  // Debounce search if needed
  // For now, the computed property handles it
}

// Load data on mount
onMounted(async () => {
  await loadJobPostings()
})
</script>

<style scoped>
.hr-job-postings {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 20px;
}

.header-content h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 8px;
}

.header-content p {
  color: #7f8c8d;
}

.btn-primary {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
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

.stat-card.active .stat-icon {
  color: #28a745;
}

.stat-card.draft .stat-icon {
  color: #ffc107;
}

.stat-card.applications .stat-icon {
  color: #17a2b8;
}

.stat-card.closed .stat-icon {
  color: #6c757d;
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

.empty-state button {
  margin-top: 20px;
}

/* Jobs Grid */
.jobs-grid {
  display: grid;
  gap: 24px;
}

.job-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.job-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ecf0f1;
}

.job-title-section h3 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 1.3rem;
}

.job-meta {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-badge {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.draft {
  background: #fff3cd;
  color: #856404;
}

.status-badge.closed {
  background: #f8d7da;
  color: #721c24;
}

.job-details {
  margin-bottom: 20px;
}

.job-description {
  color: #555;
  line-height: 1.6;
  margin-bottom: 16px;
}

.job-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.info-item i {
  color: #667eea;
  width: 16px;
}

.job-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-secondary {
  padding: 10px 16px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  transition: all 0.3s ease;
  color: #2c3e50;
}

.btn-secondary:hover {
  background: #f8f9fa;
  border-color: #667eea;
  color: #667eea;
}

.btn-danger {
  padding: 10px 16px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-danger:hover {
  background: #c82333;
}

.btn-success {
  padding: 10px 16px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-success:hover {
  background: #218838;
}

/* Responsive */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .job-header {
    flex-direction: column;
    gap: 12px;
  }

  .job-actions {
    flex-direction: column;
  }

  .job-actions button {
    width: 100%;
  }
}
</style>
