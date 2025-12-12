<template>
  <DashboardLayout>
    <div class="bda-interviews-page">
      <!-- Header -->
      <header class="dashboard-header">
        <div class="header-left">
          <h1>Behavioral Interviews</h1>
        </div>
      </header>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon scheduled">
            <i class="fas fa-calendar-check"></i>
          </div>
          <div class="stat-info">
            <h3>{{ stats.scheduled }}</h3>
            <p>Scheduled</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon completed">
            <i class="fas fa-check-double"></i>
          </div>
          <div class="stat-info">
            <h3>{{ stats.completed }}</h3>
            <p>Completed</p>
          </div>
        </div>
      </div>

      <!-- Interviews List -->
      <div class="interviews-container">
        <div v-if="loading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading interviews...</p>
        </div>
        
        <div v-else-if="interviews.length === 0" class="empty-state">
          <i class="fas fa-calendar-times"></i>
          <p>No interviews scheduled</p>
        </div>

        <div v-else class="interviews-grid">
          <div v-for="interview in interviews" :key="interview.id" class="interview-card">
            <div class="card-header">
              <div class="candidate-info">
                <div class="avatar">{{ getInitials(interview.candidate_name) }}</div>
                <div>
                  <h3>{{ interview.candidate_name }}</h3>
                  <span class="role">{{ interview.role }}</span>
                </div>
              </div>
              <span class="status-badge" :class="interview.status.toLowerCase()">
                {{ interview.status }}
              </span>
            </div>

            <div class="card-body">
              <div class="info-row">
                <i class="fas fa-calendar"></i>
                <span>{{ formatDate(interview.scheduled_at) }}</span>
              </div>
              <div class="info-row">
                <i class="fas fa-clock"></i>
                <span>{{ formatTime(interview.scheduled_at) }}</span>
              </div>
              <div class="info-row">
                <i class="fas fa-video"></i>
                <a :href="interview.meeting_link" target="_blank" class="meeting-link">Join Meeting</a>
              </div>
            </div>

            <div class="card-footer">
              <button v-if="interview.scorecard" class="action-btn secondary" @click="viewScorecard(interview)">
                <i class="fas fa-chart-bar"></i> View Scorecard
              </button>
              <button v-if="!interview.scorecard" class="action-btn primary" @click="openScoringModal(interview)">
                <i class="fas fa-star"></i> {{ interview.scorecard ? 'Update' : 'Submit' }} Scorecard
              </button>
              <button v-if="interview.status === 'scheduled' && interview.meeting_link" class="action-btn secondary" @click="startInterview(interview)">
                <i class="fas fa-video"></i> Join Meeting
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Scoring Modal -->
    <div v-if="showScoringModal" class="modal-overlay" @click="closeScoringModal">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h3><i class="fas fa-star"></i> Submit Interview Scorecard</h3>
          <button @click="closeScoringModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="candidate-info">
            <h4>{{ selectedInterview?.candidate_name }}</h4>
            <p>{{ selectedInterview?.job_title }}</p>
          </div>

          <form @submit.prevent="submitScoring" class="scoring-form">
            <!-- Score Inputs -->
            <div class="form-grid">
              <div class="form-group">
                <label>Technical Score (0-5)</label>
                <input 
                  type="number" 
                  v-model.number="scoringForm.technical_score" 
                  min="0" 
                  max="5" 
                  step="0.1"
                  placeholder="0.0"
                />
              </div>

              <div class="form-group">
                <label>Communication Score (0-5)</label>
                <input 
                  type="number" 
                  v-model.number="scoringForm.communication_score" 
                  min="0" 
                  max="5" 
                  step="0.1"
                  placeholder="0.0"
                  required
                />
              </div>

              <div class="form-group">
                <label>Problem Solving Score (0-5)</label>
                <input 
                  type="number" 
                  v-model.number="scoringForm.problem_solving_score" 
                  min="0" 
                  max="5" 
                  step="0.1"
                  placeholder="0.0"
                />
              </div>

              <div class="form-group">
                <label>Cultural Fit Score (0-5)</label>
                <input 
                  type="number" 
                  v-model.number="scoringForm.cultural_fit_score" 
                  min="0" 
                  max="5" 
                  step="0.1"
                  placeholder="0.0"
                />
              </div>
            </div>

            <div class="form-group">
              <label>Strengths</label>
              <textarea 
                v-model="scoringForm.strengths" 
                rows="3"
                placeholder="What were the candidate's main strengths?"
              ></textarea>
            </div>

            <div class="form-group">
              <label>Areas for Improvement</label>
              <textarea 
                v-model="scoringForm.weaknesses" 
                rows="3"
                placeholder="What areas could the candidate improve?"
              ></textarea>
            </div>

            <div class="form-group">
              <label>Additional Comments</label>
              <textarea 
                v-model="scoringForm.feedback_notes" 
                rows="4"
                placeholder="Any additional feedback or observations..."
              ></textarea>
            </div>

            <div class="form-group">
              <label>Recommendation</label>
              <select v-model="scoringForm.recommendation" required>
                <option value="strong_hire">Strong Hire</option>
                <option value="hire">Hire</option>
                <option value="maybe">Maybe</option>
                <option value="no_hire">No Hire</option>
              </select>
            </div>

            <div class="modal-actions">
              <button type="button" @click="closeScoringModal" class="action-btn secondary">
                Cancel
              </button>
              <button type="submit" class="action-btn primary" :disabled="submittingScore">
                <i v-if="submittingScore" class="fas fa-spinner fa-spin"></i>
                <span v-else>Submit Scorecard</span>
              </button>
            </div>
          </form>
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
const interviews = ref([])
const bdaId = ref('')

// Modal states
const showScoringModal = ref(false)
const selectedInterview = ref(null)
const submittingScore = ref(false)

// Scoring form
const scoringForm = ref({
  technical_score: null,
  communication_score: null,
  problem_solving_score: null,
  cultural_fit_score: null,
  strengths: '',
  weaknesses: '',
  feedback_notes: '',
  recommendation: ''
})

const stats = computed(() => {
  return {
    scheduled: interviews.value.filter(i => i.status === 'scheduled').length,
    completed: interviews.value.filter(i => i.status === 'completed').length
  }
})

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
    loadInterviews()
  } catch (error) {
    console.error('Error loading user data:', error)
  }
}

// ...existing code...
async function loadInterviews() {
  loading.value = true
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/pipeline/interview-assignments', {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        interviewer_id: bdaId.value
      }
    })
    
    const allInterviews = response.data.interview_assignments || []
    interviews.value = allInterviews.filter(i => i.interview_type === 'behavioral_interview')
    
    // Load scorecards for completed interviews
    await loadScorecards()
  } catch (error) {
    console.error('Error loading interviews:', error)
  } finally {
    loading.value = false
  }
}

async function loadScorecards() {
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/pipeline/scorecards', {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        interviewer_id: bdaId.value
      }
    })
    
    const scorecards = response.data.scorecards || []
    
    // Match scorecards to interviews
    interviews.value.forEach(interview => {
      const scorecard = scorecards.find(s => s.interview_assignment_id === interview.id)
      if (scorecard) {
        interview.scorecard = scorecard
      }
    })
  } catch (error) {
    console.error('Error loading scorecards:', error)
  }
}
// ...existing code...

function getInitials(name) {
  return name ? name.split(' ').map(n => n[0]).join('').toUpperCase() : '?'
}

function formatDate(dateString) {
  if (!dateString) return 'TBD'
  return new Date(dateString).toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  })
}

function formatTime(dateString) {
  if (!dateString) return 'TBD'
  return new Date(dateString).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

function openScoringModal(interview) {
  selectedInterview.value = interview
  scoringForm.value = {
    technical_score: null,
    communication_score: null,
    problem_solving_score: null,
    cultural_fit_score: null,
    strengths: '',
    weaknesses: '',
    feedback_notes: '',
    recommendation: 'hire'
  }
  showScoringModal.value = true
}

function closeScoringModal() {
  showScoringModal.value = false
  selectedInterview.value = null
}

async function submitScoring() {
  if (!selectedInterview.value) return
  
  submittingScore.value = true
  try {
    const token = getAuthToken()
    await axios.post('/api/pipeline/scorecard', {
      interview_assignment_id: selectedInterview.value.id,
      interviewer_id: bdaId.value,
      ...scoringForm.value,
      is_final: true
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    alert('Scorecard submitted successfully!')
    closeScoringModal()
    await loadInterviews()
  } catch (error) {
    console.error('Error submitting scorecard:', error)
    alert('Failed to submit scorecard')
  } finally {
    submittingScore.value = false
  }
}

function viewScorecard(interview) {
  // Navigate to scorecard view or open modal
  console.log('View scorecard for', interview.scorecard)
}

function startInterview(interview) {
  window.open(interview.meeting_link, '_blank')
}

onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.bda-interviews-page {
  padding: 24px;
  background: #f8f9fa;
  min-height: 100vh;
}

.dashboard-header {
  margin-bottom: 32px;
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
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
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

.stat-icon.scheduled { background: #e3f2fd; color: #1976d2; }
.stat-icon.completed { background: #d4edda; color: #28a745; }

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

/* Interviews Grid */
.interviews-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.interview-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  transition: transform 0.2s;
}

.interview-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.candidate-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.avatar {
  width: 48px;
  height: 48px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.1rem;
}

.candidate-info h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #2c3e50;
}

.role {
  font-size: 0.9rem;
  color: #7f8c8d;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  text-transform: capitalize;
}

.status-badge.scheduled { background: #e3f2fd; color: #1976d2; }
.status-badge.completed { background: #d4edda; color: #155724; }

.card-body {
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  color: #555;
}

.info-row i {
  width: 20px;
  color: #95a5a6;
}

.meeting-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.meeting-link:hover {
  text-decoration: underline;
}

.card-footer {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.action-btn {
  flex: 1;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.action-btn.primary {
  background: #667eea;
  color: white;
  border: none;
}

.action-btn.primary:hover {
  background: #5a6fd6;
}

.action-btn.secondary {
  background: white;
  border: 1px solid #ddd;
  color: #555;
}

.action-btn.secondary:hover {
  background: #f8f9fa;
  border-color: #ccc;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 12px;
  max-width: 700px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}

.modal-header {
  padding: 20px 25px;
  border-bottom: 2px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px 12px 0 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.close-btn {
  background: rgba(255,255,255,0.2);
  border: none;
  font-size: 1.5rem;
  color: white;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255,255,255,0.3);
}

.modal-body {
  padding: 25px;
}

.candidate-info {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 25px;
}

.candidate-info h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.candidate-info p {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.95rem;
}

.scoring-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.95rem;
}

.form-group input,
.form-group textarea,
.form-group select {
  padding: 10px 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group textarea {
  resize: vertical;
  font-family: inherit;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 2px solid #ecf0f1;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-actions {
    flex-direction: column-reverse;
  }
  
  .modal-actions .action-btn {
    width: 100%;
  }
}
</style>