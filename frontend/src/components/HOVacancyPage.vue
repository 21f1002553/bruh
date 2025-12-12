<template>
  <DashboardLayout>
    <div class="hovacancy-page">
      <div class="page-header">
        <div>
          <h1><i class="fas fa-briefcase"></i> Vacancies</h1>
          <p>View, filter, create and manage vacancies.</p>
        </div>
        <div>
          <button class="btn-create" @click="openCreateModal">
            <i class="fas fa-plus"></i> New Vacancy
          </button>
        </div>
      </div>

      <div class="filters">
        <input v-model="filters.search" placeholder="Search title or location" @input="debouncedLoad" />
        <select v-model="filters.location" @change="loadVacancies">
          <option value="">All Locations</option>
          <option v-for="loc in locations" :key="loc" :value="loc">{{ loc }}</option>
        </select>
        <select v-model="filters.school" @change="loadVacancies">
          <option value="">All Schools</option>
          <option v-for="s in schools" :key="s" :value="s">{{ s }}</option>
        </select>
        <select v-model="filters.level" @change="loadVacancies">
          <option value="">All Levels</option>
          <option v-for="l in levels" :key="l" :value="l">{{ l }}</option>
        </select>
      </div>

      <div class="vacancies-list">
        <div v-if="loading" class="loading">Loading vacancies...</div>

        <div v-else-if="vacancies.length === 0" class="no-data">No vacancies found.</div>

        <div v-else class="grid">
          <div v-for="vacancy in vacancies" :key="vacancy.id" class="vacancy-card">
            <div class="vacancy-header">
              <h3>{{ vacancy.title }}</h3>
              <span class="status" :class="vacancy.status">{{ vacancy.status }}</span>
            </div>
            <p class="meta">
              <strong>{{ vacancy.school || vacancy.location }}</strong>
            </p>
            <p class="desc">{{ truncate(vacancy.description, 180) }}</p>
            <div class="actions">
              <button class="btn-edit" @click="openEditModal(vacancy)">Edit</button>
              <button class="btn-delete" @click="deleteVacancy(vacancy.id)">Delete</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Create/Edit Modal -->
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-dialog">
          <div class="modal-header">
            <h2>{{ editingId ? 'Edit Vacancy' : 'Create Vacancy' }}</h2>
            <button class="btn-close" @click="closeModal"><i class="fas fa-times"></i></button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>Title *</label>
              <input v-model="vacancyForm.title" type="text" />
            </div>
            <div class="form-group">
              <label>Location</label>
              <input v-model="vacancyForm.location" type="text" />
            </div>
            <div class="form-group">
              <label>School</label>
              <input v-model="vacancyForm.school" type="text" />
            </div>
            <div class="form-group">
              <label>Level</label>
              <input v-model="vacancyForm.level" type="text" />
            </div>
            <div class="form-group">
              <label>Description</label>
              <textarea v-model="vacancyForm.description" rows="4"></textarea>
            </div>
            <div class="form-group">
              <label>Requirements</label>
              <textarea v-model="vacancyForm.requirements" rows="3"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="closeModal">Cancel</button>
            <button class="btn-primary" :disabled="saving" @click="saveVacancy">{{ saving ? 'Saving...' : (editingId ?
              'Update' : 'Create') }}</button>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'

const vacancies = ref([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const editingId = ref(null)
const vacancyForm = ref({ title: '', location: '', school: '', level: '', description: '', requirements: '', status: 'active', posted_by_id: null })
const filters = ref({ search: '', location: '', school: '', level: '' })
const locations = ref([])
const schools = ref([])
const levels = ref([])
const hoId = ref(null)
const hoName = ref('')

const getAuthToken = () => localStorage.getItem('access_token')

function truncate(text, n) {
  if (!text) return ''
  return text.length > n ? text.substring(0, n) + '...' : text
}

async function loadHOData() {
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/users/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    hoName.value = response.data.name
    hoId.value = response.data.id
    vacancyForm.value.posted_by_id = hoId.value
  } catch (error) {
    console.error('Error loading HO data:', error)
  }
}

async function loadVacancies() {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.q = filters.value.search
    if (filters.value.location) params.location = filters.value.location
    if (filters.value.school) params.school = filters.value.school
    if (filters.value.level) params.level = filters.value.level

    const resp = await axios.get('/api/vacancies/', {
      params,
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    vacancies.value = resp.data || []

    const locSet = new Set()
    const schoolSet = new Set()
    const levelSet = new Set()
    vacancies.value.forEach(v => {
      if (v.location) locSet.add(v.location)
      if (v.school) schoolSet.add(v.school)
      if (v.level) levelSet.add(v.level)
    })
    locations.value = Array.from(locSet).sort()
    schools.value = Array.from(schoolSet).sort()
    levels.value = Array.from(levelSet).sort()
  } catch (err) {
    console.error('Failed to load vacancies', err)
  } finally {
    loading.value = false
  }
}

let debounceTimer = null
function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => loadVacancies(), 350)
}

function openCreateModal() {
  editingId.value = null
  vacancyForm.value = { title: '', location: '', school: '', level: '', description: '', requirements: '', status: 'active' }
  showModal.value = true
}

function openEditModal(vacancy) {
  editingId.value = vacancy.id
  vacancyForm.value = { ...vacancy }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

async function saveVacancy() {
  if (!vacancyForm.value.title) {
    alert('Title is required')
    return
  }
  saving.value = true
  try {
    if (editingId.value) {
      await axios.put(`/api/vacancies/${editingId.value}`, vacancyForm.value, { headers: { Authorization: `Bearer ${getAuthToken()}` } })
      alert('Vacancy updated')
    } else {
      vacancyForm.value.posted_by_id = hoId.value
      await axios.post('/api/vacancies/', vacancyForm.value, { headers: { Authorization: `Bearer ${getAuthToken()}` } })
      alert('Vacancy created')
    }
    closeModal()
    loadVacancies()

  } catch (err) {
    console.error('Failed to save vacancy', err)
    alert(err.response?.data?.error || 'Failed to save vacancy')
  } finally {
    saving.value = false
    window.location.reload()
  }
}

async function deleteVacancy(id) {
  if (!confirm('Delete this vacancy?')) return
  try {
    await axios.delete(`/api/vacancies/${id}`, { headers: { Authorization: `Bearer ${getAuthToken()}` } })
    alert('Vacancy deleted')
    loadVacancies()
  } catch (err) {
    console.error('Failed to delete vacancy', err)
    alert(err.response?.data?.error || 'Failed to delete vacancy')
  }
}

onMounted(async () => {
  loadVacancies()
  await loadHOData()
})
</script>

<style scoped>
.hovacancy-page {
  padding: 24px;
  max-width: 1100px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px
}

.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 16px
}

.filters input,
.filters select {
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px
}

.vacancies-list .grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px
}

.vacancy-card {
  background: #fff;
  padding: 14px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05)
}

.vacancy-header {
  display: flex;
  justify-content: space-between;
  align-items: center
}

.vacancy-header h3 {
  margin: 0
}

.status {
  padding: 6px 10px;
  border-radius: 16px;
  font-weight: 600
}

.status.active {
  background: #d4edda;
  color: #155724
}

.actions {
  margin-top: 12px;
  display: flex;
  gap: 8px
}

.btn-edit {
  background: #3498db;
  color: white;
  padding: 8px 12px;
  border: none;
  border-radius: 6px
}

.btn-delete {
  background: #e74c3c;
  color: white;
  padding: 8px 12px;
  border: none;
  border-radius: 6px
}

.btn-create {
  background: #27ae60;
  color: white;
  padding: 10px 14px;
  border: none;
  border-radius: 8px
}

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
  z-index: 2000
}

.modal-dialog {
  background: white;
  width: 100%;
  max-width: 700px;
  border-radius: 10px;
  overflow: hidden
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px;
  background: #f8f9fa
}

.modal-body {
  padding: 16px
}

.modal-footer {
  padding: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  border-top: 1px solid #eee
}

.btn-secondary {
  background: #95a5a6;
  color: white;
  padding: 8px 12px;
  border: none;
  border-radius: 6px
}

.btn-primary {
  background: #3498db;
  color: white;
  padding: 8px 12px;
  border: none;
  border-radius: 6px
}
</style>