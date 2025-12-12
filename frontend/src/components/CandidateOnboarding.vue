<template>
  <DashboardLayout>
    <div class="candidate-onboarding">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <h1>Onboarding</h1>
          <p>Complete your onboarding process by uploading required documents</p>
        </div>
      </div>

      <!-- Progress Tracker -->
      <div class="progress-section">
        <h3>Onboarding Progress</h3>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
        </div>
        <span class="progress-text">{{ progressPercentage }}% Complete ({{ verifiedCount }}/{{ requiredDocs.length }} documents verified)</span>
      </div>

      <!-- Required Documents Section -->
      <div class="documents-section">
        <h2>Required Documents</h2>
        <p class="section-description">Please upload the following documents to complete your onboarding</p>

        <div class="documents-grid">
          <div 
            v-for="docType in requiredDocs" 
            :key="docType.value"
            class="document-card"
          >
            <div class="doc-header">
              <div class="doc-icon" :class="getDocStatusClass(docType.value)">
                <i :class="getDocIcon(docType.value)"></i>
              </div>
              <div class="doc-info">
                <h4>{{ docType.label }}</h4>
                <p>{{ docType.description }}</p>
              </div>
            </div>

            <div class="doc-status">
              <span 
                class="status-badge" 
                :class="getDocStatusClass(docType.value)"
              >
                {{ getDocStatus(docType.value) }}
              </span>
            </div>

            <div class="doc-actions">
              <input 
                :id="'fileInput_' + docType.value"
                type="file" 
                :accept="'.pdf,.jpg,.jpeg,.png,.docx'"
                @change="handleFileSelect($event, docType.value)"
                style="display: none"
              />
              
              <button 
                v-if="!isDocUploaded(docType.value)"
                class="btn-upload"
                @click="triggerFileUpload(docType.value)"
              >
                <i class="fas fa-upload"></i> Upload
              </button>

              <button 
                v-else-if="isDocUploaded(docType.value) && !isDocVerified(docType.value)"
                class="btn-reupload"
                @click="triggerFileUpload(docType.value)"
              >
                <i class="fas fa-sync-alt"></i> Re-upload
              </button>

              <button 
                v-if="isDocUploaded(docType.value)"
                class="btn-view"
                @click="viewDocument(docType.value)"
              >
                <i class="fas fa-eye"></i> View
              </button>
            </div>

            <div v-if="getUploadedDoc(docType.value)" class="doc-details">
              <small>Uploaded: {{ formatDate(getUploadedDoc(docType.value).uploaded_at) }}</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Upload Progress -->
      <div v-if="uploadingDoc" class="upload-progress">
        <div class="upload-card">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Uploading {{ uploadingDoc }}...</p>
        </div>
      </div>

      <!-- Additional Information -->
      <div class="info-section">
        <div class="info-card">
          <i class="fas fa-info-circle"></i>
          <div>
            <h4>Important Notes:</h4>
            <ul>
              <li>All documents must be in PDF, JPG, PNG, or DOCX format</li>
              <li>Maximum file size: 10MB per document</li>
              <li>Documents will be verified by HR within 2-3 business days</li>
              <li>You can re-upload documents if they are rejected</li>
            </ul>
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

// State
const candidateId = ref('')
const uploadedDocuments = ref([])
const uploadingDoc = ref(null)
const loading = ref(false)

// Required document types from backend config
const requiredDocs = ref([
  {
    value: 'id_proof',
    label: 'ID Proof',
    description: 'Aadhar Card, Passport, or Driving License'
  },
  {
    value: 'address_proof',
    label: 'Address Proof',
    description: 'Utility Bill, Rent Agreement, or Bank Statement'
  },
  {
    value: 'education_certificate',
    label: 'Education Certificate',
    description: 'Degree, Diploma, or Mark Sheets'
  },
  {
    value: 'work_experience_certificate',
    label: 'Work Experience Certificate',
    description: 'Experience letters from previous employers (if applicable)'
  }
])

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

function getUploadedDoc(docType) {
  return uploadedDocuments.value.find(doc => doc.doc_type === docType)
}

function isDocUploaded(docType) {
  return uploadedDocuments.value.some(doc => doc.doc_type === docType)
}

function isDocVerified(docType) {
  const doc = getUploadedDoc(docType)
  return doc && doc.verified
}

function getDocStatus(docType) {
  const doc = getUploadedDoc(docType)
  if (!doc) return 'Required'
  if (doc.verified) return 'Verified'
  return 'Pending Verification'
}

function getDocStatusClass(docType) {
  const doc = getUploadedDoc(docType)
  if (!doc) return 'required'
  if (doc.verified) return 'verified'
  return 'pending'
}

function getDocIcon(docType) {
  const doc = getUploadedDoc(docType)
  if (!doc) return 'fas fa-file-upload'
  if (doc.verified) return 'fas fa-check-circle'
  return 'fas fa-clock'
}

// Computed
const verifiedCount = computed(() => {
  return uploadedDocuments.value.filter(doc => doc.verified).length
})

const progressPercentage = computed(() => {
  return Math.round((verifiedCount.value / requiredDocs.value.length) * 100)
})

// File Upload Functions
function triggerFileUpload(docType) {
  const fileInput = document.getElementById(`fileInput_${docType}`)
  if (fileInput) {
    fileInput.click()
  }
}

async function handleFileSelect(event, docType) {
  const file = event.target.files[0]
  if (!file) return

  // Validate file size (10MB)
  if (file.size > 10 * 1024 * 1024) {
    alert('File size exceeds 10MB limit')
    return
  }

  // Validate file type
  const allowedTypes = ['.pdf', '.jpg', '.jpeg', '.png', '.docx']
  const fileExt = '.' + file.name.split('.').pop().toLowerCase()
  if (!allowedTypes.includes(fileExt)) {
    alert('Invalid file type. Please upload PDF, JPG, PNG, or DOCX files only.')
    return
  }

  await uploadDocument(file, docType)
}

async function uploadDocument(file, docType) {
  uploadingDoc.value = requiredDocs.value.find(d => d.value === docType)?.label
  
  try {
    const token = getAuthToken()
    const formData = new FormData()
    formData.append('file', file)
    formData.append('employee_id', candidateId.value)
    formData.append('doc_type', docType)

    const response = await axios.post('/api/onboarding/documents/upload', formData, {
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    })

    alert('Document uploaded successfully! Waiting for HR verification.')
    await loadDocuments()
  } catch (error) {
    console.error('Error uploading document:', error)
    alert('Failed to upload document: ' + (error.response?.data?.error || error.message))
  } finally {
    uploadingDoc.value = null
  }
}

async function viewDocument(docType) {
  const doc = getUploadedDoc(docType)
  if (!doc) return

  try {
    const token = getAuthToken()
    const response = await axios.get(`/api/onboarding/documents/${candidateId.value}/${doc.id}/download`, {
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

// API Functions
async function loadCandidateData() {
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/users/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    candidateId.value = response.data.id
  } catch (error) {
    console.error('Error loading candidate data:', error)
  }
}

async function loadDocuments() {
  loading.value = true
  try {
    const token = getAuthToken()
    const response = await axios.get(`/api/onboarding/documents/${candidateId.value}`, {
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
    uploadedDocuments.value = Object.values(docsByType)
  } catch (error) {
    console.error('Error loading documents:', error)
  } finally {
    loading.value = false
  }
}

// Load data on mount
onMounted(async () => {
  await loadCandidateData()
  await loadDocuments()
})
</script>

<style scoped>
.candidate-onboarding {
  padding: 20px;
  max-width: 1200px;
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
  font-size: 1rem;
}

/* Progress Section */
.progress-section {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.progress-section h3 {
  margin: 0 0 16px 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.progress-bar {
  width: 100%;
  height: 24px;
  background-color: #ecf0f1;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.progress-text {
  display: block;
  color: #7f8c8d;
  font-size: 0.9rem;
  font-weight: 500;
}

/* Documents Section */
.documents-section {
  margin-bottom: 30px;
}

.documents-section h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 8px;
}

.section-description {
  color: #7f8c8d;
  margin-bottom: 24px;
}

.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.document-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.document-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.doc-header {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.doc-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.doc-icon.required {
  background: #fee;
  color: #e74c3c;
}

.doc-icon.pending {
  background: #fff3cd;
  color: #ffc107;
}

.doc-icon.verified {
  background: #d4edda;
  color: #28a745;
}

.doc-info h4 {
  margin: 0 0 4px 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.doc-info p {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.85rem;
}

.doc-status {
  margin-bottom: 16px;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.status-badge.required {
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

.doc-actions {
  display: flex;
  gap: 8px;
}

.btn-upload,
.btn-reupload,
.btn-view {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.btn-upload {
  background: #667eea;
  color: white;
}

.btn-upload:hover {
  background: #5568d3;
}

.btn-reupload {
  background: #ffc107;
  color: #333;
}

.btn-reupload:hover {
  background: #e0a800;
}

.btn-view {
  background: #17a2b8;
  color: white;
}

.btn-view:hover {
  background: #138496;
}

.doc-details {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ecf0f1;
}

.doc-details small {
  color: #7f8c8d;
  font-size: 0.8rem;
}

/* Upload Progress */
.upload-progress {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}

.upload-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 12px;
}

.upload-card i {
  font-size: 1.5rem;
  color: #667eea;
}

.upload-card p {
  margin: 0;
  color: #2c3e50;
  font-weight: 500;
}

/* Info Section */
.info-section {
  margin-top: 30px;
}

.info-card {
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
  padding: 20px;
  border-radius: 8px;
  display: flex;
  gap: 16px;
}

.info-card i {
  font-size: 2rem;
  color: #2196f3;
  flex-shrink: 0;
}

.info-card h4 {
  margin: 0 0 12px 0;
  color: #1976d2;
}

.info-card ul {
  margin: 0;
  padding-left: 20px;
  color: #1565c0;
}

.info-card li {
  margin-bottom: 8px;
}

/* Responsive */
@media (max-width: 768px) {
  .documents-grid {
    grid-template-columns: 1fr;
  }

  .doc-actions {
    flex-direction: column;
  }
}
</style>
