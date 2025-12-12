<template>
  <DashboardLayout>
    <div class="candidate-tasks">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <h1>My Tasks</h1>
          <p>View and manage your assigned tasks</p>
        </div>
        <div class="header-actions">
          <button class="btn-refresh" @click="loadTasks">
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
            Refresh
          </button>
        </div>
      </div>

      <!-- Stats -->
      <div class="stats-grid">
        <div class="stat-card pending">
          <i class="fas fa-clock stat-icon"></i>
          <div class="stat-content">
            <h3>{{ pendingTasksCount }}</h3>
            <p>Pending Tasks</p>
          </div>
        </div>
        <div class="stat-card progress">
          <i class="fas fa-spinner stat-icon"></i>
          <div class="stat-content">
            <h3>{{ inProgressCount }}</h3>
            <p>In Progress</p>
          </div>
        </div>
        <div class="stat-card completed">
          <i class="fas fa-check-circle stat-icon"></i>
          <div class="stat-content">
            <h3>{{ completedCount }}</h3>
            <p>Completed</p>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-section">
        <div class="filter-group">
          <label>Status:</label>
          <select v-model="filterStatus">
            <option value="">All Tasks</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="reviewed">Reviewed</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Priority:</label>
          <select v-model="filterPriority">
            <option value="">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i>
        <p>Loading tasks...</p>
      </div>

      <!-- Tasks List -->
      <div v-else-if="filteredTasks.length > 0" class="tasks-list">
        <div v-for="task in filteredTasks" :key="task.id" class="task-card" :class="getTaskPriorityClass(task.priority)">
          <!-- Task Header -->
          <div class="task-header">
            <div class="task-title-section">
              <h4>{{ task.title }}</h4>
              <span class="priority-badge" :class="task.priority">
                <i class="fas fa-flag"></i>
                {{ formatPriority(task.priority) }}
              </span>
            </div>
            <div class="task-status-badge" :class="task.status">
              {{ formatTaskStatus(task.status) }}
            </div>
          </div>

          <!-- Task Description -->
          <div class="task-description">
            <p>{{ task.description }}</p>
          </div>

          <!-- Task Meta -->
          <div class="task-meta">
            <div class="meta-item">
              <i class="fas fa-user-tie"></i>
              <span>Assigned by: {{ task.assigned_by_name }}</span>
            </div>
            <div class="meta-item" :class="{ 'deadline-warning': isDeadlineNear(task.deadline) }">
              <i class="fas fa-clock"></i>
              <span>Deadline: {{ formatDateTime(task.deadline) }}</span>
            </div>
          </div>

          <!-- Reviews Section -->
          <div v-if="task.employee_review || task.manager_review" class="reviews-section">
            <!-- Employee Review -->
            <div v-if="task.employee_review" class="review-item employee-review">
              <div class="review-header">
                <i class="fas fa-user"></i>
                <strong>Your Review</strong>
                <small>{{ formatDate(task.employee_reviewed_at) }}</small>
              </div>
              <div class="review-text">{{ task.employee_review }}</div>
            </div>

            <!-- Manager Review -->
            <div v-if="task.manager_review" class="review-item manager-review">
              <div class="review-header">
                <i class="fas fa-user-tie"></i>
                <strong>Manager's Feedback</strong>
                <small>{{ formatDate(task.manager_reviewed_at) }}</small>
              </div>
              <div class="review-text">{{ task.manager_review }}</div>
            </div>

            <!-- AI Summary -->
            <div v-if="task.ai_summary" class="review-item ai-summary">
              <div class="review-header">
                <i class="fas fa-robot"></i>
                <strong>AI Performance Summary</strong>
                <small>{{ formatDate(task.ai_summary_generated_at) }}</small>
              </div>
              <div class="review-text ai-text" v-html="formatAISummary(task.ai_summary)">
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="task-actions">
            <!-- Submit Self Review -->
            <button v-if="!task.employee_review && task.status !== 'pending'" @click="openReviewModal(task)"
              class="btn-submit-review">
              <i class="fas fa-pencil-alt"></i>
              Submit Your Review
            </button>

            <!-- Generate AI Summary -->
            <button v-if="task.employee_review && task.manager_review && !task.ai_summary"
              @click="generateAISummary(task)" class="btn-generate-summary" :disabled="generatingSummary">
              <i class="fas fa-magic"></i>
              {{ generatingSummary ? 'Generating...' : 'Generate AI Summary' }}
            </button>

            <!-- Mark as In Progress -->
            <button v-if="task.status === 'pending'" @click="updateTaskStatus(task, 'in_progress')"
              class="btn-start-task">
              <i class="fas fa-play"></i>
              Start Task
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-clipboard-check"></i>
        </div>
        <h4>No Tasks Found</h4>
        <p>You don't have any tasks matching the selected filters.</p>
      </div>

      <!-- Review Modal -->
      <div v-if="showReviewModal" class="modal-overlay" @click="closeReviewModal">
        <div class="modal-container review-modal" @click.stop>
          <div class="modal-header">
            <h3>
              <i class="fas fa-pencil-alt"></i>
              Submit Task Review
            </h3>
            <button @click="closeReviewModal" class="close-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <div class="modal-body">
            <div class="task-info-box">
              <h4>{{ selectedTask?.title }}</h4>
              <p>{{ selectedTask?.description }}</p>
            </div>
            
            <div class="form-group">
              <label>Your Review</label>
              <textarea 
                v-model="employeeReview" 
                class="review-textarea"
                placeholder="Describe what you accomplished, challenges faced, and lessons learned..."
                rows="6"
              ></textarea>
              <small class="character-count">{{ employeeReview.length }} characters</small>
            </div>
          </div>
          
          <div class="modal-footer">
            <button @click="closeReviewModal" class="btn-cancel">Cancel</button>
            <button @click="submitEmployeeReview" class="btn-submit" :disabled="submittingReview || !employeeReview.trim()">
              <i class="fas fa-paper-plane"></i>
              {{ submittingReview ? 'Submitting...' : 'Submit Review' }}
            </button>
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
const tasks = ref([])
const loading = ref(false)
const filterStatus = ref('')
const filterPriority = ref('')
const showReviewModal = ref(false)
const selectedTask = ref(null)
const employeeReview = ref('')
const submittingReview = ref(false)
const generatingSummary = ref(false)

// Computed
const pendingTasksCount = computed(() => 
  tasks.value.filter(t => t.status === 'pending').length
)

const inProgressCount = computed(() => 
  tasks.value.filter(t => t.status === 'in_progress').length
)

const completedCount = computed(() => 
  tasks.value.filter(t => t.status === 'completed' || t.status === 'reviewed').length
)

const filteredTasks = computed(() => {
  let filtered = tasks.value

  if (filterStatus.value) {
    filtered = filtered.filter(t => t.status === filterStatus.value)
  }

  if (filterPriority.value) {
    filtered = filtered.filter(t => t.priority === filterPriority.value)
  }

  return filtered
})

// Functions
async function loadTasks() {
  loading.value = true
  try {
    const response = await axios.get('/api/tasks/today', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })

    if (response.data && response.data.tasks) {
      tasks.value = response.data.tasks
    }

    console.log('✅ Tasks loaded:', tasks.value.length)
  } catch (error) {
    console.error('❌ Failed to load tasks:', error)
    alert('Failed to load tasks')
  } finally {
    loading.value = false
  }
}

function getTaskPriorityClass(priority) {
  return `priority-${priority}`
}

function formatPriority(priority) {
  const priorityMap = {
    'low': 'Low',
    'medium': 'Medium',
    'high': 'High'
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

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

function formatDateTime(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function isDeadlineNear(deadline) {
  const now = new Date()
  const deadlineDate = new Date(deadline)
  const diffHours = (deadlineDate - now) / (1000 * 60 * 60)
  return diffHours <= 24 && diffHours >= 0
}

function openReviewModal(task) {
  selectedTask.value = task
  showReviewModal.value = true
  employeeReview.value = ''
}

function closeReviewModal() {
  showReviewModal.value = false
  selectedTask.value = null
  employeeReview.value = ''
}

async function submitEmployeeReview() {
  if (!employeeReview.value.trim()) return

  submittingReview.value = true
  try {
    await axios.post(
      `/api/tasks/${selectedTask.value.id}/employee-review`,
      { review: employeeReview.value },
      {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      }
    )

    alert('Review submitted successfully!')
    closeReviewModal()
    await loadTasks()
  } catch (error) {
    console.error('Failed to submit review:', error)
    alert('Failed to submit review. Please try again.')
  } finally {
    submittingReview.value = false
  }
}

async function generateAISummary(task) {
  try {
    generatingSummary.value = true

    const response = await axios.post(
      `/api/tasks/${task.id}/generate-ai-summary`,
      {},
      {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      }
    )

    alert('AI summary generated successfully!')
    await loadTasks()
  } catch (error) {
    console.error('Failed to generate AI summary:', error)
    alert('Failed to generate AI summary. Please try again.')
  } finally {
    generatingSummary.value = false
  }
}

async function updateTaskStatus(task, newStatus) {
  try {
    await axios.put(
      `/api/tasks/${task.id}`,
      { status: newStatus },
      {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      }
    )

    await loadTasks()
  } catch (error) {
    console.error('Failed to update task status:', error)
    alert('Failed to update task status.')
  }
}

function formatAISummary(summary) {
  if (!summary) return ''
  try {
    const parsed = typeof summary === 'string' ? JSON.parse(summary) : summary
    let html = '<div class="ai-summary-formatted">'
    if (parsed.Strengths) html += `<p><strong>💪 Strengths:</strong> ${parsed.Strengths}</p>`
    if (parsed.Weaknesses) html += `<p><strong>⚠️ Weaknesses:</strong> ${parsed.Weaknesses}</p>`
    if (parsed.Improvements) html += `<p><strong>📈 Improvements Needed:</strong> ${parsed.Improvements}</p>`
    if (parsed.Actionable_step) html += `<p><strong>🎯 Actionable Step:</strong> ${parsed.Actionable_step}</p>`
    if (parsed.Comments) html += `<p><strong>💬 Comments:</strong> ${parsed.Comments}</p>`
    html += '</div>'
    return html
  } catch (e) {
    console.error('Error parsing AI summary:', e)
    return summary
  }
}

// Load tasks on mount
onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.candidate-tasks {
  padding: 20px;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #ecf0f1;
}

.header-content h1 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 700;
}

.header-content p {
  margin: 0;
  color: #7f8c8d;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn-refresh {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-refresh:hover {
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
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-card.pending .stat-icon {
  color: #f39c12;
}

.stat-card.progress .stat-icon {
  color: #3498db;
}

.stat-card.completed .stat-icon {
  color: #27ae60;
}

.stat-icon {
  font-size: 2.5rem;
  opacity: 0.8;
}

.stat-content h3 {
  margin: 0 0 5px 0;
  font-size: 2rem;
  color: #2c3e50;
  font-weight: 700;
}

.stat-content p {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.95rem;
}

/* Filters */
.filters-section {
  background: white;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 25px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 20px;
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

.filter-group select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.filter-group select:focus {
  outline: none;
  border-color: #667eea;
}

/* Loading & Empty States */
.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.loading-state i {
  font-size: 4rem;
  color: #bdc3c7;
  margin-bottom: 20px;
}

.empty-state .empty-icon i {
  font-size: 4rem;
  color: #bdc3c7;
  margin-bottom: 20px;
}

.empty-state h4 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.empty-state p {
  color: #7f8c8d;
}

/* Tasks List */
.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.task-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border-left: 4px solid #ddd;
  transition: all 0.3s ease;
}

.task-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.task-card.priority-high {
  border-left-color: #e74c3c;
}

.task-card.priority-medium {
  border-left-color: #f39c12;
}

.task-card.priority-low {
  border-left-color: #27ae60;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 10px;
}

.task-title-section {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.task-title-section h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.priority-badge {
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.priority-badge.high {
  background: #fee;
  color: #e74c3c;
}

.priority-badge.medium {
  background: #fef5e7;
  color: #f39c12;
}

.priority-badge.low {
  background: #eafaf1;
  color: #27ae60;
}

.task-status-badge {
  padding: 6px 15px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.task-status-badge.pending {
  background: #f39c12;
  color: white;
}

.task-status-badge.in_progress {
  background: #3498db;
  color: white;
}

.task-status-badge.completed {
  background: #27ae60;
  color: white;
}

.task-status-badge.reviewed {
  background: #9b59b6;
  color: white;
}

.task-description {
  margin-bottom: 15px;
}

.task-description p {
  margin: 0;
  color: #555;
  line-height: 1.6;
}

.task-meta {
  display: flex;
  gap: 25px;
  flex-wrap: wrap;
  margin-bottom: 15px;
  padding-top: 15px;
  border-top: 1px solid #ecf0f1;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.meta-item i {
  color: #3498db;
}

.meta-item.deadline-warning {
  color: #e74c3c;
  font-weight: 600;
}

.meta-item.deadline-warning i {
  color: #e74c3c;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Reviews Section */
.reviews-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px solid #ecf0f1;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.review-item {
  padding: 15px;
  border-radius: 8px;
  background: #f8f9fa;
}

.review-item.employee-review {
  background: #f0f8ff;
  border-left: 3px solid #3498db;
}

.review-item.manager-review {
  background: #fff8f0;
  border-left: 3px solid #f39c12;
}

.review-item.ai-summary {
  background: #f0fff4;
  border-left: 3px solid #27ae60;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  color: #2c3e50;
}

.review-header i {
  font-size: 1.1rem;
}

.review-header strong {
  font-size: 1rem;
}

.review-header small {
  margin-left: auto;
  color: #7f8c8d;
  font-size: 0.85rem;
}

.review-text {
  padding-left: 30px;
  color: #555;
  line-height: 1.6;
}

.review-text.ai-text {
  font-size: 0.95rem;
}

/* Task Actions */
.task-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn-submit-review,
.btn-generate-summary,
.btn-start-task {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-submit-review {
  background: #3498db;
  color: white;
}

.btn-submit-review:hover {
  background: #2980b9;
}

.btn-generate-summary {
  background: #9b59b6;
  color: white;
}

.btn-generate-summary:hover:not(:disabled) {
  background: #8e44ad;
}

.btn-generate-summary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-start-task {
  background: #27ae60;
  color: white;
}

.btn-start-task:hover {
  background: #229954;
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
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-container.review-modal {
  max-width: 700px;
}

.modal-header {
  padding: 20px 25px;
  border-bottom: 1px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 10px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #7f8c8d;
  cursor: pointer;
  width: 35px;
  height: 35px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #ecf0f1;
  color: #2c3e50;
}

.modal-body {
  padding: 25px;
}

.task-info-box {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.task-info-box h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.task-info-box p {
  margin: 0;
  color: #555;
  font-size: 0.95rem;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #2c3e50;
  font-weight: 600;
}

.review-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-family: inherit;
  font-size: 1rem;
  resize: vertical;
  transition: border-color 0.3s ease;
}

.review-textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.character-count {
  display: block;
  margin-top: 5px;
  color: #7f8c8d;
  font-size: 0.85rem;
}

.modal-footer {
  padding: 20px 25px;
  border-top: 1px solid #ecf0f1;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-cancel,
.btn-submit {
  padding: 10px 25px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-cancel {
  background: #ecf0f1;
  color: #2c3e50;
}

.btn-cancel:hover {
  background: #dfe6e9;
}

.btn-submit {
  background: #3498db;
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-submit:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-2px);
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

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters-section {
    flex-direction: column;
  }

  .task-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .task-actions {
    flex-direction: column;
  }

  .task-actions button {
    width: 100%;
  }
}
</style>
