<template>
  <DashboardLayout>
    <div class="technical-interviews-page">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <h1><i class="fas fa-laptop-code"></i> Technical Interviews Management</h1>
          <p>Evaluate AI tests and manage technical interview schedules</p>
        </div>
        <button @click="refreshData" class="refresh-btn" :disabled="loading">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i> Refresh
        </button>
      </div>

      <!-- Tabs -->
      <div class="tabs-container">
        <div class="tabs-header">
          <button 
            @click="activeTab = 'ai-tests'" 
            :class="['tab-btn', { active: activeTab === 'ai-tests' }]"
          >
            <i class="fas fa-code"></i> AI Technical Tests
            <span v-if="pendingTestsCount > 0" class="badge">{{ pendingTestsCount }}</span>
          </button>
          <button 
            @click="activeTab = 'interviews'" 
            :class="['tab-btn', { active: activeTab === 'interviews' }]"
          >
            <i class="fas fa-video"></i> Interview Schedules
            <span v-if="upcomingInterviewsCount > 0" class="badge">{{ upcomingInterviewsCount }}</span>
          </button>
        </div>

        <!-- AI Tests Tab -->
        <div v-if="activeTab === 'ai-tests'" class="tab-content">
          <!-- Stats -->
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon pending"><i class="fas fa-clock"></i></div>
              <div class="stat-info">
                <h3>{{ pendingTestsCount }}</h3>
                <p>Pending Evaluation</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon completed"><i class="fas fa-check-circle"></i></div>
              <div class="stat-info">
                <h3>{{ evaluatedTestsCount }}</h3>
                <p>Evaluated</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon total"><i class="fas fa-clipboard-list"></i></div>
              <div class="stat-info">
                <h3>{{ aiTests.length }}</h3>
                <p>Total Tests</p>
              </div>
            </div>
          </div>

          <!-- Filters -->
          <div class="filters-section">
            <div class="filter-group">
              <label><i class="fas fa-filter"></i> Filter by Status:</label>
              <select v-model="testStatusFilter">
                <option value="all">All Tests</option>
                <option value="pending">Pending Evaluation</option>
                <option value="submitted">Submitted</option>
                <option value="evaluated">Evaluated</option>
              </select>
            </div>
            <div class="filter-group">
              <label><i class="fas fa-search"></i> Search:</label>
              <input 
                v-model="testSearchQuery" 
                type="text" 
                placeholder="Search candidate or job..."
              />
            </div>
          </div>

          <!-- Tests List -->
          <div v-if="loading" class="loading-state">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Loading technical tests...</p>
          </div>

          <div v-else-if="filteredAITests.length === 0" class="empty-state">
            <i class="fas fa-inbox"></i>
            <p>No technical tests found</p>
          </div>

          <div v-else class="tests-grid">
            <div v-for="test in filteredAITests" :key="test.id" class="test-card">
              <div class="test-header">
                <div class="test-info">
                  <h3>{{ test.candidate_name }}</h3>
                  <p class="job-title"><i class="fas fa-briefcase"></i> {{ test.job_title }}</p>
                </div>
                <span :class="['status-badge', test.status]">{{ formatTestStatus(test.status) }}</span>
              </div>

              <div class="test-details">
                <div class="detail-row">
                  <span class="label"><i class="fas fa-calendar"></i> Assigned:</span>
                  <span>{{ formatDate(test.created_at) }}</span>
                </div>
                <div class="detail-row">
                  <span class="label"><i class="fas fa-hourglass-end"></i> Deadline:</span>
                  <span>{{ formatDate(test.deadline) }}</span>
                </div>
                <div class="detail-row">
                  <span class="label"><i class="fas fa-clock"></i> Duration:</span>
                  <span>{{ test.duration_minutes }} minutes</span>
                </div>
                <div v-if="test.submitted_at" class="detail-row">
                  <span class="label"><i class="fas fa-check"></i> Submitted:</span>
                  <span>{{ formatDate(test.submitted_at) }}</span>
                </div>
              </div>

              <div v-if="test.assessment" class="assessment-info">
                <h4><i class="fas fa-star"></i> Evaluation Results</h4>
                <div class="score-display">
                  <div class="score-circle" :class="getScoreClass(test.assessment.score_percentage)">
                    {{ test.assessment.score_percentage }}%
                  </div>
                  <div class="score-details">
                    <p><strong>Recommendation:</strong> {{ test.assessment.recommendation }}</p>
                    <p v-if="test.assessment.comments"><strong>Comments:</strong> {{ test.assessment.comments }}</p>
                  </div>
                </div>
              </div>

              <div class="test-actions">
                <button 
                  v-if="test.status === 'submitted' && !test.assessment" 
                  @click="openEvaluationModal(test)" 
                  class="btn-primary"
                >
                  <i class="fas fa-clipboard-check"></i> Evaluate Test
                </button>
                <button 
                  v-if="test.status === 'submitted' || test.assessment" 
                  @click="viewTestDetails(test)" 
                  class="btn-secondary"
                >
                  <i class="fas fa-eye"></i> View Details
                </button>
                <button 
                  v-if="test.assessment" 
                  @click="openEvaluationModal(test)" 
                  class="btn-outline"
                >
                  <i class="fas fa-edit"></i> Re-evaluate
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Interviews Tab -->
        <div v-if="activeTab === 'interviews'" class="tab-content">
          <!-- Stats -->
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon upcoming"><i class="fas fa-calendar-check"></i></div>
              <div class="stat-info">
                <h3>{{ upcomingInterviewsCount }}</h3>
                <p>Upcoming</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon completed"><i class="fas fa-check-double"></i></div>
              <div class="stat-info">
                <h3>{{ completedInterviewsCount }}</h3>
                <p>Completed</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon total"><i class="fas fa-users"></i></div>
              <div class="stat-info">
                <h3>{{ technicalInterviews.length }}</h3>
                <p>Total Interviews</p>
              </div>
            </div>
          </div>

          <!-- Filters -->
          <div class="filters-section">
            <div class="filter-group">
              <label><i class="fas fa-filter"></i> Filter by Status:</label>
              <select v-model="interviewStatusFilter">
                <option value="all">All Interviews</option>
                <option value="scheduled">Scheduled</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            <div class="filter-group">
              <label><i class="fas fa-search"></i> Search:</label>
              <input 
                v-model="interviewSearchQuery" 
                type="text" 
                placeholder="Search candidate..."
              />
            </div>
          </div>

          <!-- Interviews List -->
          <div v-if="loading" class="loading-state">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Loading interviews...</p>
          </div>

          <div v-else-if="filteredInterviews.length === 0" class="empty-state">
            <i class="fas fa-inbox"></i>
            <p>No technical interviews found</p>
          </div>

          <div v-else class="interviews-list">
            <div v-for="interview in filteredInterviews" :key="interview.id" class="interview-card">
              <div class="interview-header">
                <div class="interview-time">
                  <div class="date">{{ formatDate(interview.scheduled_at) }}</div>
                  <div class="time">{{ formatTime(interview.scheduled_at) }}</div>
                </div>
                <div class="interview-info">
                  <h3>{{ interview.candidate_name }}</h3>
                  <p class="job-title"><i class="fas fa-briefcase"></i> {{ interview.job_title }}</p>
                  <p v-if="interview.meeting_link" class="meeting-link">
                    <i class="fas fa-link"></i> 
                    <a :href="interview.meeting_link" target="_blank">Join Meeting</a>
                  </p>
                </div>
                <span :class="['status-badge', interview.status]">{{ formatInterviewStatus(interview.status) }}</span>
              </div>

              <div v-if="interview.scorecard" class="scorecard-preview">
                <h4><i class="fas fa-star"></i> Interview Score</h4>
                <div class="scores-grid">
                  <div class="score-item">
                    <span class="label">Overall</span>
                    <span class="value">{{ interview.scorecard.overall_score?.toFixed(1) || 'N/A' }}/10</span>
                  </div>
                  <div class="score-item">
                    <span class="label">Technical</span>
                    <span class="value">{{ interview.scorecard.technical_score || 'N/A' }}/10</span>
                  </div>
                  <div class="score-item">
                    <span class="label">Communication</span>
                    <span class="value">{{ interview.scorecard.communication_score || 'N/A' }}/10</span>
                  </div>
                  <div class="score-item">
                    <span class="label">Problem Solving</span>
                    <span class="value">{{ interview.scorecard.problem_solving_score || 'N/A' }}/10</span>
                  </div>
                </div>
                <p class="recommendation">
                  <strong>Recommendation:</strong> {{ interview.scorecard.recommendation }}
                </p>
              </div>

              <div class="interview-actions">
                <button 
                  v-if="!interview.scorecard" 
                  @click="openScoringModal(interview)" 
                  class="btn-primary"
                >
                  <i class="fas fa-clipboard-check"></i> Score Interview
                </button>
                <button 
                  v-if="interview.scorecard" 
                  @click="viewScorecard(interview)" 
                  class="btn-secondary"
                >
                  <i class="fas fa-eye"></i> View Full Scorecard
                </button>
                <button 
                  v-if="interview.scorecard" 
                  @click="openScoringModal(interview)" 
                  class="btn-outline"
                >
                  <i class="fas fa-edit"></i> Edit Score
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Evaluation Modal -->
      <div v-if="showEvaluationModal" class="modal-overlay" @click="closeEvaluationModal">
        <div class="modal-container evaluation-modal" @click.stop>
          <div class="modal-header">
            <h3><i class="fas fa-clipboard-check"></i> Evaluate Technical Test</h3>
            <button @click="closeEvaluationModal" class="close-btn">&times;</button>
          </div>

          <div class="modal-body">
            <div class="candidate-info">
              <h4>{{ selectedTest?.candidate_name }}</h4>
              <p>{{ selectedTest?.job_title }}</p>
              <p><strong>Test Status:</strong> {{ formatTestStatus(selectedTest?.status) }}</p>
            </div>

            <!-- Questions & Answers Section -->
            <div v-if="testQuestionsAndAnswers.length > 0" class="questions-answers-section">
              <h4><i class="fas fa-question-circle"></i> Questions & Candidate Answers</h4>
              
              <div class="qa-list">
                <div 
                  v-for="(qa, index) in testQuestionsAndAnswers" 
                  :key="index" 
                  class="qa-item"
                  :class="qa.difficulty"
                >
                  <div class="qa-header">
                    <span class="question-number">Q{{ index + 1 }}</span>
                    <span class="difficulty-badge" :class="qa.difficulty">{{ qa.difficulty }}</span>
                  </div>
                  
                  <div class="question-text">
                    <strong>Question:</strong> {{ qa.question }}
                  </div>
                  
                  <div class="answer-text" :class="{ 'no-answer': !qa.answer }">
                    <strong>Answer:</strong> 
                    <span v-if="qa.answer">{{ qa.answer }}</span>
                    <span v-else class="empty-answer"><i class="fas fa-times-circle"></i> No answer provided</span>
                  </div>
                </div>
              </div>
            </div>

            <form @submit.prevent="submitEvaluation" class="evaluation-form">
              <div class="form-group">
                <label>Score Percentage <span class="required">*</span></label>
                <input 
                  v-model.number="evaluationForm.score_percentage" 
                  type="number" 
                  min="0" 
                  max="100" 
                  required 
                  placeholder="0-100"
                />
              </div>

              <div class="form-group">
                <label>Recommendation <span class="required">*</span></label>
                <select v-model="evaluationForm.recommendation" required>
                  <option value="">Select recommendation</option>
                  <option value="Strongly Recommended">Strongly Recommended</option>
                  <option value="Recommended">Recommended</option>
                  <option value="Maybe">Maybe</option>
                  <option value="Not Recommended">Not Recommended</option>
                </select>
              </div>

              <div class="form-group">
                <label>Strengths</label>
                <textarea 
                  v-model="evaluationForm.strengths" 
                  rows="3" 
                  placeholder="Identify candidate's strengths..."
                ></textarea>
              </div>

              <div class="form-group">
                <label>Weaknesses</label>
                <textarea 
                  v-model="evaluationForm.weaknesses" 
                  rows="3" 
                  placeholder="Identify areas for improvement..."
                ></textarea>
              </div>

              <div class="form-group">
                <label>Feedback & Comments</label>
                <textarea 
                  v-model="evaluationForm.feedback" 
                  rows="4" 
                  placeholder="Detailed feedback..."
                ></textarea>
              </div>

              <div class="form-group">
                <label>Comments</label>
                <textarea 
                  v-model="evaluationForm.comments" 
                  rows="3" 
                  placeholder="Additional comments..."
                ></textarea>
              </div>

              <div class="modal-actions">
                <button type="button" @click="closeEvaluationModal" class="btn-secondary">Cancel</button>
                <button type="submit" class="btn-primary" :disabled="submittingEvaluation">
                  <i class="fas fa-save"></i> {{ submittingEvaluation ? 'Saving...' : 'Submit Evaluation' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Scoring Modal -->
      <div v-if="showScoringModal" class="modal-overlay" @click="closeScoringModal">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3><i class="fas fa-clipboard-check"></i> Score Technical Interview</h3>
            <button @click="closeScoringModal" class="close-btn">&times;</button>
          </div>

          <div class="modal-body">
            <div class="candidate-info">
              <h4>{{ selectedInterview?.candidate_name }}</h4>
              <p>{{ selectedInterview?.job_title }}</p>
              <p>Interview Date: {{ formatDate(selectedInterview?.scheduled_at) }}</p>
            </div>

            <form @submit.prevent="submitScoring" class="scoring-form">
              <div class="scores-section">
                <h4>Technical Scores (0-10)</h4>
                <div class="form-row">
                  <div class="form-group">
                    <label>Technical Skills <span class="required">*</span></label>
                    <input 
                      v-model.number="scoringForm.technical_score" 
                      type="number" 
                      min="0" 
                      max="10" 
                      step="0.1"
                      required 
                    />
                  </div>
                  <div class="form-group">
                    <label>Communication <span class="required">*</span></label>
                    <input 
                      v-model.number="scoringForm.communication_score" 
                      type="number" 
                      min="0" 
                      max="10" 
                      step="0.1"
                      required 
                    />
                  </div>
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label>Problem Solving <span class="required">*</span></label>
                    <input 
                      v-model.number="scoringForm.problem_solving_score" 
                      type="number" 
                      min="0" 
                      max="10" 
                      step="0.1"
                      required 
                    />
                  </div>
                  <div class="form-group">
                    <label>Cultural Fit <span class="required">*</span></label>
                    <input 
                      v-model.number="scoringForm.cultural_fit_score" 
                      type="number" 
                      min="0" 
                      max="10" 
                      step="0.1"
                      required 
                    />
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label>Strengths</label>
                <textarea 
                  v-model="scoringForm.strengths" 
                  rows="3" 
                  placeholder="Key strengths demonstrated..."
                ></textarea>
              </div>

              <div class="form-group">
                <label>Weaknesses</label>
                <textarea 
                  v-model="scoringForm.weaknesses" 
                  rows="3" 
                  placeholder="Areas needing improvement..."
                ></textarea>
              </div>

              <div class="form-group">
                <label>Feedback Notes</label>
                <textarea 
                  v-model="scoringForm.feedback_notes" 
                  rows="4" 
                  placeholder="Detailed interview feedback..."
                ></textarea>
              </div>

              <div class="form-group">
                <label>Recommendation <span class="required">*</span></label>
                <select v-model="scoringForm.recommendation" required>
                  <option value="">Select recommendation</option>
                  <option value="Strong Hire">Strong Hire</option>
                  <option value="Hire">Hire</option>
                  <option value="Maybe">Maybe</option>
                  <option value="No Hire">No Hire</option>
                </select>
              </div>

              <div class="modal-actions">
                <button type="button" @click="closeScoringModal" class="btn-secondary">Cancel</button>
                <button type="submit" class="btn-primary" :disabled="submittingScore">
                  <i class="fas fa-save"></i> {{ submittingScore ? 'Saving...' : 'Submit Scorecard' }}
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
import { useRouter } from 'vue-router'
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'

const router = useRouter()

// State
const userData = ref([])
const activeTab = ref('ai-tests')
const loading = ref(false)
const aiTests = ref([])
const technicalInterviews = ref([])

// Filters
const testStatusFilter = ref('all')
const testSearchQuery = ref('')
const interviewStatusFilter = ref('all')
const interviewSearchQuery = ref('')

// Modals
const showEvaluationModal = ref(false)
const showScoringModal = ref(false)
const selectedTest = ref(null)
const selectedInterview = ref(null)
const submittingEvaluation = ref(false)
const submittingScore = ref(false)
const testQuestionsAndAnswers = ref([])

// Forms
const evaluationForm = ref({
  score_percentage: null,
  recommendation: '',
  strengths: '',
  weaknesses: '',
  feedback: '',
  comments: ''
})


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

// Computed
const pendingTestsCount = computed(() => 
  aiTests.value.filter(t => t.status === 'submitted' && !t.assessment).length
)

const evaluatedTestsCount = computed(() => 
  aiTests.value.filter(t => t.assessment).length
)

const upcomingInterviewsCount = computed(() => 
  technicalInterviews.value.filter(i => i.status === 'scheduled').length
)

const completedInterviewsCount = computed(() => 
  technicalInterviews.value.filter(i => i.status === 'completed').length
)

const filteredAITests = computed(() => {
  let filtered = aiTests.value

  // Status filter
  if (testStatusFilter.value !== 'all') {
    if (testStatusFilter.value === 'pending') {
      filtered = filtered.filter(t => t.status === 'submitted' && !t.assessment)
    } else if (testStatusFilter.value === 'evaluated') {
      filtered = filtered.filter(t => t.assessment)
    } else {
      filtered = filtered.filter(t => t.status === testStatusFilter.value)
    }
  }

  // Search filter
  if (testSearchQuery.value) {
    const query = testSearchQuery.value.toLowerCase()
    filtered = filtered.filter(t => 
      t.candidate_name?.toLowerCase().includes(query) ||
      t.job_title?.toLowerCase().includes(query)
    )
  }

  return filtered
})

const filteredInterviews = computed(() => {
  let filtered = technicalInterviews.value

  // Status filter
  if (interviewStatusFilter.value !== 'all') {
    filtered = filtered.filter(i => i.status === interviewStatusFilter.value)
  }

  // Search filter
  if (interviewSearchQuery.value) {
    const query = interviewSearchQuery.value.toLowerCase()
    filtered = filtered.filter(i => 
      i.candidate_name?.toLowerCase().includes(query) ||
      i.job_title?.toLowerCase().includes(query)
    )
  }

  return filtered
})

// Helper Functions
const getAuthToken = () => localStorage.getItem('access_token')

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

function formatTime(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatTestStatus(status) {
  const map = {
    'pending': 'Pending',
    'submitted': 'Submitted',
    'evaluated': 'Evaluated',
    'expired': 'Expired'
  }
  return map[status] || status
}

function formatInterviewStatus(status) {
  const map = {
    'scheduled': 'Scheduled',
    'completed': 'Completed',
    'cancelled': 'Cancelled'
  }
  return map[status] || status
}

function getScoreClass(score) {
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  if (score >= 40) return 'average'
  return 'poor'
}

// API Functions
async function loadAITests() {
  loading.value = true
  try {
    const response = await axios.get('/api/ai/ho/technical-tests', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data && response.data.tests) {
      aiTests.value = response.data.tests
    }
  } catch (error) {
    console.error('❌ Failed to load AI tests:', error)
    alert('Failed to load AI technical tests')
  } finally {
    loading.value = false
  }
}

async function loadTechnicalInterviews() {
  loading.value = true
  try {
    const response = await axios.get('/api/pipeline/interview-assignments', {
      headers: { Authorization: `Bearer ${getAuthToken()}` },
      params: { 
        interviewer_id: userData.value.id,
        interview_type: 'technical_interview'
      }
    })

    if (response.data && response.data.interview_assignments) {
      technicalInterviews.value = response.data.interview_assignments
    }
  } catch (error) {
    console.error('❌ Failed to load technical interviews:', error)
    alert('Failed to load technical interviews')
  } finally {
    loading.value = false
  }
}

async function refreshData() {
  if (activeTab.value === 'ai-tests') {
    await loadAITests()
  } else {
    await loadTechnicalInterviews()
  }
}

// Modal Functions
function openEvaluationModal(test) {
  selectedTest.value = test
  
  // Parse questions and answers
  testQuestionsAndAnswers.value = parseQuestionsAndAnswers(test)
  
  // Pre-fill form if re-evaluating
  if (test.assessment) {
    evaluationForm.value = {
      score_percentage: test.assessment.score_percentage,
      recommendation: test.assessment.recommendation,
      strengths: test.assessment.strengths || '',
      weaknesses: test.assessment.weaknesses || '',
      feedback: test.assessment.feedback || '',
      comments: test.assessment.comments || ''
    }
  } else {
    evaluationForm.value = {
      score_percentage: null,
      recommendation: '',
      strengths: '',
      weaknesses: '',
      feedback: '',
      comments: ''
    }
  }
  
  showEvaluationModal.value = true
}

function parseQuestionsAndAnswers(test) {
  const qaList = []
  
  try {
    // Parse questions
    const questions = JSON.parse(test.questions || '{}')
    
    // Parse answers (array of strings)
    let answers = []
    if (test.answers) {
      answers = JSON.parse(test.answers)
    }
    
    let answerIndex = 0
    
    // Process questions by difficulty
    const difficulties = ['easy', 'medium', 'hard']
    
    for (const difficulty of difficulties) {
      const difficultyQuestions = questions[difficulty] || questions[`${difficulty}_questions`] || []
      
      for (const qObj of difficultyQuestions) {
        qaList.push({
          question: qObj.question || qObj,
          answer: answers[answerIndex] || '',
          difficulty: difficulty
        })
        answerIndex++
      }
    }
  } catch (error) {
    console.error('Error parsing questions/answers:', error)
  }
  
  return qaList
}

function closeEvaluationModal() {
  showEvaluationModal.value = false
  selectedTest.value = null
  testQuestionsAndAnswers.value = []
}

function openScoringModal(interview) {
  selectedInterview.value = interview
  
  // Pre-fill form if editing
  if (interview.scorecard) {
    scoringForm.value = {
      technical_score: interview.scorecard.technical_score,
      communication_score: interview.scorecard.communication_score,
      problem_solving_score: interview.scorecard.problem_solving_score,
      cultural_fit_score: interview.scorecard.cultural_fit_score,
      strengths: interview.scorecard.strengths || '',
      weaknesses: interview.scorecard.weaknesses || '',
      feedback_notes: interview.scorecard.feedback_notes || '',
      recommendation: interview.scorecard.recommendation || ''
    }
  } else {
    scoringForm.value = {
      technical_score: null,
      communication_score: null,
      problem_solving_score: null,
      cultural_fit_score: null,
      strengths: '',
      weaknesses: '',
      feedback_notes: '',
      recommendation: ''
    }
  }
  
  showScoringModal.value = true
}

function closeScoringModal() {
  showScoringModal.value = false
  selectedInterview.value = null
}

async function submitEvaluation() {
  if (!selectedTest.value) return

  submittingEvaluation.value = true
  try {
 
    
    // Calculate scores from evaluation form
    const totalQuestions = JSON.parse(selectedTest.value.questions || '[]').length || 1
    const maxScore = 100

    const response = await axios.post('/api/ai/submit-assessment', {
      test_id: selectedTest.value.id,
      candidate_id: selectedTest.value.candidate_id,
      score_percentage: evaluationForm.value.score_percentage,
      strengths: evaluationForm.value.strengths,
      weaknesses: evaluationForm.value.weaknesses,
      feedback: evaluationForm.value.feedback,
      recommendation: evaluationForm.value.recommendation,
      assessed_by: userData.value.id
    }, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    alert('✅ Test evaluation submitted successfully!')
    closeEvaluationModal()
    await loadAITests()
  } catch (error) {
    console.error('❌ Failed to submit evaluation:', error)
    alert(error.response?.data?.error || 'Failed to submit evaluation')
  } finally {
    submittingEvaluation.value = false
  }
}

async function submitScoring() {
  if (!selectedInterview.value) return

  submittingScore.value = true
  try {
    const currentUserId = userData.value.id

    const response = await axios.post('/api/pipeline/scorecard', {
      interview_assignment_id: selectedInterview.value.id,
      interviewer_id: currentUserId,
      ...scoringForm.value,
      force_update: selectedInterview.value.scorecard ? true : false
    }, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    alert('✅ Interview scorecard submitted successfully!')
    closeScoringModal()
    await loadTechnicalInterviews()
  } catch (error) {
    console.error('❌ Failed to submit scorecard:', error)
    alert(error.response?.data?.error || 'Failed to submit scorecard')
  } finally {
    submittingScore.value = false
  }
}

function viewTestDetails(test) {
  // Navigate to detailed test view or open in modal
  alert(`View full test details for ${test.candidate_name}`)
  // TODO: Implement detailed view
}

function viewScorecard(interview) {
  // Navigate to detailed scorecard view or open in modal
  alert(`View full scorecard for ${interview.candidate_name}`)
  // TODO: Implement detailed view
}


async function loadHOData() {
  // Load HR dashboard data
  try{
    const response = await axios.get('/api/users/', {
    headers: { Authorization: `Bearer ${getAuthToken()}` }
  })

  if (response.data) {
    userData.value = response.data
    }
  }
  catch(error) {
    console.error('Failed to load HR data:', error)
  }
}

// Load data on mount
onMounted(async () => {
  await loadHOData()
  await loadAITests()
  await loadTechnicalInterviews()
})
</script>

<style scoped>
.technical-interviews-page {
  padding: 24px;
  background-color: #f4f7fa;
  min-height: 100vh;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.header-content h1 {
  margin: 0 0 8px 0;
  font-size: 1.8rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-content p {
  margin: 0;
  opacity: 0.9;
}

.refresh-btn {
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.3);
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(255,255,255,0.3);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Tabs */
.tabs-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow: hidden;
}

.tabs-header {
  display: flex;
  border-bottom: 2px solid #ecf0f1;
  background: #f8f9fa;
}

.tab-btn {
  flex: 1;
  padding: 16px 24px;
  background: transparent;
  border: none;
  font-size: 1.05rem;
  font-weight: 600;
  color: #7f8c8d;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
}

.tab-btn:hover {
  background: rgba(102, 126, 234, 0.05);
  color: #667eea;
}

.tab-btn.active {
  color: #667eea;
  background: white;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: #667eea;
}

.tab-btn .badge {
  background: #e74c3c;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 700;
}

/* Tab Content */
.tab-content {
  padding: 24px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  border-left: 4px solid #667eea;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.stat-icon.pending { background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); }
.stat-icon.completed { background: linear-gradient(135deg, #27ae60 0%, #229954 100%); }
.stat-icon.total { background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); }
.stat-icon.upcoming { background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); }

.stat-info h3 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 700;
  color: #2c3e50;
}

.stat-info p {
  margin: 4px 0 0 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

/* Filters */
.filters-section {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
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
  display: flex;
  align-items: center;
  gap: 6px;
}

.filter-group select,
.filter-group input {
  padding: 10px 14px;
  border: 1px solid #dce1e6;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.filter-group select:focus,
.filter-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Loading & Empty States */
.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.loading-state i,
.empty-state i {
  font-size: 3rem;
  margin-bottom: 16px;
  display: block;
}

/* Tests Grid */
.tests-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.test-card {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  transition: all 0.3s ease;
}

.test-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

.test-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 2px solid #ecf0f1;
}

.test-info h3 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.job-title {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
}

.status-badge.pending { background: #fff3cd; color: #856404; }
.status-badge.submitted { background: #d1ecf1; color: #0c5460; }
.status-badge.evaluated { background: #d4edda; color: #155724; }
.status-badge.expired { background: #f8d7da; color: #721c24; }
.status-badge.scheduled { background: #d1ecf1; color: #0c5460; }
.status-badge.completed { background: #d4edda; color: #155724; }
.status-badge.cancelled { background: #f8d7da; color: #721c24; }

.test-details {
  margin-bottom: 16px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 0.9rem;
}

.detail-row .label {
  color: #7f8c8d;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.assessment-info {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.assessment-info h4 {
  margin: 0 0 12px 0;
  font-size: 0.95rem;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 6px;
}

.score-display {
  display: flex;
  gap: 16px;
  align-items: center;
}

.score-circle {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  font-weight: 700;
  color: white;
}

.score-circle.excellent { background: linear-gradient(135deg, #27ae60, #229954); }
.score-circle.good { background: linear-gradient(135deg, #3498db, #2980b9); }
.score-circle.average { background: linear-gradient(135deg, #f39c12, #e67e22); }
.score-circle.poor { background: linear-gradient(135deg, #e74c3c, #c0392b); }

.score-details {
  flex: 1;
}

.score-details p {
  margin: 6px 0;
  font-size: 0.85rem;
}

.test-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* Interviews List */
.interviews-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.interview-card {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  transition: all 0.3s ease;
}

.interview-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.interview-header {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 2px solid #ecf0f1;
}

.interview-time {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
  min-width: 100px;
}

.interview-time .date {
  font-weight: 700;
  font-size: 0.95rem;
  margin-bottom: 4px;
}

.interview-time .time {
  font-size: 0.85rem;
  opacity: 0.9;
}

.interview-info {
  flex: 1;
}

.interview-info h3 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.meeting-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.meeting-link a:hover {
  text-decoration: underline;
}

.scorecard-preview {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.scorecard-preview h4 {
  margin: 0 0 12px 0;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.scores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.score-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.score-item .label {
  font-size: 0.8rem;
  color: #7f8c8d;
  font-weight: 600;
}

.score-item .value {
  font-size: 1.1rem;
  color: #2c3e50;
  font-weight: 700;
}

.recommendation {
  font-size: 0.9rem;
  margin: 8px 0 0 0;
}

.interview-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* Buttons */
.btn-primary,
.btn-secondary,
.btn-outline {
  padding: 10px 18px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #7f8c8d;
}

.btn-outline {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-outline:hover:not(:disabled) {
  background: #667eea;
  color: white;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Modal */
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
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 2px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea, #764ba2);
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
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255,255,255,0.3);
  transform: rotate(90deg);
}

.modal-body {
  padding: 24px;
}

.candidate-info {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.candidate-info h4 {
  margin: 0 0 6px 0;
  color: #2c3e50;
}

.candidate-info p {
  margin: 4px 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

/* Questions & Answers Section */
.questions-answers-section {
  margin-bottom: 24px;
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
}

.questions-answers-section h4 {
  margin: 0 0 16px 0;
  color: #2c3e50;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 8px;
  position: sticky;
  top: 0;
  background: #fafafa;
  padding-bottom: 12px;
  border-bottom: 2px solid #e0e0e0;
  z-index: 1;
}

.qa-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.qa-item {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s ease;
}

.qa-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.qa-item.easy {
  border-left: 4px solid #27ae60;
}

.qa-item.medium {
  border-left: 4px solid #f39c12;
}

.qa-item.hard {
  border-left: 4px solid #e74c3c;
}

.qa-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.question-number {
  font-weight: 700;
  color: #2c3e50;
  background: #ecf0f1;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
}

.difficulty-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.difficulty-badge.easy {
  background: #d4edda;
  color: #155724;
}

.difficulty-badge.medium {
  background: #fff3cd;
  color: #856404;
}

.difficulty-badge.hard {
  background: #f8d7da;
  color: #721c24;
}

.question-text {
  margin-bottom: 12px;
  line-height: 1.6;
}

.question-text strong {
  color: #34495e;
  display: block;
  margin-bottom: 6px;
}

.answer-text {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  line-height: 1.6;
}

.answer-text strong {
  color: #34495e;
  display: block;
  margin-bottom: 6px;
}

.answer-text.no-answer {
  background: #fff3cd;
  border: 1px dashed #ffc107;
}

.empty-answer {
  color: #856404;
  font-style: italic;
  display: flex;
  align-items: center;
  gap: 6px;
}

.modal-container.evaluation-modal {
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
}

/* Forms */
.evaluation-form,
.scoring-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

.form-group .required {
  color: #e74c3c;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 14px;
  border: 1px solid #dce1e6;
  border-radius: 8px;
  font-size: 0.95rem;
  font-family: inherit;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.scores-section {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.scores-section h4 {
  margin: 0 0 12px 0;
  color: #2c3e50;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px solid #ecf0f1;
}

/* Responsive */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .tests-grid {
    grid-template-columns: 1fr;
  }

  .filters-section {
    flex-direction: column;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .interview-header {
    flex-direction: column;
  }

  .scores-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
