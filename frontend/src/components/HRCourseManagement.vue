<template>
  <DashboardLayout>
    <div class="course-management">
      <header class="page-header">
        <h1>Course Management</h1>
        <p>Create and manage training courses</p>
      </header>

      <!-- Success/Error Messages -->
      <div v-if="successMessage" class="alert alert-success">
        {{ successMessage }}
      </div>
      <div v-if="errorMessage" class="alert alert-error">
        {{ errorMessage }}
      </div>

      <!-- Create New Course Section -->
      <div class="course-form-container">
        <h2>{{ editingCourse ? 'Edit Course' : 'Create New Course' }}</h2>
        <form @submit.prevent="submitCourse" class="course-form">
          <div class="form-row">
            <div class="form-group">
              <label for="training">Training Program *</label>
              <select v-model="courseForm.training_id" id="training" required>
                <option value="">Select Training Program</option>
                <option v-for="training in trainings" :key="training.id" :value="training.id">
                  {{ training.title }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="title">Course Title *</label>
              <input v-model="courseForm.title" type="text" id="title"
                placeholder="e.g., Introduction to Teaching Methods" required />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="duration">Duration (minutes) *</label>
              <input v-model.number="courseForm.duration_mins" type="number" id="duration" placeholder="e.g., 60"
                min="1" required />
            </div>

            <div class="form-group">
              <label for="content_url">Content URL</label>
              <input v-model="courseForm.content_url" type="url" id="content_url"
                placeholder="https://example.com/course-materials" />
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary">
              {{ editingCourse ? 'Update Course' : 'Create Course' }}
            </button>
            <button v-if="editingCourse" type="button" @click="cancelEdit" class="btn btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      </div>

      <!-- Create New Training Program -->
      <div class="training-form-container">
        <button @click="showTrainingForm = !showTrainingForm" class="btn btn-outline">
          {{ showTrainingForm ? 'Hide' : 'Create New Training Program' }}
        </button>

        <form v-if="showTrainingForm" @submit.prevent="createTraining" class="training-form">
          <div class="form-row">
            <div class="form-group">
              <label for="training_title">Training Program Title *</label>
              <input v-model="trainingForm.title" type="text" id="training_title"
                placeholder="e.g., Teacher Onboarding Program" required />
            </div>
          </div>

          <div class="form-group">
            <label for="training_description">Description</label>
            <textarea v-model="trainingForm.description" id="training_description" rows="3"
              placeholder="Describe the training program..."></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="start_date">Start Date</label>
              <input v-model="trainingForm.start_date" type="date" id="start_date" />
            </div>

            <div class="form-group">
              <label for="end_date">End Date</label>
              <input v-model="trainingForm.end_date" type="date" id="end_date" />
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Create Training Program</button>
          </div>
        </form>
      </div>

      <!-- Existing Courses List -->
      <div class="courses-list-container">
        <h2>Existing Courses</h2>

        <div v-if="loading" class="loading">Loading courses...</div>

        <div v-else-if="courses.length === 0" class="no-courses">
          No courses available. Create your first course above!
        </div>

        <div v-else class="courses-grid">
          <div v-for="course in courses" :key="course.id" class="course-card">
            <div class="course-header">
              <h3>{{ course.title }}</h3>
              <span class="course-duration">{{ course.duration_mins }} mins</span>
            </div>
            <div class="course-body">
              <p class="training-name">
                <strong>Program:</strong> {{ course.training_title || 'N/A' }}
              </p>
              <p v-if="course.content_url" class="course-url">
                <strong>Content:</strong>
                <a :href="course.content_url" target="_blank">View Materials</a>
              </p>
            </div>
            <div class="course-actions">
              <button @click="editCourse(course)" class="btn btn-sm btn-edit">Edit</button>
              <button @click="deleteCourse(course.id)" class="btn btn-sm btn-delete">Delete</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import axios from 'axios';
import DashboardLayout from './DashboardLayout.vue'

const API_BASE_URL = 'http://localhost:5001/api';

// State
const courses = ref([]);
const trainings = ref([]);
const loading = ref(false);
const successMessage = ref('');
const errorMessage = ref('');
const showTrainingForm = ref(false);
const editingCourse = ref(null);

// Forms
const courseForm = ref({
  training_id: '',
  title: '',
  content_url: '',
  duration_mins: 60
});

const trainingForm = ref({
  title: '',
  description: '',
  start_date: '',
  end_date: ''
});

// Load data on mount
onMounted(() => {
  loadCourses();
  loadTrainings();
});

// Functions
const loadCourses = async () => {
  loading.value = true;
  try {
    const response = await axios.get(`${API_BASE_URL}/training/courses`);
    courses.value = response.data.data || [];
  } catch (error) {
    showError('Failed to load courses: ' + (error.response?.data?.error || error.message));
  } finally {
    loading.value = false;
  }
};

const loadTrainings = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/training/programs`);
    trainings.value = response.data.data || [];
  } catch (error) {
    showError('Failed to load training programs: ' + (error.response?.data?.error || error.message));
  }
};

const submitCourse = async () => {
  try {
    if (editingCourse.value) {
      // Update existing course
      await axios.put(`${API_BASE_URL}/training/courses/${editingCourse.value.id}`, courseForm.value);
      showSuccess('Course updated successfully!');
    } else {
      // Create new course
      await axios.post(`${API_BASE_URL}/training/courses`, courseForm.value);
      showSuccess('Course created successfully!');
    }

    resetCourseForm();
    loadCourses();
  } catch (error) {
    showError('Failed to save course: ' + (error.response?.data?.error || error.message));
  }
};

const createTraining = async () => {
  try {
    await axios.post(`${API_BASE_URL}/training/programs`, trainingForm.value);
    showSuccess('Training program created successfully!');
    resetTrainingForm();
    showTrainingForm.value = false;
    loadTrainings();
  } catch (error) {
    showError('Failed to create training program: ' + (error.response?.data?.error || error.message));
  }
};


const editCourse = async (course) => {
  editingCourse.value = course;
  courseForm.value = {
    training_id: course.training_id,
    title: course.title,
    content_url: course.content_url || '',
    duration_mins: course.duration_mins || 60
  };

  // Wait for Vue to update the DOM (form appears at top)
  await nextTick();

  // This is the actual scrolling container in your DashboardLayout
  const contentArea = document.querySelector('.content-area');
  if (contentArea) {
    contentArea.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }
};

const cancelEdit = () => {
  editingCourse.value = null;
  resetCourseForm();
};

const deleteCourse = async (courseId) => {
  if (!confirm('Are you sure you want to delete this course?')) return;

  try {
    await axios.delete(`${API_BASE_URL}/training/courses/${courseId}`);
    showSuccess('Course deleted successfully!');
    loadCourses();
  } catch (error) {
    showError('Failed to delete course: ' + (error.response?.data?.error || error.message));
  }
};

const resetCourseForm = () => {
  courseForm.value = {
    training_id: '',
    title: '',
    content_url: '',
    duration_mins: 60
  };
  editingCourse.value = null;
};

const resetTrainingForm = () => {
  trainingForm.value = {
    title: '',
    description: '',
    start_date: '',
    end_date: ''
  };
};

const showSuccess = (message) => {
  successMessage.value = message;
  errorMessage.value = '';
  setTimeout(() => successMessage.value = '', 5000);
};

const showError = (message) => {
  errorMessage.value = message;
  successMessage.value = '';
  setTimeout(() => errorMessage.value = '', 5000);
};
</script>

<style scoped>
/* Base Layout */
.course-management {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Header */
.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 8px;
}

.page-header p {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

/* Alerts */
.alert {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 14px;
  border: 1px solid;
}

.alert-success {
  background: #f0fdf4;
  color: #166534;
  border-color: #bbf7d0;
}

.alert-error {
  background: #fef2f2;
  color: #991b1b;
  border-color: #fecaca;
}

/* Form Containers */
.course-form-container,
.training-form-container {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
}

.course-form-container h2,
.training-form-container h2 {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 20px;
}

/* Forms */
.course-form,
.training-form {
  margin-top: 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
  background: #fff;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #2563eb;
}

.form-group textarea {
  resize: vertical;
  font-family: inherit;
}

/* Buttons */
.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #2563eb;
  color: #fff;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-secondary {
  background: #6b7280;
  color: #fff;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-outline {
  background: #fff;
  color: #2563eb;
  border: 1px solid #2563eb;
  width: 100%;
  margin-bottom: 16px;
}

.btn-outline:hover {
  background: #2563eb;
  color: #fff;
}

/* Courses List */
.courses-list-container {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 24px;
}

.courses-list-container h2 {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 20px;
}

.loading,
.no-courses {
  text-align: center;
  padding: 40px 20px;
  color: #9ca3af;
  font-size: 14px;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

/* Course Card */
.course-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  transition: border-color 0.2s;
}

.course-card:hover {
  border-color: #2563eb;
}

.course-header {
  display: flex;
  align-items: start;
  gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.course-header h3 {
  font-size: 16px;
  font-weight: 500;
  color: #111827;
  margin: 0;
  flex: 1;
  line-height: 1.4;
}

.course-duration {
  background: #2563eb;
  color: #fff;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.course-body {
  margin-bottom: 12px;
}

.course-body p {
  margin: 6px 0;
  color: #6b7280;
  font-size: 13px;
  line-height: 1.5;
}

.course-body strong {
  color: #374151;
  font-weight: 500;
}

.course-url a {
  color: #2563eb;
  text-decoration: none;
}

.course-url a:hover {
  text-decoration: underline;
}

.course-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.btn-sm {
  padding: 8px 14px;
  font-size: 13px;
  flex: 1;
}

.btn-edit {
  background: #f59e0b;
  color: #fff;
}

.btn-edit:hover {
  background: #d97706;
}

.btn-delete {
  background: #dc2626;
  color: #fff;
}

.btn-delete:hover {
  background: #b91c1c;
}

/* Responsive */
@media (max-width: 768px) {
  .course-management {
    padding: 16px;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .courses-grid {
    grid-template-columns: 1fr;
  }

  .course-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .course-duration {
    margin-top: 4px;
  }
}
</style>
