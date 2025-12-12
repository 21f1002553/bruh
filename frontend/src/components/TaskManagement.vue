<template>
  <DashboardLayout>
    <div class="task-management">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <h1>Task Management</h1>
          <p>Create, assign, and manage tasks for your team</p>
        </div>
        <div class="header-actions">
          <button class="btn-create-task" @click="showTaskModal = true">
            <i class="fas fa-plus"></i> Create New Task
          </button>
        </div>
      </div>

      <!-- Stats Grid -->
      <div class="stats-grid">
        <div class="stat-card">
          <i class="fas fa-tasks stat-icon"></i>
          <div class="stat-content">
            <h3>{{ stats.totalTasks }}</h3>
            <p>Total Tasks</p>
          </div>
        </div>
        <div class="stat-card pending">
          <i class="fas fa-clock stat-icon"></i>
          <div class="stat-content">
            <h3>{{ stats.pendingTasks }}</h3>
            <p>Pending Tasks</p>
          </div>
        </div>
        <div class="stat-card progress">
          <i class="fas fa-spinner stat-icon"></i>
          <div class="stat-content">
            <h3>{{ stats.inProgressTasks }}</h3>
            <p>In Progress</p>
          </div>
        </div>
        <div class="stat-card completed">
          <i class="fas fa-check-circle stat-icon"></i>
          <div class="stat-content">
            <h3>{{ stats.completedTasks }}</h3>
            <p>Completed</p>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-section">
        <div class="filter-group">
          <label>Status:</label>
          <select v-model="filters.status">
            <option value="">All Tasks</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="reviewed">Reviewed</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Priority:</label>
          <select v-model="filters.priority">
            <option value="">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Search:</label>
          <input 
            type="text" 
            v-model="filters.search" 
            placeholder="Search tasks..."
          />
        </div>
      </div>

      <!-- Tasks List -->
      <div class="tasks-section">
        <h2>All Tasks</h2>
        
        <div v-if="tasksLoading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading tasks...</p>
        </div>

        <div v-else-if="filteredTasks.length === 0" class="empty-state">
          <i class="fas fa-inbox"></i>
          <p>No tasks found</p>
        </div>

        <div v-else class="tasks-grid">
          <div 
            v-for="task in filteredTasks" 
            :key="task.id"
            class="task-card"
            :class="'priority-' + task.priority"
          >
            <div class="task-header">
              <div class="task-title-section">
                <h4>{{ task.title }}</h4>
                <span class="priority-badge" :class="task.priority">
                  {{ formatPriority(task.priority) }}
                </span>
              </div>
              <span class="task-status-badge" :class="task.status">
                {{ formatTaskStatus(task.status) }}
              </span>
            </div>

            <div class="task-description">
              <p>{{ task.description }}</p>
            </div>

            <div class="task-meta">
              <div class="meta-item">
                <i class="fas fa-user"></i>
                <span>{{ task.assigned_to_name || 'Unassigned' }}</span>
              </div>
              <div class="meta-item">
                <i class="fas fa-calendar"></i>
                <span>{{ formatDate(task.deadline) }}</span>
              </div>
            </div>

            <!-- Reviews Section -->
            <div v-if="task.employee_review || task.manager_review" class="reviews-section">
              <div v-if="task.employee_review" class="review-item employee-review">
                <div class="review-header">
                  <i class="fas fa-user"></i>
                  <strong>Employee Review</strong>
                  <small>{{ formatDate(task.employee_reviewed_at) }}</small>
                </div>
                <div class="review-text">{{ task.employee_review }}</div>
              </div>

              <div v-if="task.manager_review" class="review-item manager-review">
                <div class="review-header">
                  <i class="fas fa-user-tie"></i>
                  <strong>Your Review</strong>
                  <small>{{ formatDate(task.manager_reviewed_at) }}</small>
                </div>
                <div class="review-text">{{ task.manager_review }}</div>
              </div>

              <div v-if="task.ai_summary" class="review-item ai-summary">
                <div class="review-header">
                  <i class="fas fa-robot"></i>
                  <strong>AI Summary</strong>
                  <small>{{ formatDate(task.ai_summary_generated_at) }}</small>
                </div>
                <div class="review-text ai-text" v-html="formatAISummary(task.ai_summary)"></div>
              </div>
            </div>

            <!-- Task Actions -->
            <div class="task-actions">
              <button 
                v-if="task.status === 'completed' && !task.manager_review"
                class="btn-review-task"
                @click="openReviewModal(task)"
              >
                <i class="fas fa-comment-dots"></i>
                Submit Review
              </button>

              <button 
                v-if="task.employee_review && task.manager_review && !task.ai_summary"
                class="btn-generate-summary"
                @click="generateAISummary(task)"
                :disabled="generatingSummary === task.id"
              >
                <i class="fas fa-robot"></i>
                {{ generatingSummary === task.id ? 'Generating...' : 'Generate AI Summary' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Create Task Modal -->
      <div v-if="showTaskModal" class="modal-overlay" @click.self="showTaskModal = false">
        <div class="modal-container">
          <div class="modal-header">
            <h3>Create New Task</h3>
            <button class="close-btn" @click="showTaskModal = false">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>Assign To:</label>
              <select v-model="taskForm.assigned_to_id" required>
                <option value="">Select Candidate</option>
                <option v-for="candidate in candidates" :key="candidate.id" :value="candidate.id">
                  {{ candidate.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Task Title:</label>
              <input type="text" v-model="taskForm.title" placeholder="Enter task title" required />
            </div>

            <div class="form-group">
              <label>Description:</label>
              <textarea v-model="taskForm.description" rows="4" placeholder="Enter task description"></textarea>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Deadline:</label>
                <input type="datetime-local" v-model="taskForm.deadline" required />
              </div>

              <div class="form-group">
                <label>Priority:</label>
                <select v-model="taskForm.priority">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
            </div>

            <div class="modal-footer">
              <button class="btn-cancel" @click="showTaskModal = false">Cancel</button>
              <button 
                class="btn-submit" 
                @click="submitTask"
                :disabled="submittingTask"
              >
                {{ submittingTask ? 'Creating...' : 'Create Task' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Manager Review Modal -->
      <div v-if="showReviewModal" class="modal-overlay" @click.self="closeReviewModal">
        <div class="modal-container review-modal">
          <div class="modal-header">
            <h3>Submit Manager Review</h3>
            <button class="close-btn" @click="closeReviewModal">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <div class="task-info-box">
              <h4>{{ selectedTask?.title }}</h4>
              <p>{{ selectedTask?.description }}</p>
            </div>

            <div v-if="selectedTask?.employee_review" class="employee-review-box">
              <h4>Employee's Review:</h4>
              <p>{{ selectedTask.employee_review }}</p>
            </div>

            <div class="form-group">
              <label>Your Review:</label>
              <textarea 
                v-model="managerReview" 
                rows="6" 
                placeholder="Enter your review of the employee's work..."
                class="review-textarea"
              ></textarea>
            </div>

            <div class="modal-footer">
              <button class="btn-cancel" @click="closeReviewModal">Cancel</button>
              <button 
                class="btn-submit" 
                @click="submitManagerReview"
                :disabled="submittingReview || !managerReview"
              >
                {{ submittingReview ? 'Submitting...' : 'Submit Review' }}
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
import { useRouter } from 'vue-router'
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'

const router = useRouter()

// State
const hoId = ref('')
const allTasks = ref([])
const candidates = ref([])
const tasksLoading = ref(false)
const showTaskModal = ref(false)
const showReviewModal = ref(false)
const selectedTask = ref(null)
const managerReview = ref('')
const submittingTask = ref(false)
const submittingReview = ref(false)
const generatingSummary = ref(null)

// Filters
const filters = ref({
  status: '',
  priority: '',
  search: ''
})

// Task Form
const taskForm = ref({
  assigned_to_id: '',
  title: '',
  description: '',
  deadline: '',
  priority: 'medium'
})

// Helper Functions
const getAuthToken = () => localStorage.getItem('access_token')

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatPriority(priority) {
  const priorityMap = {
    'high': 'High',
    'medium': 'Medium',
    'low': 'Low'
  }
  return priorityMap[priority] || priority
}

function formatTaskStatus(status) {
  const statusMap = {
    'pending': 'Pending',
    'in_progress': 'In Progress',
    'completed': 'Completed',
    'reviewed': 'Reviewed'
  }
  return statusMap[status] || status
}

function formatAISummary(summary) {
  if (!summary) return ''
  try {
    const parsed = typeof summary === 'string' ? JSON.parse(summary) : summary
    return `<div class="ai-summary-content">
      ${parsed.Strengths ? `<p><strong>💪 Strengths:</strong> ${parsed.Strengths}</p>` : ''}
      ${parsed.Weaknesses ? `<p><strong>⚠️ Weaknesses:</strong> ${parsed.Weaknesses}</p>` : ''}
      ${parsed.Improvements ? `<p><strong>📈 Improvements Needed:</strong> ${parsed.Improvements}</p>` : ''}
      ${parsed.Actionable_step ? `<p><strong>🎯 Actionable Step:</strong> ${parsed.Actionable_step}</p>` : ''}
      ${parsed.Comments ? `<p><strong>💬 Comments:</strong> ${parsed.Comments}</p>` : ''}
    </div>`
  } catch (e) {
    console.error('Error parsing AI summary:', e)
    return summary
  }
}

// Computed
const stats = computed(() => {
  return {
    totalTasks: allTasks.value.length,
    pendingTasks: allTasks.value.filter(t => t.status === 'pending').length,
    inProgressTasks: allTasks.value.filter(t => t.status === 'in_progress').length,
    completedTasks: allTasks.value.filter(t => t.status === 'completed' || t.status === 'reviewed').length
  }
})

const filteredTasks = computed(() => {
  let tasks = allTasks.value

  if (filters.value.status) {
    tasks = tasks.filter(t => t.status === filters.value.status)
  }

  if (filters.value.priority) {
    tasks = tasks.filter(t => t.priority === filters.value.priority)
  }

  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    tasks = tasks.filter(t => 
      t.title.toLowerCase().includes(search) ||
      t.description?.toLowerCase().includes(search) ||
      t.assigned_to_name?.toLowerCase().includes(search)
    )
  }

  return tasks
})

// API Functions
async function loadHOData() {
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/users/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    hoId.value = response.data.id
  } catch (error) {
    console.error('Error loading HO data:', error)
  }
}

async function loadTasks() {
  tasksLoading.value = true
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/tasks/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    allTasks.value = response.data.tasks || []
  } catch (error) {
    console.error('Error loading tasks:', error)
  } finally {
    tasksLoading.value = false
  }
}

async function loadCandidates() {
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/users/role/candidate', {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    candidates.value = response.data || []
  } catch (error) {
    console.error('Error loading candidates:', error)
  }
}

async function submitTask() {
  if (!taskForm.value.assigned_to_id || !taskForm.value.title || !taskForm.value.deadline) {
    alert('Please fill in all required fields')
    return
  }

  submittingTask.value = true
  try {
    const token = getAuthToken()
    await axios.post('/api/tasks/', {
      assigned_to_id: taskForm.value.assigned_to_id,
      title: taskForm.value.title,
      description: taskForm.value.description,
      deadline: new Date(taskForm.value.deadline).toISOString(),
      priority: taskForm.value.priority
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })

    alert('Task created successfully!')
    showTaskModal.value = false
    
    // Reset form
    taskForm.value = {
      assigned_to_id: '',
      title: '',
      description: '',
      deadline: '',
      priority: 'medium'
    }
    
    await loadTasks()
  } catch (error) {
    console.error('Error creating task:', error)
    alert('Failed to create task: ' + (error.response?.data?.error || error.message))
  } finally {
    submittingTask.value = false
  }
}

function openReviewModal(task) {
  selectedTask.value = task
  showReviewModal.value = true
  managerReview.value = ''
}

function closeReviewModal() {
  showReviewModal.value = false
  selectedTask.value = null
  managerReview.value = ''
}

async function submitManagerReview() {
  if (!managerReview.value) {
    alert('Please enter your review')
    return
  }

  submittingReview.value = true
  try {
    const token = getAuthToken()
    await axios.post(`/api/tasks/${selectedTask.value.id}/manager-review`, {
      review: managerReview.value
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })

    alert('Review submitted successfully!')
    closeReviewModal()
    await loadTasks()
  } catch (error) {
    console.error('Error submitting review:', error)
    alert('Failed to submit review')
  } finally {
    submittingReview.value = false
  }
}

async function generateAISummary(task) {
  if (!confirm('Generate AI summary for this task?')) return

  generatingSummary.value = task.id
  try {
    const token = getAuthToken()
    await axios.post(`/api/tasks/${task.id}/generate-ai-summary`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    })

    alert('AI summary generated successfully!')
    await loadTasks()
  } catch (error) {
    console.error('Error generating AI summary:', error)
    alert('Failed to generate AI summary')
  } finally {
    generatingSummary.value = null
  }
}

// Load data on mount
onMounted(async () => {
  await loadHOData()
  loadTasks()
  loadCandidates()
})
</script>

<style scoped>
.task-management {
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

.btn-create-task {
  padding: 12px 24px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-create-task:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(240, 147, 251, 0.4);
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
  color: #f093fb;
  opacity: 0.8;
}

.stat-card.pending .stat-icon {
  color: #ffc107;
}

.stat-card.progress .stat-icon {
  color: #17a2b8;
}

.stat-card.completed .stat-icon {
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
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.filter-group {
  flex: 1;
  min-width: 200px;
}

.filter-group label {
  display: block;
  margin-bottom: 8px;
  color: #2c3e50;
  font-weight: 500;
}

.filter-group select,
.filter-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}

/* Tasks Section */
.tasks-section h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 20px;
}

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

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
}

.task-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.task-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.task-card.priority-high {
  border-left: 4px solid #e74c3c;
}

.task-card.priority-medium {
  border-left: 4px solid #ffc107;
}

.task-card.priority-low {
  border-left: 4px solid #28a745;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 16px;
}

.task-title-section {
  flex: 1;
}

.task-title-section h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.priority-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.priority-badge.high {
  background: #f8d7da;
  color: #721c24;
}

.priority-badge.medium {
  background: #fff3cd;
  color: #856404;
}

.priority-badge.low {
  background: #d4edda;
  color: #155724;
}

.task-status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.task-status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.task-status-badge.in_progress {
  background: #cce5ff;
  color: #004085;
}

.task-status-badge.completed {
  background: #d4edda;
  color: #155724;
}

.task-status-badge.reviewed {
  background: #d1ecf1;
  color: #0c5460;
}

.task-description p {
  color: #7f8c8d;
  margin: 0 0 16px 0;
}

.task-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.meta-item i {
  color: #f093fb;
}

/* Reviews Section */
.reviews-section {
  border-top: 1px solid #ecf0f1;
  padding-top: 16px;
  margin-top: 16px;
}

.review-item {
  margin-bottom: 12px;
  padding: 12px;
  border-radius: 8px;
}

.review-item.employee-review {
  background: #e3f2fd;
}

.review-item.manager-review {
  background: #fff3cd;
}

.review-item.ai-summary {
  background: #f3e5f5;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.review-header i {
  color: #f093fb;
}

.review-header strong {
  color: #2c3e50;
}

.review-header small {
  color: #7f8c8d;
  margin-left: auto;
}

.review-text {
  color: #2c3e50;
  font-size: 0.9rem;
}

/* Task Actions */
.task-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.btn-review-task,
.btn-generate-summary {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.btn-review-task {
  background: #f093fb;
  color: white;
}

.btn-review-task:hover {
  background: #f5576c;
}

.btn-generate-summary {
  background: #9c27b0;
  color: white;
}

.btn-generate-summary:hover:not(:disabled) {
  background: #7b1fa2;
}

.btn-generate-summary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-container.review-modal {
  max-width: 700px;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3rem;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 4px 8px;
  transition: opacity 0.3s ease;
}

.close-btn:hover {
  opacity: 0.7;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #2c3e50;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #f093fb;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.task-info-box,
.employee-review-box {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.task-info-box h4,
.employee-review-box h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.task-info-box p,
.employee-review-box p {
  margin: 0;
  color: #7f8c8d;
}

.review-textarea {
  font-family: inherit;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-cancel,
.btn-submit {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-cancel {
  background: #ecf0f1;
  color: #2c3e50;
}

.btn-cancel:hover {
  background: #dde1e3;
}

.btn-submit {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(240, 147, 251, 0.4);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .tasks-grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .filters-section {
    flex-direction: column;
  }
}
</style>
