<template>
  <DashboardLayout>
    <div class="bda-expense-page">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <h1>
            <i class="fas fa-receipt"></i>
            My Expense Reports
          </h1>
          <p>Create, submit, and track your expense reports</p>
        </div>
        <button @click="openCreateDialog" class="btn-create-expense">
          <i class="fas fa-plus"></i>
          New Expense Report
        </button>
      </div>

      <!-- Tabs -->
      <div class="tabs-section">
        <button v-for="tab in tabs" :key="tab" @click="activeTab = tab" :class="{ active: activeTab === tab }"
          class="tab-button">
          <i :class="getTabIcon(tab)"></i>
          {{ formatTabName(tab) }}
          <span v-if="getTabCount(tab)" class="tab-count">{{ getTabCount(tab) }}</span>
        </button>
      </div>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-file-alt"></i>
          </div>
          <div class="stat-content">
            <h3>{{ stats.total }}</h3>
            <p>Total Reports</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="stat-content">
            <h3>{{ stats.pending }}</h3>
            <p>Pending Approval</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="stat-content">
            <h3>₹{{ stats.approvedAmount.toFixed(2) }}</h3>
            <p>Approved Amount</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-calculator"></i>
          </div>
          <div class="stat-content">
            <h3>₹{{ stats.totalAmount.toFixed(2) }}</h3>
            <p>Total Amount</p>
          </div>
        </div>
      </div>

      <!-- Expense Reports List -->
      <div class="reports-container">
        <div v-if="loading" class="loading">
          <i class="fas fa-spinner fa-spin"></i>
          Loading expense reports...
        </div>

        <div v-else-if="filteredReports.length === 0" class="no-data">
          <i class="fas fa-inbox"></i>
          <p>{{ activeTab === 'draft' ? 'No draft reports' : 'No ' + activeTab + ' reports' }}</p>
        </div>

        <div v-else class="reports-list">
          <div v-for="report in filteredReports" :key="report.id" class="report-card">
            <!-- Card Header -->
            <div class="card-header" @click="toggleReportExpanded(report.id)">
              <div class="header-info">
                <div class="status-badge" :class="report.status">
                  {{ formatStatus(report.status) }}
                </div>
                <div class="report-meta">
                  <h3>Report #{{ report.id.substring(0, 8) }}</h3>
                  <p class="date">{{ formatDate(report.generated_at) }}</p>
                </div>
              </div>
              <div class="header-amount">
                <span class="amount">₹{{ report.total.toFixed(2) }}</span>
                <i class="fas" :class="expandedReports.has(report.id) ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
              </div>
            </div>

            <!-- Card Content (Expandable) -->
            <div v-if="expandedReports.has(report.id)" class="card-content">
              <!-- Expense Items -->
              <div class="items-section">
                <h4>Expense Items</h4>
                <table class="items-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Category</th>
                      <th>Description</th>
                      <th>Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, index) in report.items" :key="index">
                      <td>{{ formatDate(item.expense_date) }}</td>
                      <td>
                        <span class="category-badge">{{ item.category }}</span>
                      </td>
                      <td>{{ item.description }}</td>
                      <td class="amount">₹{{ Number(item.amount).toFixed(2) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Report Summary -->
              <div class="summary-section">
                <div class="summary-item">
                  <span class="label">Report ID:</span>
                  <span class="value">{{ report.report_id }}</span>
                </div>
                <div class="summary-item">
                  <span class="label">Total Amount:</span>
                  <span class="value highlight">₹{{ report.total.toFixed(2) }}</span>
                </div>
                <div class="summary-item">
                  <span class="label">Items Count:</span>
                  <span class="value">{{ report.items.length }}</span>
                </div>
                <div v-if="report.status !== 'pending'" class="summary-item">
                  <span class="label">Approved By:</span>
                  <span class="value">{{ report.approved_by_name || 'N/A' }}</span>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="action-buttons">
                <button v-if="report.status === 'draft'" @click="submitExistingReport(report.id)" class="btn-submit">
                  <i class="fas fa-paper-plane"></i> Submit for Approval
                </button>
                <button v-if="report.status === 'draft'" @click="editExpenseReport(report.id)" class="btn-edit">
                  <i class="fas fa-edit"></i> Edit
                </button>
                <button v-if="report.status === 'draft'" @click="deleteExpenseReport(report.id)" class="btn-delete">
                  <i class="fas fa-trash"></i> Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Create/Edit Expense Dialog -->
      <div v-if="showCreateDialog" class="modal-overlay" @click.self="closeCreateDialog">
        <div class="modal-dialog large">
          <div class="modal-header">
            <h2>{{ editingReportId ? 'Edit Expense Report' : 'Create New Expense Report' }}</h2>
            <button @click="closeCreateDialog" class="btn-close">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <!-- Add Items Section -->
            <div class="form-section">
              <h3>Add Expense Items</h3>

              <div class="item-form">
                <div class="form-row">
                  <div class="form-group">
                    <label for="expense-date">Expense Date:</label>
                    <input v-model="newItem.expense_date" type="date" id="expense-date" class="form-input" />
                  </div>

                  <div class="form-group">
                    <label for="category">Category:</label>
                    <select v-model="newItem.category" id="category" class="form-input">
                      <option value="">Select Category</option>
                      <option value="Travel">Travel</option>
                      <option value="Food">Food</option>
                      <option value="Supplies">Supplies</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>

                  <div class="form-group">
                    <label for="amount">Amount (₹):</label>
                    <input v-model.number="newItem.amount" type="number" id="amount" class="form-input"
                      placeholder="0.00" min="0" step="0.01" />
                  </div>
                </div>

                <div class="form-group full-width">
                  <label for="description">Description:</label>
                  <textarea v-model="newItem.description" id="description" class="form-textarea"
                    placeholder="Enter expense description..." rows="3"></textarea>
                </div>

                <div class="form-group full-width">
                  <label for="receipt">Receipt (PDF/Image):</label>
                  <div class="file-input-wrapper">
                    <input type="file" id="receipt" class="file-input" accept=".pdf,.png,.jpg,.jpeg,.gif"
                      @change="handleReceiptUpload" />
                    <label for="receipt" class="file-input-label">
                      <i class="fas fa-cloud-upload-alt"></i>
                      {{ newItem.receipt_file ? newItem.receipt_file.name : 'Click to upload receipt' }}
                    </label>
                  </div>
                  <span class="help-text">Max 5MB. Allowed: PDF, PNG, JPG, JPEG, GIF</span>
                </div>

                <button @click="addExpenseItem" class="btn-add-item">
                  <i class="fas fa-plus"></i> Add Item
                </button>
              </div>

              <!-- Items List -->
              <div v-if="formItems.length > 0" class="added-items">
                <h4>Added Items ({{ formItems.length }})</h4>
                <div v-for="(item, index) in formItems" :key="index" class="item-card">
                  <div class="item-header">
                    <div class="item-title">
                      <span class="category">{{ item.category }}</span>
                      <span class="description">{{ item.description }}</span>
                    </div>
                    <div class="item-amount">
                      ₹{{ (Number(item.amount)).toFixed(2) }}
                      <button @click="removeExpenseItem(index)" class="btn-remove">
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </div>
                  <div class="item-details">
                    <span>{{ formatDate(item.expense_date) }}</span>
                    <span v-if="item.receipt_url || item.receipt_file" class="has-receipt">
                      <i class="fas fa-file"></i> Receipt attached
                    </span>
                  </div>
                </div>

                <!-- Total -->
                <div class="total-section">
                  <span>Total Amount:</span>
                  <span class="total-amount">₹{{ calculateTotalAmount().toFixed(2) }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button @click="closeCreateDialog" class="btn-secondary">
              Cancel
            </button>
            <button @click="saveAsDraft" class="btn-draft" :disabled="formItems.length === 0 || savingReport">
              <i v-if="savingReport" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-save"></i>
              {{ savingReport ? 'Saving...' : 'Save as Draft' }}
            </button>
            <button @click="submitExpense" class="btn-primary" :disabled="formItems.length === 0 || savingReport">
              <i v-if="savingReport" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-check"></i>
              {{ savingReport ? 'Submitting...' : 'Submit' }}
            </button>
          </div>
        </div>
      </div>

      <!-- AI Verification Dialog -->
      <div v-if="showAIVerificationDialog" class="modal-overlay" @click.self="closeAIVerificationDialog">
        <div class="modal-dialog">
          <div class="modal-header">
            <h2>AI Verification Results</h2>
            <button @click="closeAIVerificationDialog" class="btn-close">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <div v-if="aiVerificationLoading" class="loading-center">
              <i class="fas fa-spinner fa-spin"></i>
              <p>Verifying expense items...</p>
            </div>
            <div v-else>
              <div class="verification-summary">
                <h3>Overall Verification Status: {{ aiVerificationResults?.verification_status }}</h3>
                <p>Confidence Score: {{ aiVerificationResults?.overall_confidence }}%</p>
              </div>

              <div class="verification-results">
                <div v-for="(result, index) in aiVerificationResults?.results" :key="index" class="result-item">
                  <div class="result-header">
                    <span class="item-name">{{ result.item }}</span>
                    <span :class="['confidence', result.confidence_score > 0.9 ? 'high' : 'low']">
                      {{ (result.confidence_score * 100).toFixed(0) }}% Confidence
                    </span>
                  </div>
                  <div class="result-details">
                    <p>Claimed: ₹{{ result.claimed_amount }}</p>
                    <p>Verified: ₹{{ result.verified_amount }}</p>
                    <p v-if="result.flags.length > 0" class="flags">
                      <i class="fas fa-exclamation-triangle"></i> {{ result.flags.join(', ') }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="closeAIVerificationDialog" class="btn-primary">
              Close
            </button>
          </div>
        </div>
      </div>

      <!-- Policy Check Dialog -->
      <div v-if="showPolicyCheckDialog" class="modal-overlay" @click.self="closePolicyCheckDialog">
        <div class="modal-dialog">
          <div class="modal-header">
            <h2>Policy Compliance Check</h2>
            <button @click="closePolicyCheckDialog" class="btn-close">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <div v-if="policyCheckLoading" class="loading-center">
              <i class="fas fa-spinner fa-spin"></i>
              <p>Checking policy compliance...</p>
            </div>
            <div v-else>
              <div class="compliance-status">
                <h3>Compliance Status:
                  <span :class="policyCheckResults?.is_compliant ? 'compliant' : 'non-compliant'">
                    {{ policyCheckResults?.is_compliant ? 'COMPLIANT' : 'VIOLATIONS FOUND' }}
                  </span>
                </h3>
              </div>

              <div v-if="policyCheckResults?.violations.length > 0" class="violations-section">
                <h4>
                  <i class="fas fa-exclamation-circle"></i>
                  Violations ({{ policyCheckResults?.violations.length }})
                </h4>
                <div v-for="(violation, index) in policyCheckResults?.violations" :key="index" class="violation-item">
                  <p><strong>{{ violation.type }}:</strong> {{ violation.item || violation.category }}</p>
                  <p>Limit: ₹{{ violation.limit }} | Actual: ₹{{ violation.actual }}</p>
                </div>
              </div>

              <div v-if="policyCheckResults?.warnings.length > 0" class="warnings-section">
                <h4>
                  <i class="fas fa-exclamation-triangle"></i>
                  Warnings ({{ policyCheckResults?.warnings.length }})
                </h4>
                <div v-for="(warning, index) in policyCheckResults?.warnings" :key="index" class="warning-item">
                  <p>{{ warning.message }}</p>
                </div>
              </div>

              <div class="category-breakdown">
                <h4>Category Breakdown</h4>
                <div v-for="(total, category) in policyCheckResults?.category_totals" :key="category"
                  class="breakdown-item">
                  <span>{{ category }}:</span>
                  <span>₹{{ total.toFixed(2) }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="closePolicyCheckDialog" class="btn-primary">
              Close
            </button>
          </div>
        </div>
      </div>

      <!-- Toast Notifications -->
      <div v-if="successMessage" class="toast success">
        <i class="fas fa-check-circle"></i>
        {{ successMessage }}
      </div>
      <div v-if="errorMessage" class="toast error">
        <i class="fas fa-exclamation-circle"></i>
        {{ errorMessage }}
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
const activeTab = ref('pending')
const expenseReports = ref([])
const loading = ref(false)
const expandedReports = ref(new Set())
const tabs = ['pending', 'draft', 'approved', 'rejected']

// Create/Edit Dialog
const showCreateDialog = ref(false)
const editingReportId = ref(null)
const formItems = ref([])
const savingReport = ref(false)

const newItem = ref({
  expense_date: new Date().toISOString().split('T')[0],
  category: '',
  amount: 0,
  description: '',
  receipt_file: null,
  receipt_url: null
})

// Verification Dialogs
const showAIVerificationDialog = ref(false)
const showPolicyCheckDialog = ref(false)
const aiVerificationLoading = ref(false)
const policyCheckLoading = ref(false)
const aiVerificationResults = ref(null)
const policyCheckResults = ref(null)

// Messages
const successMessage = ref('')
const errorMessage = ref('')

// Computed
const filteredReports = computed(() => {
  if (activeTab.value === 'draft') {
    return expenseReports.value.filter(r => r.status === 'draft')
  }
  return expenseReports.value.filter(r => r.status === activeTab.value)
})

const stats = computed(() => {
  const stats = {
    total: expenseReports.value.length,
    pending: expenseReports.value.filter(r => r.status === 'pending').length,
    approved: expenseReports.value.filter(r => r.status === 'approved').length,
    totalAmount: 0,
    approvedAmount: 0
  }

  expenseReports.value.forEach(report => {
    stats.totalAmount += report.total
    if (report.status === 'approved') {
      stats.approvedAmount += report.total
    }
  })

  return stats
})

// Methods
const getAuthToken = () => localStorage.getItem('access_token')

const getCurrentUserId = () => {
  const user = JSON.parse(localStorage.getItem('user'))
  return user?.id
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

function formatStatus(status) {
  const statusMap = {
    pending: 'Pending',
    draft: 'Draft',
    approved: 'Approved',
    rejected: 'Rejected'
  }
  return statusMap[status] || status
}

function formatTabName(tab) {
  const names = {
    pending: 'Pending',
    draft: 'Drafts',
    approved: 'Approved',
    rejected: 'Rejected'
  }
  return names[tab] || tab
}

function getTabIcon(tab) {
  const icons = {
    draft: 'fas fa-file-alt',
    pending: 'fas fa-clock',
    approved: 'fas fa-check-circle',
    rejected: 'fas fa-times-circle'
  }
  return icons[tab] || 'fas fa-file'
}

function getTabCount(tab) {
  if (tab === 'draft') {
    return expenseReports.value.filter(r => r.status === 'draft').length
  }
  return expenseReports.value.filter(r => r.status === tab).length
}

function toggleReportExpanded(reportId) {
  if (expandedReports.value.has(reportId)) {
    expandedReports.value.delete(reportId)
  } else {
    expandedReports.value.add(reportId)
  }
}

function openCreateDialog() {
  showCreateDialog.value = true
  formItems.value = []
  resetNewItem()
}

function closeCreateDialog() {
  showCreateDialog.value = false
  editingReportId.value = null
  formItems.value = []
  resetNewItem()
}

function resetNewItem() {
  newItem.value = {
    expense_date: new Date().toISOString().split('T')[0],
    category: '',
    amount: 0,
    description: '',
    receipt_file: null,
    receipt_url: null
  }
}

function handleReceiptUpload(event) {
  const file = event.target.files[0]
  if (file) {
    if (file.size > 5 * 1024 * 1024) {
      showToast('File size exceeds 5MB limit', 'error')
      return
    }
    newItem.value.receipt_file = file
  }
}

function addExpenseItem() {
  if (!newItem.value.expense_date || !newItem.value.category || !newItem.value.amount || !newItem.value.description) {
    showToast('Please fill all required fields', 'error')
    return
  }

  formItems.value.push({
    expense_date: newItem.value.expense_date,
    category: newItem.value.category,
    amount: newItem.value.amount,
    description: newItem.value.description,
    receipt_file: newItem.value.receipt_file,
    receipt_url: newItem.value.receipt_url
  })

  resetNewItem()
}

function removeExpenseItem(index) {
  formItems.value.splice(index, 1)
}

function calculateTotalAmount() {
  return formItems.value.reduce((sum, item) => sum + item.amount, 0)
}

async function loadExpenseReports() {
  loading.value = true
  try {
    const response = await axios.get('/api/expenses/', {
      params: { user_id: getCurrentUserId() },
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data && response.data.data) {
      expenseReports.value = response.data.data
    }
  } catch (error) {
    console.error('Failed to load expense reports:', error)
    showToast('Failed to load expense reports', 'error')
  } finally {
    loading.value = false
  }
}

async function saveAsDraft() {
  await submitExpenseReport(null, 'draft')
}

async function submitExpense() {
  await submitExpenseReport(null, 'pending')
}

async function submitExpenseReport(reportId, status = 'pending') {
  if (formItems.value.length === 0) {
    showToast('Please add at least one expense item', 'error')
    return
  }

  savingReport.value = true
  try {
    // If reportId is provided, update existing report via PUT
    if (reportId) {
      const payload = {
        items: formItems.value.map(i => ({
          expense_date: i.expense_date,
          category: i.category,
          amount: i.amount,
          description: i.description,
          receipt_url: i.receipt_url || null
        })),
        total: calculateTotalAmount(),
        status: status
      }

      const response = await axios.put(`/api/expenses/${reportId}`, payload, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      })

      if (response.data.success) {
        showToast('Expense report updated successfully!', 'success')
        closeCreateDialog()
        await loadExpenseReports()
      }

    } else {
      // New report submission/create draft - send items as JSON and optionally first receipt file
      const formData = new FormData()
      formData.append('status', status)
      formData.append('items', JSON.stringify(formItems.value.map(i => ({
        expense_date: i.expense_date,
        category: i.category,
        amount: i.amount,
        description: i.description,
        receipt_url: i.receipt_url || null
      }))))

      // Attach first receipt file (backend will handle single-file case)
      const firstWithFile = formItems.value.find(i => i.receipt_file)
      if (firstWithFile && firstWithFile.receipt_file) {
        formData.append('receipt', firstWithFile.receipt_file)
      }

      const response = await axios.post('/api/expenses/submit', formData, {
        headers: {
          Authorization: `Bearer ${getAuthToken()}`,
          'Content-Type': 'multipart/form-data'
        }
      })

      if (response.data && response.data.success) {
        showToast(status === 'draft' ? 'Draft saved' : 'Expense report submitted!', 'success')
        closeCreateDialog()
        await loadExpenseReports()
      }
    }
  } catch (error) {
    console.error('Failed to submit expense report:', error)
    showToast(error.response?.data?.error || 'Failed to submit expense report', 'error')
  } finally {
    savingReport.value = false
  }
}

// Submit an existing draft by setting its status to pending
async function submitExistingReport(reportId) {
  try {
    savingReport.value = true
    const response = await axios.put(`/api/expenses/${reportId}`, { status: 'pending' }, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data && response.data.success) {
      showToast('Expense submitted for approval', 'success')
      await loadExpenseReports()
    }
  } catch (error) {
    console.error('Failed to submit existing report:', error)
    showToast(error.response?.data?.error || 'Failed to submit report', 'error')
  } finally {
    savingReport.value = false
  }
}

async function editExpenseReport(reportId) {
  const report = expenseReports.value.find(r => r.id === reportId)
  if (!report) return

  editingReportId.value = reportId
  formItems.value = report.items.map(item => ({
    ...item,
    receipt_file: null
  }))
  showCreateDialog.value = true
}

async function deleteExpenseReport(reportId) {
  if (!confirm('Are you sure you want to delete this expense report?')) return

  try {
    const response = await axios.delete(`/api/expenses/${reportId}`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data.success) {
      showToast('Expense report deleted successfully!', 'success')
      await loadExpenseReports()
    }
  } catch (error) {
    console.error('Failed to delete expense report:', error)
    showToast(error.response?.data?.error || 'Failed to delete expense report', 'error')
  }
}

function showToast(message, type = 'success') {
  if (type === 'success') {
    successMessage.value = message
    setTimeout(() => { successMessage.value = '' }, 3000)
  } else {
    errorMessage.value = message
    setTimeout(() => { errorMessage.value = '' }, 3000)
  }
}

onMounted(() => {
  loadExpenseReports()
})
</script>

<style scoped>
.bda-expense-page {
  padding: 30px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  gap: 20px;
}

.header-content h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-content p {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin: 0;
}

.btn-create-expense {
  padding: 12px 24px;
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-create-expense:hover {
  background: #229954;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
}

/* Tabs */
.tabs-section {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  background: white;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tab-button {
  padding: 10px 20px;
  border: 2px solid transparent;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  color: #7f8c8d;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.tab-button.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.tab-button:hover:not(.active) {
  background: #ecf0f1;
}

.tab-count {
  display: inline-block;
  background: rgba(255, 255, 255, 0.3);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 700;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 15px;
  align-items: center;
  border-left: 4px solid #3498db;
}

.stat-icon {
  font-size: 2rem;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 8px;
  color: #3498db;
}

.stat-content h3 {
  margin: 0;
  font-size: 1.6rem;
  color: #2c3e50;
}

.stat-content p {
  margin: 5px 0 0 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

/* Reports Container */
.reports-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-height: 300px;
  padding: 20px;
}

.loading,
.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: #7f8c8d;
  font-size: 1.1rem;
}

.loading i {
  font-size: 2rem;
  margin-bottom: 10px;
}

.no-data i {
  font-size: 3rem;
  margin-bottom: 10px;
  opacity: 0.5;
}

/* Reports List */
.reports-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.report-card {
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.report-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  cursor: pointer;
  user-select: none;
}

.card-header:hover {
  background: #ecf0f1;
}

.header-info {
  display: flex;
  gap: 15px;
  align-items: center;
  flex: 1;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.8rem;
  text-transform: uppercase;
  background: #ecf0f1;
  color: #7f8c8d;
}

.status-badge.pending {
  background: #fff3cd;
  color: #f39c12;
}

.status-badge.approved {
  background: #d4edda;
  color: #27ae60;
}

.status-badge.rejected {
  background: #f8d7da;
  color: #e74c3c;
}

.report-meta h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.report-meta .date {
  margin: 5px 0 0 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.header-amount {
  display: flex;
  align-items: center;
  gap: 15px;
  text-align: right;
}

.header-amount .amount {
  font-size: 1.3rem;
  font-weight: 700;
  color: #2c3e50;
}

/* Card Content */
.card-content {
  padding: 20px;
  border-top: 1px solid #ecf0f1;
  background: white;
}

.items-section {
  margin-bottom: 20px;
}

.items-section h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.items-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.items-table th {
  background: #f5f7fa;
  padding: 10px;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #ecf0f1;
}

.items-table td {
  padding: 12px 10px;
  border-bottom: 1px solid #ecf0f1;
}

.items-table tr:hover {
  background: #f9f9f9;
}

.category-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
  background: #ecf0f1;
  color: #2c3e50;
}

.items-table .amount {
  font-weight: 600;
  color: #2c3e50;
}

.receipt-link {
  color: #3498db;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.receipt-link:hover {
  color: #2980b9;
}

.no-receipt {
  color: #bdc3c7;
}

/* Summary Section */
.summary-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 15px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
}

.summary-item .label {
  font-weight: 600;
  color: #2c3e50;
}

.summary-item .value {
  color: #7f8c8d;
}

.summary-item .highlight {
  color: #27ae60;
  font-weight: 600;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  padding-top: 15px;
  border-top: 1px solid #ecf0f1;
}

.action-buttons button {
  flex: 1;
  min-width: 120px;
  padding: 10px 15px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-submit {
  background: #27ae60;
  color: white;
}

.btn-submit:hover {
  background: #229954;
}

.btn-edit {
  background: #3498db;
  color: white;
}

.btn-edit:hover {
  background: #2980b9;
}

.btn-delete {
  background: #e74c3c;
  color: white;
}

.btn-delete:hover {
  background: #c0392b;
}

.btn-view {
  background: #95a5a6;
  color: white;
}

.btn-view:hover {
  background: #7f8c8d;
}

/* Modal */
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

.modal-dialog {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-dialog.large {
  max-width: 700px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #ecf0f1;
  position: sticky;
  top: 0;
}

.modal-header h2 {
  margin: 0;
  color: #2c3e50;
}

.btn-close {
  background: none;
  border: none;
  cursor: pointer;
  color: #7f8c8d;
  font-size: 1.5rem;
}

.btn-close:hover {
  color: #2c3e50;
}

.modal-body {
  padding: 20px;
}

.form-section {
  margin-bottom: 20px;
}

.form-section h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.item-form {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

.form-input,
.form-textarea {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  font-family: inherit;
}

#expense-date {
  padding-right: 30px;
  max-width: -moz-available;
  max-width: -webkit-fill-available;
}

#amount {
  max-width: -moz-available;
  max-width: -webkit-fill-available;
}

#description {
  max-width: -moz-available;
  max-width: -webkit-fill-available;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-textarea {
  resize: vertical;
}

.help-text {
  font-size: 0.8rem;
  color: #7f8c8d;
  margin-top: 5px;
}

.file-input-wrapper {
  position: relative;
}

.file-input {
  display: none;
}

.file-input-label {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  border: 2px dashed #3498db;
  border-radius: 8px;
  cursor: pointer;
  background: white;
  transition: all 0.3s ease;
  font-weight: 600;
  color: #3498db;
}

.file-input-label:hover {
  background: #ecf0f1;
}

.btn-add-item {
  width: 100%;
  padding: 10px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-add-item:hover {
  background: #2980b9;
}

.added-items {
  background: white;
  padding: 15px;
  border-radius: 8px;
}

.added-items h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.item-card {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 10px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.item-title {
  display: flex;
  gap: 10px;
  align-items: center;
}

.category {
  display: inline-block;
  padding: 2px 8px;
  background: #ecf0f1;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #2c3e50;
}

.description {
  color: #2c3e50;
  font-weight: 500;
}

.item-amount {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: #2c3e50;
}

.btn-remove {
  background: none;
  border: none;
  cursor: pointer;
  color: #e74c3c;
  font-size: 1rem;
}

.btn-remove:hover {
  color: #c0392b;
}

.item-details {
  display: flex;
  gap: 10px;
  font-size: 0.85rem;
  color: #7f8c8d;
}

.has-receipt {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #27ae60;
}

.total-section {
  display: flex;
  justify-content: space-between;
  padding: 15px;
  background: #ecf0f1;
  border-radius: 6px;
  margin-top: 15px;
  font-weight: 600;
  color: #2c3e50;
}

.total-amount {
  font-size: 1.3rem;
  color: #27ae60;
}

.modal-footer {
  display: flex;
  gap: 10px;
  padding: 20px;
  background: #f8f9fa;
  border-top: 1px solid #ecf0f1;
  position: sticky;
  bottom: 0;
}

.modal-footer button {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

.btn-draft {
  background: #f39c12;
  color: white;
}

.btn-draft:hover:not(:disabled) {
  background: #e67e22;
}

.btn-primary {
  background: #27ae60;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #229954;
}

.btn-primary:disabled,
.btn-draft:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c0392b;
}

/* Verification/Policy Dialogs */
.loading-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  gap: 15px;
  color: #7f8c8d;
}

.loading-center i {
  font-size: 2rem;
}

.verification-summary,
.compliance-status {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.verification-results,
.violations-section,
.warnings-section,
.category-breakdown {
  margin-bottom: 20px;
}

.verification-results h4,
.violations-section h4,
.warnings-section h4,
.category-breakdown h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.result-item,
.violation-item,
.warning-item {
  background: #f9f9f9;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 10px;
  border-left: 3px solid #3498db;
}

.violation-item {
  border-left-color: #e74c3c;
}

.warning-item {
  border-left-color: #f39c12;
}

.result-header,
.violation-item p,
.warning-item p {
  margin: 0;
  color: #2c3e50;
}

.confidence {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.confidence.high {
  background: #d4edda;
  color: #27ae60;
}

.confidence.low {
  background: #f8d7da;
  color: #e74c3c;
}

.result-details {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #ecf0f1;
  font-size: 0.9rem;
  color: #7f8c8d;
}

.result-details p {
  margin: 4px 0;
}

.flags {
  color: #e74c3c !important;
  font-weight: 600;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 6px;
  margin-bottom: 8px;
}

/* Toast Notifications */
.toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 15px 20px;
  border-radius: 8px;
  color: white;
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 2000;
  animation: slideIn 0.3s ease;
}

.toast.success {
  background: #27ae60;
}

.toast.error {
  background: #e74c3c;
}

@keyframes slideIn {
  from {
    transform: translateX(400px);
    opacity: 0;
  }

  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
  }

  .btn-create-expense {
    width: 100%;
  }

  .tabs-section {
    flex-wrap: wrap;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .summary-section {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons button {
    min-width: auto;
  }

  .modal-dialog {
    width: 95%;
  }

  .items-table {
    font-size: 0.85rem;
  }

  .items-table th,
  .items-table td {
    padding: 8px 5px;
  }
}
</style>
