<template>
  <DashboardLayout>
    <div class="performance-reviews">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <h1>Performance Reviews</h1>
          <p>View AI-generated performance reviews from task completions</p>
        </div>
        <div class="header-actions">
          <button class="btn-refresh" @click="loadPerformanceReviews">
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
            Refresh
          </button>
        </div>
      </div>

      <!-- Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <i class="fas fa-clipboard-check stat-icon"></i>
          <div class="stat-content">
            <h3>{{ totalReviews }}</h3>
            <p>Total Reviews</p>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-users stat-icon"></i>
          <div class="stat-content">
            <h3>{{ uniqueEmployees }}</h3>
            <p>Employees Reviewed</p>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-calendar-alt stat-icon"></i>
          <div class="stat-content">
            <h3>{{ reviewsThisMonth }}</h3>
            <p>This Month</p>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-section">
        <div class="filter-group">
          <label>Search Employee:</label>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search by employee name..."
          />
        </div>
        <div class="filter-group">
          <label>Sort By:</label>
          <select v-model="sortBy">
            <option value="recent">Most Recent</option>
            <option value="oldest">Oldest First</option>
            <option value="employee">Employee Name</option>
          </select>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i>
        <p>Loading performance reviews...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredReviews.length === 0" class="empty-state">
        <i class="fas fa-inbox"></i>
        <h3>No Performance Reviews Yet</h3>
        <p>Performance reviews will appear here once HO generates AI summaries for completed tasks.</p>
      </div>

      <!-- Reviews List -->
      <div v-else class="reviews-list">
        <div 
          v-for="review in filteredReviews" 
          :key="review.id"
          class="review-card"
        >
          <!-- Review Header -->
          <div class="review-header">
            <div class="employee-info">
              <div class="employee-avatar">
                <i class="fas fa-user"></i>
              </div>
              <div class="employee-details">
                <h3>{{ review.assigned_to_name }}</h3>
                <p class="task-title">{{ review.title }}</p>
              </div>
            </div>
            <div class="review-meta">
              <span class="review-date">
                <i class="fas fa-calendar"></i>
                {{ formatDate(review.ai_summary_generated_at) }}
              </span>
              <span class="priority-badge" :class="review.priority">
                {{ formatPriority(review.priority) }}
              </span>
            </div>
          </div>

          <!-- Task Details -->
          <div class="task-details">
            <div class="detail-row">
              <strong>Task Description:</strong>
              <p>{{ review.description }}</p>
            </div>
            <div class="detail-row">
              <strong>Assigned By:</strong>
              <span>{{ review.assigned_by_name }}</span>
            </div>
            <div class="detail-row">
              <strong>Deadline:</strong>
              <span>{{ formatDate(review.deadline) }}</span>
            </div>
          </div>

          <!-- Employee Review -->
          <div class="review-section employee-section">
            <div class="section-header">
              <i class="fas fa-user"></i>
              <strong>Employee Self-Review</strong>
              <small>{{ formatDate(review.employee_reviewed_at) }}</small>
            </div>
            <div class="section-content">
              {{ review.employee_review }}
            </div>
          </div>

          <!-- Manager Review -->
          <div class="review-section manager-section">
            <div class="section-header">
              <i class="fas fa-user-tie"></i>
              <strong>Manager Feedback</strong>
              <small>{{ formatDate(review.manager_reviewed_at) }}</small>
            </div>
            <div class="section-content">
              {{ review.manager_review }}
            </div>
          </div>

          <!-- AI Summary -->
          <div class="review-section ai-section">
            <div class="section-header">
              <i class="fas fa-robot"></i>
              <strong>AI Performance Analysis</strong>
            </div>
            <div class="section-content ai-content" v-html="formatAISummary(review.ai_summary)">
            </div>
          </div>

          <!-- Actions -->
          <div class="review-actions">
            <button class="btn-export" @click="exportReview(review)">
              <i class="fas fa-download"></i>
              Export Review
            </button>
            <button class="btn-view-task" @click="viewTask(review.id)">
              <i class="fas fa-eye"></i>
              View Task Details
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
const reviews = ref([])
const loading = ref(false)
const searchQuery = ref('')
const sortBy = ref('recent')

// Computed
const totalReviews = computed(() => reviews.value.length)

const uniqueEmployees = computed(() => {
  const employees = new Set(reviews.value.map(r => r.assigned_to_id))
  return employees.size
})

const reviewsThisMonth = computed(() => {
  const now = new Date()
  const thisMonth = reviews.value.filter(r => {
    const reviewDate = new Date(r.ai_summary_generated_at)
    return reviewDate.getMonth() === now.getMonth() && 
           reviewDate.getFullYear() === now.getFullYear()
  })
  return thisMonth.length
})

const filteredReviews = computed(() => {
  let filtered = reviews.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(r => 
      r.assigned_to_name.toLowerCase().includes(query) ||
      r.title.toLowerCase().includes(query)
    )
  }

  // Sort
  const sorted = [...filtered]
  if (sortBy.value === 'recent') {
    sorted.sort((a, b) => new Date(b.ai_summary_generated_at) - new Date(a.ai_summary_generated_at))
  } else if (sortBy.value === 'oldest') {
    sorted.sort((a, b) => new Date(a.ai_summary_generated_at) - new Date(b.ai_summary_generated_at))
  } else if (sortBy.value === 'employee') {
    sorted.sort((a, b) => a.assigned_to_name.localeCompare(b.assigned_to_name))
  }

  return sorted
})

// Functions
async function loadPerformanceReviews() {
  loading.value = true
  try {
    const response = await axios.get('/api/tasks/', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })

    // Filter only tasks that have AI summaries
    if (response.data && response.data.tasks) {
      reviews.value = response.data.tasks.filter(task => task.ai_summary)
    }

    console.log('✅ Loaded performance reviews:', reviews.value.length)
  } catch (error) {
    console.error('❌ Failed to load performance reviews:', error)
    alert('Failed to load performance reviews')
  } finally {
    loading.value = false
  }
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

function formatPriority(priority) {
  const map = {
    'high': 'High Priority',
    'medium': 'Medium Priority',
    'low': 'Low Priority'
  }
  return map[priority] || priority
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

function exportReview(review) {
  try {
    const parsed = JSON.parse(review.ai_summary)
    const content = `
PERFORMANCE REVIEW
==================

Employee: ${review.assigned_to_name}
Task: ${review.title}
Review Date: ${formatDate(review.ai_summary_generated_at)}

TASK DESCRIPTION:
${review.description}

EMPLOYEE SELF-REVIEW:
${review.employee_review}

MANAGER FEEDBACK:
${review.manager_review}

AI PERFORMANCE ANALYSIS:
------------------------
Strengths: ${parsed.Strengths || 'N/A'}
Weaknesses: ${parsed.Weaknesses || 'N/A'}
Improvements Needed: ${parsed.Improvements || 'N/A'}
Actionable Step: ${parsed.Actionable_step || 'N/A'}
Comments: ${parsed.Comments || 'N/A'}
    `.trim()

    const blob = new Blob([content], { type: 'text/plain' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `performance-review-${review.assigned_to_name.replace(/\s+/g, '-')}-${new Date().toISOString().split('T')[0]}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error exporting review:', error)
    alert('Failed to export review')
  }
}

function viewTask(taskId) {
  // Navigate to task details or open modal
  console.log('View task:', taskId)
  alert('Task details view coming soon!')
}

// Load data on mount
onMounted(() => {
  loadPerformanceReviews()
})
</script>

<style scoped>
.performance-reviews {
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

.stat-icon {
  font-size: 2.5rem;
  color: #667eea;
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

.filter-group input,
.filter-group select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.filter-group input:focus,
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

.loading-state i,
.empty-state i {
  font-size: 4rem;
  color: #bdc3c7;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.empty-state p {
  color: #7f8c8d;
}

/* Reviews List */
.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.review-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s ease;
}

.review-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

/* Review Header */
.review-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 25px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.employee-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.employee-avatar {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.employee-details h3 {
  margin: 0 0 5px 0;
  font-size: 1.3rem;
  font-weight: 600;
}

.task-title {
  margin: 0;
  opacity: 0.9;
  font-size: 0.95rem;
}

.review-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.review-date {
  display: flex;
  align-items: center;
  gap: 6px;
  opacity: 0.9;
}

.priority-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.25);
}

.priority-badge.high {
  background: #e74c3c;
}

.priority-badge.medium {
  background: #f39c12;
}

.priority-badge.low {
  background: #27ae60;
}

/* Task Details */
.task-details {
  padding: 20px 25px;
  background: #f8f9fa;
  border-bottom: 1px solid #ecf0f1;
}

.detail-row {
  margin-bottom: 12px;
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-row strong {
  color: #2c3e50;
  min-width: 150px;
}

.detail-row p {
  margin: 0;
  color: #555;
  flex: 1;
}

/* Review Sections */
.review-section {
  padding: 20px 25px;
  border-bottom: 1px solid #ecf0f1;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  color: #2c3e50;
}

.section-header i {
  font-size: 1.2rem;
}

.section-header strong {
  font-size: 1.1rem;
}

.section-header small {
  margin-left: auto;
  color: #7f8c8d;
}

.section-content {
  padding-left: 32px;
  color: #555;
  line-height: 1.6;
}

.employee-section {
  background: #f0f8ff;
}

.manager-section {
  background: #fff8f0;
}

.ai-section {
  background: #f0fff4;
}

.ai-content {
  font-size: 0.95rem;
}

.ai-content p {
  margin: 10px 0;
  padding: 8px 0;
}

.ai-content strong {
  color: #2c3e50;
  display: inline-block;
  margin-right: 8px;
}

/* Review Actions */
.review-actions {
  padding: 20px 25px;
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  background: #fafafa;
}

.btn-export,
.btn-view-task {
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

.btn-export {
  background: #3498db;
  color: white;
}

.btn-export:hover {
  background: #2980b9;
  transform: translateY(-2px);
}

.btn-view-task {
  background: white;
  color: #2c3e50;
  border: 2px solid #ddd;
}

.btn-view-task:hover {
  background: #f8f9fa;
  border-color: #667eea;
  color: #667eea;
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

  .review-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .review-meta {
    width: 100%;
    justify-content: flex-start;
  }

  .detail-row {
    flex-direction: column;
  }

  .detail-row strong {
    min-width: auto;
  }
}
</style>
