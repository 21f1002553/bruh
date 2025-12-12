<template>
  <DashboardLayout>
    <div class="hr-employees-page">
      <div class="page-header">
        <div>
          <h1>Employee Management</h1>
          <p class="subtitle">Manage your team members and their roles</p>
        </div>
        <button class="btn-primary" @click="openCreateModal">
          <i class="fas fa-plus"></i>
          Add Employee
        </button>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="employee-count">
            <i class="fas fa-users"></i>
            <span><strong>{{ employees.length }}</strong> Total Employees</span>
          </div>
        </div>

        <div v-if="loading" class="state-row">
          <i class="fas fa-spinner fa-spin"></i>
          <span>Loading employees...</span>
        </div>

        <div v-else-if="error" class="state-row error">
          <i class="fas fa-exclamation-circle"></i>
          <span>{{ error }}</span>
        </div>

        <div v-else-if="employees.length === 0" class="state-row empty">
          <div class="empty-state">
            <i class="fas fa-user-friends"></i>
            <h3>No employees yet</h3>
            <p>Get started by adding your first team member</p>
            <button class="btn-primary" @click="openCreateModal">
              <i class="fas fa-plus"></i>
              Add Employee
            </button>
          </div>
        </div>

        <div v-else class="table-wrapper">
          <table class="employees-table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Role</th>
                <th>Status</th>
                <th>Joined</th>
                <th class="actions-header">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="emp in employees" :key="emp.id" class="employee-row">
                <td>
                  <div class="employee-info">
                    <div class="avatar">{{ getInitials(emp.name) }}</div>
                    <div class="employee-details">
                      <div class="employee-name">{{ emp.name }}</div>
                      <div class="employee-email">{{ emp.email }}</div>
                    </div>
                  </div>
                </td>
                <td>
                  <span class="role-badge">{{ emp.role_name }}</span>
                </td>
                <td>
                  <span class="status-badge" :class="emp.status === 'active' ? 'active' : 'inactive'">
                    <i class="fas fa-circle"></i>
                    {{ emp.status || 'N/A' }}
                  </span>
                </td>
                <td class="date-cell">{{ formatDate(emp.created_at) }}</td>
                <td class="actions-cell">
                  <label class="switch" :title="emp.status === 'active' ? 'Active' : 'Inactive'">
                    <input type="checkbox" :checked="emp.status === 'active'" @change="toggleStatus(emp)">
                    <span class="slider"></span>
                  </label>
                  <button class="btn-action danger" @click="deleteEmployee(emp)" title="Delete">
                    <i class="fas fa-trash-alt"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Add Employee modal -->
      <transition name="modal">
        <div v-if="showCreateModal" class="modal-backdrop" @click.self="closeCreateModal">
          <div class="modal">
            <div class="modal-header">
              <h2>Add New Employee</h2>
              <button class="btn-close" @click="closeCreateModal">
                <i class="fas fa-times"></i>
              </button>
            </div>

            <div class="modal-body">
              <div class="form-row">
                <label>Full Name <span class="required">*</span></label>
                <div class="input-wrapper">
                  <i class="fas fa-user"></i>
                  <input v-model="newEmployee.name" type="text" placeholder="John Doe" />
                </div>
              </div>

              <div class="form-row">
                <label>Email Address <span class="required">*</span></label>
                <div class="input-wrapper">
                  <i class="fas fa-envelope"></i>
                  <input v-model="newEmployee.email" type="email" placeholder="john@example.com" />
                </div>
              </div>

              <div class="form-row">
                <label>Role <span class="required">*</span></label>
                <div class="input-wrapper">
                  <i class="fas fa-briefcase"></i>
                  <select v-model="newEmployee.role_id">
                    <option disabled value="">Select a role</option>
                    <option v-for="role in roles" :key="role.id" :value="role.id">
                      {{ role.name }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="form-row">
                <label>Status</label>
                <div class="input-wrapper">
                  <i class="fas fa-toggle-on"></i>
                  <select v-model="newEmployee.status">
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>
              </div>

              <p v-if="createError" class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                {{ createError }}
              </p>
            </div>

            <div class="modal-actions">
              <button class="btn-secondary" @click="closeCreateModal">Cancel</button>
              <button class="btn-primary" @click="createEmployee">
                <i class="fas fa-check"></i>
                Create Employee
              </button>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'

const employees = ref([])
const loading = ref(false)
const error = ref('')

const showCreateModal = ref(false)
const createError = ref('')
const newEmployee = ref({
  name: '',
  email: '',
  role_id: '',
  status: 'active'
})

const roles = ref([])
const loadingRoles = ref(false)

function getInitials(name) {
  if (!name) return '??'
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

function formatDate(dateString) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

async function fetchEmployees() {
  loading.value = true
  error.value = ''
  try {
    const resp = await axios.get('/api/users/employees', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    employees.value = Array.isArray(resp.data) ? resp.data : []
  } catch (e) {
    console.error('Failed to load employees:', e)
    error.value = e.response?.data?.error || 'Failed to load employees'
  } finally {
    loading.value = false
  }
}

async function fetchRoles() {
  loadingRoles.value = true
  try {
    const resp = await axios.get('/api/users/roles', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    roles.value = Array.isArray(resp.data) ? resp.data : []
  } catch (e) {
    console.error('Failed to load roles:', e)
  } finally {
    loadingRoles.value = false
  }
}

function openCreateModal() {
  createError.value = ''
  newEmployee.value = {
    name: '',
    email: '',
    role_id: '',
    status: 'active'
  }
  showCreateModal.value = true
}

function closeCreateModal() {
  showCreateModal.value = false
}

async function createEmployee() {
  createError.value = ''
  if (!newEmployee.value.name || !newEmployee.value.email || !newEmployee.value.role_id) {
    createError.value = 'Name, email and role are required'
    return
  }
  try {
    await axios.post(
      '/api/users/',
      {
        name: newEmployee.value.name,
        email: newEmployee.value.email,
        role_id: newEmployee.value.role_id,
        status: newEmployee.value.status
      },
      {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      }
    )
    showCreateModal.value = false
    await fetchEmployees()
  } catch (e) {
    console.error('Failed to create employee:', e)
    createError.value = e.response?.data?.error || 'Failed to create employee'
  }
}

async function toggleStatus(emp) {
  const newStatus = emp.status === 'active' ? 'inactive' : 'active'
  try {
    await axios.put(
      `/api/users/${emp.id}`,
      { status: newStatus },
      {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      }
    )
    emp.status = newStatus
  } catch (e) {
    console.error('Failed to update status:', e)
    alert(e.response?.data?.error || 'Failed to update status')
  }
}

async function deleteEmployee(emp) {
  if (!confirm(`Delete ${emp.name}? This cannot be undone.`)) return
  try {
    await axios.delete(`/api/users/${emp.id}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    employees.value = employees.value.filter(e => e.id !== emp.id)
  } catch (e) {
    console.error('Failed to delete employee:', e)
    alert(e.response?.data?.error || 'Failed to delete employee')
  }
}

onMounted(async () => {
  await Promise.all([fetchEmployees(), fetchRoles()])
})
</script>

<style scoped>
.hr-employees-page {
  padding: 32px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  margin-right: 8px;
  cursor: pointer;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #e5e7eb;
  border-radius: 24px;
  transition: 0.3s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  border-radius: 50%;
  transition: 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.switch input:checked+.slider {
  background-color: #10b981;
}

.switch input:checked+.slider:before {
  transform: translateX(20px);
}

.switch:hover .slider {
  opacity: 0.9;
}

h1 {
  margin: 0 0 6px 0;
  font-size: 2rem;
  font-weight: 700;
  color: #1a1a1a;
}

.subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 0.95rem;
}

.card {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.card-header {
  padding: 24px 28px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(to bottom, #fafafa, #ffffff);
}

.employee-count {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #374151;
  font-size: 0.95rem;
}

.employee-count i {
  color: #3498db;
  font-size: 1.1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  border: none;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(52, 152, 219, 0.2);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(52, 152, 219, 0.3);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-secondary {
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  color: #374151;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.table-wrapper {
  overflow-x: auto;
}

.employees-table {
  width: 100%;
  border-collapse: collapse;
}

.employees-table th {
  padding: 16px 24px;
  background: #f9fafb;
  text-align: left;
  font-size: 0.8rem;
  font-weight: 700;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #e5e7eb;
}

.employees-table td {
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 0.9rem;
}

.employee-row {
  transition: background-color 0.15s ease;
}

.employee-row:hover {
  background-color: #f9fafb;
}

.employee-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.employee-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.employee-name {
  font-weight: 600;
  color: #1a1a1a;
}

.employee-email {
  font-size: 0.85rem;
  color: #6b7280;
}

.role-badge {
  display: inline-block;
  padding: 6px 12px;
  background: #eff6ff;
  color: #1e40af;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge i {
  font-size: 0.5rem;
}

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.active i {
  color: #10b981;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.inactive i {
  color: #ef4444;
}

.date-cell {
  color: #6b7280;
}

.actions-header {
  text-align: right;
}

.actions-cell {
  text-align: right;
}

.btn-action {
  background: transparent;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.btn-action:hover {
  background: #f3f4f6;
  color: #3498db;
}

.btn-action.danger:hover {
  background: #fef2f2;
  color: #dc2626;
}

.state-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px 24px;
  color: #6b7280;
}

.state-row i {
  font-size: 1.4rem;
}

.state-row.error {
  color: #dc2626;
}

.empty-state {
  text-align: center;
  padding: 20px;
}

.empty-state i {
  font-size: 3.5rem;
  color: #d1d5db;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 1.2rem;
  color: #374151;
}

.empty-state p {
  margin: 0 0 24px 0;
  color: #6b7280;
  font-size: 0.95rem;
}

/* Modal styles */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.modal {
  background: #fff;
  border-radius: 16px;
  width: 480px;
  max-width: 90%;
  max-height: 90vh;
  overflow: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 700;
  color: #1a1a1a;
}

.btn-close {
  background: transparent;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
  font-size: 1.1rem;
}

.btn-close:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-body {
  padding: 24px 28px;
}

.form-row {
  margin-bottom: 20px;
}

.form-row label {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: #374151;
}

.required {
  color: #dc2626;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper i {
  position: absolute;
  left: 14px;
  color: #9ca3af;
  font-size: 0.9rem;
}

.input-wrapper input,
.input-wrapper select {
  width: 100%;
  padding: 11px 14px 11px 15px;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  font-size: 0.95rem;
  transition: all 0.2s ease;
  background: #ffffff;
  margin-left: 20px;
}

.input-wrapper input:focus,
.input-wrapper select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 28px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 16px 0 0 0;
  padding: 12px 16px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #991b1b;
  font-size: 0.85rem;
}

.error-message i {
  color: #dc2626;
}

/* Modal transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal,
.modal-leave-active .modal {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal,
.modal-leave-to .modal {
  transform: scale(0.95);
}

/* Responsive */
@media (max-width: 768px) {
  .hr-employees-page {
    padding: 20px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .employees-table th,
  .employees-table td {
    padding: 12px 16px;
  }

  .employee-info {
    gap: 10px;
  }

  .avatar {
    width: 36px;
    height: 36px;
    font-size: 0.8rem;
  }
}
</style>