<template>
  <DashboardLayout>
    <div class="expense-reports-page">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <h1>
            <i class="fas fa-file-invoice-dollar"></i>
            Expense Reports Management
          </h1>
          <p>Review and approve/reject expense reports submitted by employees</p>
        </div>
      </div>

      <!-- Filters & Actions -->
      <div class="filters-section">
        <div class="filter-group">
          <label for="status-filter">Status:</label>
          <select v-model="selectedStatus" id="status-filter" class="filter-select">
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>

        <div class="filter-group">
          <label for="category-filter">Category:</label>
          <select v-model="selectedCategory" id="category-filter" class="filter-select">
            <option value="">All Categories</option>
            <option value="Travel">Travel</option>
            <option value="Food">Food</option>
            <option value="Supplies">Supplies</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <div class="filter-group">
          <label for="date-from">From Date:</label>
          <input v-model="dateFrom" type="date" id="date-from" class="filter-input">
        </div>

        <div class="filter-group">
          <label for="date-to">To Date:</label>
          <input v-model="dateTo" type="date" id="date-to" class="filter-input">
        </div>

        <button @click="applyFilters" class="btn-apply">
          <i class="fas fa-filter"></i> Apply Filters
        </button>
        <button @click="clearFilters" class="btn-clear">
          <i class="fas fa-redo"></i> Clear
        </button>
      </div>

      <!-- Summary Stats -->
      <div class="stats-grid">
        <div class="stat-card pending">
          <div class="stat-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="stat-content">
            <h3>{{ summaryStats.pending }}</h3>
            <p>Pending Approval</p>
          </div>
        </div>

        <div class="stat-card approved">
          <div class="stat-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="stat-content">
            <h3>{{ summaryStats.approved }}</h3>
            <p>Approved</p>
            <span class="amount">₹{{ summaryStats.approvedAmount.toFixed(2) }}</span>
          </div>
        </div>

        <div class="stat-card rejected">
          <div class="stat-icon">
            <i class="fas fa-times-circle"></i>
          </div>
          <div class="stat-content">
            <h3>{{ summaryStats.rejected }}</h3>
            <p>Rejected</p>
          </div>
        </div>

        <div class="stat-card total">
          <div class="stat-icon">
            <i class="fas fa-calculator"></i>
          </div>
          <div class="stat-content">
            <h3>₹{{ summaryStats.totalAmount.toFixed(2) }}</h3>
            <p>Total Amount</p>
          </div>
        </div>
      </div>

      <!-- Expense Reports Table -->
      <div class="reports-container">
        <div v-if="loading" class="loading">
          <i class="fas fa-spinner fa-spin"></i>
          Loading expense reports...
        </div>

        <div v-else-if="filteredReports.length === 0" class="no-data">
          <i class="fas fa-inbox"></i>
          <p>No expense reports found</p>
        </div>

        <div v-else class="reports-list">
          <div v-for="report in filteredReports" :key="report.id" class="report-card">
            <!-- Card Header -->
            <div class="card-header" @click="toggleReportExpanded(report.id)">
              <div class="header-info">
                <div class="status-badge" :class="report.status">
                  {{ formatStatus(report.status) }}
                </div>
                <div class="submitter-info">
                  <h3>{{ report.user_name }}</h3>
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

              <!-- Report Details -->
              <div class="details-section">
                <div class="detail-row">
                  <label>Report ID:</label>
                  <span>{{ report.report_id }}</span>
                </div>
                <div class="detail-row">
                  <label>User ID:</label>
                  <span>{{ report.user_id }}</span>
                </div>
                <div class="detail-row">
                  <label>Total Amount:</label>
                  <span class="highlight">₹{{ report.total.toFixed(2) }}</span>
                </div>
                <div v-if="report.status !== 'pending'" class="detail-row">
                  <label>Approved By:</label>
                  <span>{{ report.approved_by_name || 'N/A' }}</span>
                </div>
              </div>

              <!-- Action Buttons -->
              <div v-if="report.status === 'pending'" class="action-buttons">
                <button @click="openApprovalDialog(report)" class="btn-approve">
                  <i class="fas fa-check"></i> Approve
                </button>
                <button @click="openRejectionDialog(report)" class="btn-reject">
                  <i class="fas fa-times"></i> Reject
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Approval Dialog -->
      <div v-if="showApprovalDialog" class="modal-overlay" @click.self="closeApprovalDialog">
        <div class="modal-dialog">
          <div class="modal-header">
            <h2>Approve Expense Report</h2>
            <button @click="closeApprovalDialog" class="btn-close">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to approve this expense report?</p>
            <div class="report-summary">
              <p><strong>Employee:</strong> {{ currentReport?.user_name }}</p>
              <p><strong>Total Amount:</strong> ₹{{ currentReport?.total.toFixed(2) }}</p>
            </div>
            <div class="form-group">
              <label for="approval-comments">Comments (Optional):</label>
              <textarea v-model="approvalComments" id="approval-comments" class="form-textarea"
                placeholder="Add any approval comments..."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="closeApprovalDialog" class="btn-secondary">
              Cancel
            </button>
            <button @click="confirmApproval" class="btn-primary" :disabled="approvingReport">
              <i v-if="approvingReport" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-check"></i>
              {{ approvingReport ? 'Approving...' : 'Approve' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Rejection Dialog -->
      <div v-if="showRejectionDialog" class="modal-overlay" @click.self="closeRejectionDialog">
        <div class="modal-dialog">
          <div class="modal-header">
            <h2>Reject Expense Report</h2>
            <button @click="closeRejectionDialog" class="btn-close">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <p>Please provide a reason for rejecting this expense report.</p>
            <div class="report-summary">
              <p><strong>Employee:</strong> {{ currentReport?.user_name }}</p>
              <p><strong>Total Amount:</strong> ₹{{ currentReport?.total.toFixed(2) }}</p>
            </div>
            <div class="form-group">
              <label for="rejection-reason">Rejection Reason:</label>
              <textarea v-model="rejectionReason" id="rejection-reason" class="form-textarea"
                placeholder="Explain why this report is being rejected..." required></textarea>
              <span v-if="rejectionReasonError" class="error-text">{{ rejectionReasonError }}</span>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="closeRejectionDialog" class="btn-secondary">
              Cancel
            </button>
            <button @click="confirmRejection" class="btn-danger" :disabled="rejectingReport || !rejectionReason.trim()">
              <i v-if="rejectingReport" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-times"></i>
              {{ rejectingReport ? 'Rejecting...' : 'Reject' }}
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
const expenseReports = ref([])
const loading = ref(false)
const expandedReports = ref(new Set())

// Filter state
const selectedStatus = ref('')
const selectedCategory = ref('')
const dateFrom = ref('')
const dateTo = ref('')

// Dialog state
const showApprovalDialog = ref(false)
const showRejectionDialog = ref(false)
const currentReport = ref(null)
const approvingReport = ref(false)
const rejectingReport = ref(false)
const approvalComments = ref('')
const rejectionReason = ref('')
const rejectionReasonError = ref('')

// Messages
const successMessage = ref('')
const errorMessage = ref('')

// Computed
const filteredReports = computed(() => {
  return expenseReports.value.filter(report => {
    let matches = true

    if (selectedStatus.value && report.status !== selectedStatus.value) {
      matches = false
    }

    if (selectedCategory.value) {
      const hasCategory = report.items.some(item => item.category === selectedCategory.value)
      if (!hasCategory) matches = false
    }

    if (dateFrom.value) {
      const reportDate = new Date(report.generated_at)
      const filterDate = new Date(dateFrom.value)
      if (reportDate < filterDate) matches = false
    }

    if (dateTo.value) {
      const reportDate = new Date(report.generated_at)
      const filterDate = new Date(dateTo.value)
      if (reportDate > filterDate) matches = false
    }

    return matches
  })
})

const summaryStats = computed(() => {
  const stats = {
    pending: 0,
    approved: 0,
    rejected: 0,
    totalAmount: 0,
    approvedAmount: 0
  }

  filteredReports.value.forEach(report => {
    if (report.status === 'pending') stats.pending++
    if (report.status === 'approved') {
      stats.approved++
      stats.approvedAmount += report.total
    }
    if (report.status === 'rejected') stats.rejected++
    stats.totalAmount += report.total
  })

  return stats
})

// Methods
const getAuthToken = () => localStorage.getItem('access_token')

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

function formatStatus(status) {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

function toggleReportExpanded(reportId) {
  if (expandedReports.value.has(reportId)) {
    expandedReports.value.delete(reportId)
  } else {
    expandedReports.value.add(reportId)
  }
}

async function loadExpenseReports() {
  loading.value = true
  try {
    const response = await axios.get('/api/expenses/', {
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

function applyFilters() {
  // Filters are applied via computed property
  console.log('Filters applied')
}

function clearFilters() {
  selectedStatus.value = ''
  selectedCategory.value = ''
  dateFrom.value = ''
  dateTo.value = ''
}

function viewReportDetails(reportId) {
  router.push(`/hr/expense-report/${reportId}`)
}

function openApprovalDialog(report) {
  currentReport.value = report
  approvalComments.value = ''
  showApprovalDialog.value = true
}

function closeApprovalDialog() {
  showApprovalDialog.value = false
  currentReport.value = null
  approvalComments.value = ''
}

async function confirmApproval() {
  if (!currentReport.value) return

  approvingReport.value = true
  try {
    const response = await axios.put(
      `/api/expenses/${currentReport.value.id}/approve`,
      {
        approver_id: JSON.parse(localStorage.getItem('user'))?.id,
        comments: approvalComments.value
      },
      {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      }
    )

    if (response.data.success) {
      // Update the report in the list
      const index = expenseReports.value.findIndex(r => r.id === currentReport.value.id)
      if (index !== -1) {
        expenseReports.value[index].status = 'approved'
      }

      showToast('Expense report approved successfully!', 'success')
      closeApprovalDialog()
    }
  } catch (error) {
    console.error('Failed to approve expense report:', error)
    showToast(error.response?.data?.error || 'Failed to approve expense report', 'error')
  } finally {
    approvingReport.value = false
  }
}

function openRejectionDialog(report) {
  currentReport.value = report
  rejectionReason.value = ''
  rejectionReasonError.value = ''
  showRejectionDialog.value = true
}

function closeRejectionDialog() {
  showRejectionDialog.value = false
  currentReport.value = null
  rejectionReason.value = ''
  rejectionReasonError.value = ''
}

async function confirmRejection() {
  if (!rejectionReason.value.trim()) {
    rejectionReasonError.value = 'Rejection reason is required'
    return
  }

  if (!currentReport.value) return

  rejectingReport.value = true
  try {
    const response = await axios.put(
      `/api/expenses/${currentReport.value.id}/reject`,
      {
        approver_id: JSON.parse(localStorage.getItem('user'))?.id,
        reason: rejectionReason.value
      },
      {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      }
    )

    if (response.data.success) {
      // Update the report in the list
      const index = expenseReports.value.findIndex(r => r.id === currentReport.value.id)
      if (index !== -1) {
        expenseReports.value[index].status = 'rejected'
      }

      showToast('Expense report rejected successfully!', 'success')
      closeRejectionDialog()
    }
  } catch (error) {
    console.error('Failed to reject expense report:', error)
    showToast(error.response?.data?.error || 'Failed to reject expense report', 'error')
  } finally {
    rejectingReport.value = false
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
.expense-reports-page {
  padding: 30px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 40px;
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

/* Filters Section */
.filters-section {
  background: white;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 30px;
  display: flex;
  gap: 15px;
  align-items: flex-end;
  flex-wrap: wrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

.filter-select,
.filter-input {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  min-width: 150px;
}

.filter-select:focus,
.filter-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.btn-apply,
.btn-clear {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-apply {
  background: #3498db;
  color: white;
}

.btn-apply:hover {
  background: #2980b9;
  transform: translateY(-1px);
}

.btn-clear {
  background: #95a5a6;
  color: white;
}

.btn-clear:hover {
  background: #7f8c8d;
  transform: translateY(-1px);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
  border-left: 4px solid #3498db;
}

.stat-card.pending {
  border-left-color: #f39c12;
}

.stat-card.approved {
  border-left-color: #27ae60;
}

.stat-card.rejected {
  border-left-color: #e74c3c;
}

.stat-card.total {
  border-left-color: #9b59b6;
}

.stat-icon {
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: #f5f7fa;
  border-radius: 8px;
  color: #3498db;
}

.stat-card.pending .stat-icon {
  color: #f39c12;
}

.stat-card.approved .stat-icon {
  color: #27ae60;
}

.stat-card.rejected .stat-icon {
  color: #e74c3c;
}

.stat-card.total .stat-icon {
  color: #9b59b6;
}

.stat-content h3 {
  margin: 0;
  font-size: 1.8rem;
  color: #2c3e50;
}

.stat-content p {
  margin: 5px 0 0 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.stat-content .amount {
  display: block;
  font-size: 0.85rem;
  color: #27ae60;
  font-weight: 600;
  margin-top: 5px;
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

.submitter-info h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.submitter-info .date {
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

.items-section,
.details-section {
  margin-bottom: 20px;
}

.items-section h4,
.details-section h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 1rem;
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
  transition: color 0.3s ease;
}

.receipt-link:hover {
  color: #2980b9;
}

.no-receipt {
  color: #bdc3c7;
}

/* Details Section */
.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #ecf0f1;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row label {
  font-weight: 600;
  color: #2c3e50;
}

.detail-row span {
  color: #7f8c8d;
}

.detail-row .highlight {
  color: #27ae60;
  font-weight: 600;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ecf0f1;
}

.action-buttons button {
  flex: 1;
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

.btn-view {
  background: #3498db;
  color: white;
}

.btn-view:hover {
  background: #2980b9;
}

.btn-approve {
  background: #27ae60;
  color: white;
}

.btn-approve:hover {
  background: #229954;
}

.btn-reject {
  background: #e74c3c;
  color: white;
}

.btn-reject:hover {
  background: #c0392b;
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
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #ecf0f1;
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

.modal-body p {
  margin: 0 0 15px 0;
  color: #7f8c8d;
}

.report-summary {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.report-summary p {
  margin: 8px 0;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.form-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.95rem;
  resize: vertical;
  min-height: 100px;
}

.form-textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.error-text {
  display: block;
  color: #e74c3c;
  font-size: 0.85rem;
  margin-top: 5px;
}

.modal-footer {
  display: flex;
  gap: 10px;
  padding: 20px;
  background: #f8f9fa;
  border-top: 1px solid #ecf0f1;
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

.btn-primary {
  background: #27ae60;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #229954;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c0392b;
}

.btn-primary:disabled,
.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  .filters-section {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-select,
  .filter-input,
  .btn-apply,
  .btn-clear {
    width: 100%;
  }

  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-amount {
    width: 100%;
    justify-content: space-between;
    margin-top: 10px;
  }

  .items-table {
    font-size: 0.85rem;
  }

  .items-table th,
  .items-table td {
    padding: 8px 5px;
  }

  .action-buttons {
    flex-direction: column;
  }

  .modal-dialog {
    width: 95%;
  }
}
</style>
