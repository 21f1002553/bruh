<template>
  <DashboardLayout>
    <div class="hr-onboarding">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <h1>Onboarding Management</h1>
          <p>Review and verify candidate documents in the onboarding stage</p>
        </div>
        <div class="header-actions">
          <button class="btn-refresh" @click="refreshData" :disabled="loading">
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
            Refresh
          </button>
        </div>
      </div>

      <!-- Stats Overview -->
      <div class="stats-grid">
        <div class="stat-card">
          <i class="fas fa-users stat-icon"></i>
          <div class="stat-content">
            <h3>{{ stats.totalCandidates }}</h3>
            <p>Total Candidates</p>
          </div>
        </div>
        <div class="stat-card pending">
          <i class="fas fa-clock stat-icon"></i>
          <div class="stat-content">
            <h3>{{ stats.pendingDocs }}</h3>
            <p>Pending Documents</p>
          </div>
        </div>
        <div class="stat-card verified">
          <i class="fas fa-check-circle stat-icon"></i>
          <div class="stat-content">
            <h3>{{ stats.verifiedDocs }}</h3>
            <p>Verified Documents</p>
          </div>
        </div>
        <div class="stat-card ready">
          <i class="fas fa-user-check stat-icon"></i>
          <div class="stat-content">
            <h3>{{ stats.readyToHire }}</h3>
            <p>Ready to Hire</p>
          </div>
        </div>
      </div>

      <!-- Candidates List -->
      <div class="candidates-section">
        <h2>Candidates in Onboarding</h2>
        
        <div v-if="candidatesLoading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading candidates...</p>
        </div>

        <div v-else-if="onboardingCandidates.length === 0" class="empty-state">
          <i class="fas fa-inbox"></i>
          <p>No candidates in onboarding stage</p>
        </div>

        <div v-else class="candidates-grid">
          <div 
            v-for="candidate in onboardingCandidates" 
            :key="candidate.candidate_id"
            class="candidate-card"
          >
            <div class="candidate-header">
              <div class="candidate-avatar">
                {{ getInitials(candidate.candidate_name) }}
              </div>
              <div class="candidate-info">
                <h3>{{ candidate.name }}</h3>
                <p>{{ candidate.email }}</p>
                <span class="job-title">{{ candidate.job_title }}</span>
              </div>
            </div>

            <div class="progress-section">
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: calculateProgress(candidate.candidate_id) + '%' }"
                ></div>
              </div>
              <span class="progress-text">
                {{ getVerifiedCount(candidate.candidate_id) }}/{{ requiredDocsCount }} documents verified
              </span>
            </div>

            <div class="documents-list">
              <h4>Documents</h4>
              <div 
                v-for="docType in requiredDocTypes" 
                :key="docType.value"
                class="document-item"
              >
                <div class="doc-name">
                  <i :class="getDocIcon(candidate.candidate_id, docType.value)"></i>
                  {{ docType.label }}
                </div>
                <div class="doc-actions-inline">
                  <span 
                    class="status-badge" 
                    :class="getDocStatusClass(candidate.candidate_id, docType.value)"
                  >
                    {{ getDocStatus(candidate.candidate_id, docType.value) }}
                  </span>
                  
                  <button 
                    v-if="hasDocument(candidate.candidate_id, docType.value)"
                    class="btn-icon"
                    @click="viewDocument(candidate.candidate_id, docType.value)"
                    title="View Document"
                  >
                    <i class="fas fa-eye"></i>
                  </button>

                  <button 
                    v-if="hasDocument(candidate.candidate_id, docType.value) && !isDocVerified(candidate.candidate_id, docType.value)"
                    class="btn-icon verify"
                    @click="verifyDocument(candidate.candidate_id, docType.value)"
                    title="Verify Document"
                  >
                    <i class="fas fa-check"></i>
                  </button>

                  <button 
                    v-if="isDocVerified(candidate.candidate_id, docType.value)"
                    class="btn-icon unverify"
                    @click="unverifyDocument(candidate.candidate_id, docType.value)"
                    title="Unverify Document"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>

            <div class="candidate-actions">
              <button 
                class="btn-hire"
                :disabled="!canHire(candidate.candidate_id) || hiringCandidate === candidate.candidate_id"
                @click="hireCandidate(candidate)"
              >
                <i class="fas fa-user-check"></i>
                {{ hiringCandidate === candidate.candidate_id ? 'Hiring...' : 'Hire Candidate' }}
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
const loading = ref(false)
const candidatesLoading = ref(false)
const hiringCandidate = ref(null)
const onboardingCandidates = ref([])
const candidateDocuments = ref({}) // Map of candidateId -> documents array
const onboardingStageId = ref(null)

const requiredDocTypes = ref([
  { value: 'id_proof', label: 'ID Proof' },
  { value: 'address_proof', label: 'Address Proof' },
  { value: 'education_certificate', label: 'Education Certificate' },
  { value: 'work_experience_certificate', label: 'Work Experience Certificate' }
])

const requiredDocsCount = computed(() => requiredDocTypes.value.length)

// Stats
const stats = computed(() => {
  const totalCandidates = onboardingCandidates.value.length
  let pendingDocs = 0
  let verifiedDocs = 0
  let readyToHire = 0

  onboardingCandidates.value.forEach(candidate => {
    const docs = candidateDocuments.value[candidate.candidate_id] || []
    docs.forEach(doc => {
      if (doc.verified) {
        verifiedDocs++
      } else {
        pendingDocs++
      }
    })

    if (canHire(candidate.candidate_id)) {
      readyToHire++
    }
  })

  return {
    totalCandidates,
    pendingDocs,
    verifiedDocs,
    readyToHire
  }
})

// Helper Functions
const getAuthToken = () => localStorage.getItem('access_token')

function getInitials(name) {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2)
}

function getCandidateDocuments(candidateId) {
  return candidateDocuments.value[candidateId] || []
}

function hasDocument(candidateId, docType) {
  const docs = getCandidateDocuments(candidateId)
  return docs.some(doc => doc.doc_type === docType)
}

function isDocVerified(candidateId, docType) {
  const docs = getCandidateDocuments(candidateId)
  const doc = docs.find(d => d.doc_type === docType)
  return doc && doc.verified
}

function getDocStatus(candidateId, docType) {
  const docs = getCandidateDocuments(candidateId)
  const doc = docs.find(d => d.doc_type === docType)
  if (!doc) return 'Not Uploaded'
  return doc.verified ? 'Verified' : 'Pending'
}

function getDocStatusClass(candidateId, docType) {
  const docs = getCandidateDocuments(candidateId)
  const doc = docs.find(d => d.doc_type === docType)
  if (!doc) return 'not-uploaded'
  return doc.verified ? 'verified' : 'pending'
}

function getDocIcon(candidateId, docType) {
  const docs = getCandidateDocuments(candidateId)
  const doc = docs.find(d => d.doc_type === docType)
  if (!doc) return 'fas fa-file-upload'
  return doc.verified ? 'fas fa-check-circle' : 'fas fa-clock'
}

function getVerifiedCount(candidateId) {
  const docs = getCandidateDocuments(candidateId)
  return docs.filter(doc => doc.verified).length
}

function calculateProgress(candidateId) {
  const verifiedCount = getVerifiedCount(candidateId)
  return Math.round((verifiedCount / requiredDocsCount.value) * 100)
}

function canHire(candidateId) {
  const docs = getCandidateDocuments(candidateId)
  return docs.length === requiredDocsCount.value && 
         docs.every(doc => doc.verified)
}

// API Functions
async function loadOnboardingStage() {
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/pipeline/stages', {
      headers: { Authorization: `Bearer ${token}` }
    })

    const onboardingStage = response.data.stages.find(
      stage => stage.name.toLowerCase() === 'onboarding'
    )

    if (onboardingStage) {
      onboardingStageId.value = onboardingStage.id
    }
  } catch (error) {
    console.error('Error loading onboarding stage:', error)
  }
}

async function loadOnboardingCandidates() {
  if (!onboardingStageId.value) return

  candidatesLoading.value = true
  try {
    const token = getAuthToken()
    const response = await axios.get(`/api/pipeline/candidates/${onboardingStageId.value}`, {
      headers: { Authorization: `Bearer ${token}` }
    })

    onboardingCandidates.value = response.data.candidates || []

    // Load documents for each candidate
    for (const candidate of onboardingCandidates.value) {
      await loadCandidateDocuments(candidate.candidate_id)
    }
  } catch (error) {
    console.error('Error loading onboarding candidates:', error)
  } finally {
    candidatesLoading.value = false
  }
}

async function loadCandidateDocuments(candidateId) {
  try {
    const token = getAuthToken()
    const response = await axios.get(`/api/onboarding/documents/${candidateId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })

    const allDocuments = response.data || []
    
    // Group documents by doc_type and keep only the latest one for each type
    const docsByType = {}
    allDocuments.forEach(doc => {
      const docType = doc.doc_type
      if (!docsByType[docType] || new Date(doc.uploaded_at) > new Date(docsByType[docType].uploaded_at)) {
        docsByType[docType] = doc
      }
    })
    
    // Convert back to array with only the latest documents
    candidateDocuments.value[candidateId] = Object.values(docsByType)
  } catch (error) {
    console.error('Error loading candidate documents:', error)
  }
}

async function viewDocument(candidateId, docType) {
  const docs = getCandidateDocuments(candidateId)
  const doc = docs.find(d => d.doc_type === docType)
  if (!doc) return

  try {
    const token = getAuthToken()
    
    // Use the file_path directly to download the document
    const response = await axios.get(`/api/onboarding/documents/${candidateId}/${doc.id}/download`, {
      headers: { Authorization: `Bearer ${token}` },
      responseType: 'blob'
    })

    // Create blob URL and open in new window
    const blob = new Blob([response.data], { type: response.headers['content-type'] })
    const url = window.URL.createObjectURL(blob)
    window.open(url, '_blank')
    
    // Clean up
    setTimeout(() => window.URL.revokeObjectURL(url), 100)
  } catch (error) {
    console.error('Error viewing document:', error)
    alert('Failed to view document. The file may not exist.')
  }
}

async function verifyDocument(candidateId, docType) {
  const docs = getCandidateDocuments(candidateId)
  const doc = docs.find(d => d.doc_type === docType)
  if (!doc) return

  try {
    const token = getAuthToken()
    const hrId = getCurrentUserId()

    await axios.put(`/api/onboarding/documents/${doc.id}/verify`, {
      verifier_id: hrId,
      verified: true
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })

    // Reload documents
    await loadCandidateDocuments(candidateId)
    alert('Document verified successfully!')
  } catch (error) {
    console.error('Error verifying document:', error)
    alert('Failed to verify document: ' + (error.response?.data?.error || error.message))
  }
}

async function unverifyDocument(candidateId, docType) {
  const docs = getCandidateDocuments(candidateId)
  const doc = docs.find(d => d.doc_type === docType)
  if (!doc) return

  try {
    const token = getAuthToken()
    const hrId = getCurrentUserId()

    await axios.put(`/api/onboarding/documents/${doc.id}/verify`, {
      verifier_id: hrId,
      verified: false
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })

    // Reload documents
    await loadCandidateDocuments(candidateId)
    alert('Document unverified successfully!')
  } catch (error) {
    console.error('Error unverifying document:', error)
    alert('Failed to unverify document')
  }
}

async function hireCandidate(candidate) {
  if (!canHire(candidate.candidate_id)) {
    alert('Please verify all documents before hiring this candidate.')
    return
  }

  if (!confirm(`Are you sure you want to hire ${candidate.name}?`)) {
    return
  }

  hiringCandidate.value = candidate.candidate_id

  try {
    const token = getAuthToken()
    const hrId = getCurrentUserId()

    // Move candidate to Hired stage
    await axios.put(`/api/pipeline/candidates/${candidate.candidate_id}/move`, {
      stage_id: 'hired', // You'll need to get the actual hired stage ID
      job_id: candidate.job_id,
      notes: 'All onboarding documents verified',
      moved_by_id: hrId
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })

    alert(`${candidate.name} has been successfully hired!`)
    
    // Refresh the list
    await refreshData()
  } catch (error) {
    console.error('Error hiring candidate:', error)
    alert('Failed to hire candidate: ' + (error.response?.data?.error || error.message))
  } finally {
    hiringCandidate.value = null
  }
}

function getCurrentUserId() {
  // Get current HR user ID from localStorage or state
  const userData = JSON.parse(localStorage.getItem('user') || '{}')
  return userData.id
}

async function refreshData() {
  loading.value = true
  try {
    await loadOnboardingStage()
    await loadOnboardingCandidates()
  } catch (error) {
    console.error('Error refreshing data:', error)
  } finally {
    loading.value = false
  }
}

// Load data on mount
onMounted(async () => {
  await refreshData()
})
</script>

<style scoped>
.hr-onboarding {
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

.btn-refresh {
  padding: 10px 20px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-refresh:hover:not(:disabled) {
  background: #f8f9fa;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  color: #667eea;
  opacity: 0.8;
}

.stat-card.pending .stat-icon {
  color: #ffc107;
}

.stat-card.verified .stat-icon {
  color: #28a745;
}

.stat-card.ready .stat-icon {
  color: #17a2b8;
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

/* Candidates Section */
.candidates-section h2 {
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

.candidates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.candidate-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.candidate-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.candidate-header {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ecf0f1;
}

.candidate-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 600;
  flex-shrink: 0;
}

.candidate-info h3 {
  margin: 0 0 4px 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.candidate-info p {
  margin: 0 0 8px 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.job-title {
  display: inline-block;
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.progress-section {
  margin-bottom: 20px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #ecf0f1;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.85rem;
  color: #7f8c8d;
}

.documents-list h4 {
  margin: 0 0 12px 0;
  color: #2c3e50;
  font-size: 1rem;
}

.document-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #ecf0f1;
}

.document-item:last-child {
  border-bottom: none;
}

.doc-name {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #2c3e50;
  font-size: 0.9rem;
}

.doc-name i {
  width: 20px;
}

.doc-name i.fa-check-circle {
  color: #28a745;
}

.doc-name i.fa-clock {
  color: #ffc107;
}

.doc-name i.fa-file-upload {
  color: #e74c3c;
}

.doc-actions-inline {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.not-uploaded {
  background: #fee;
  color: #e74c3c;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.verified {
  background: #d4edda;
  color: #155724;
}

.btn-icon {
  width: 32px;
  height: 32px;
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
  background: #e9ecef;
}

.btn-icon.verify {
  background: #d4edda;
  color: #28a745;
}

.btn-icon.verify:hover {
  background: #c3e6cb;
}

.btn-icon.unverify {
  background: #fee;
  color: #e74c3c;
}

.btn-icon.unverify:hover {
  background: #f8d7da;
}

.candidate-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
}

.btn-hire {
  width: 100%;
  padding: 12px 24px;
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-hire:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
}

.btn-hire:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

/* Responsive */
@media (max-width: 768px) {
  .candidates-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
