<template>
  <DashboardLayout>
    <div class="hr-notifications-page">
      <!-- Header -->
      <header class="dashboard-header">
        <div class="header-left">
          <h1>Notifications</h1>
        </div>
        <div class="header-right">
          <button class="action-btn secondary" @click="markAllAsRead" :disabled="unreadCount === 0">
            <i class="fas fa-check-double"></i> Mark All as Read
          </button>
        </div>
      </header>

      <!-- Notifications List -->
      <div class="notifications-container">
        <div v-if="loading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading notifications...</p>
        </div>
        
        <div v-else-if="notifications.length === 0" class="empty-state">
          <i class="fas fa-bell-slash"></i>
          <p>No notifications</p>
        </div>

        <div v-else class="notifications-list">
          <div 
            v-for="notification in notifications" 
            :key="notification.id" 
            class="notification-item"
            :class="{ unread: !notification.read }"
            @click="markAsRead(notification)"
          >
            <div class="notification-icon" :class="getNotificationIconClass(notification.message)">
              <i :class="getNotificationIcon(notification.message)"></i>
            </div>
            
            <div class="notification-content">
              <div class="notification-header">
                <p>{{ notification.message }}</p>
                <span class="time">{{ formatTime(notification.created_at) }}</span>
              </div>
            </div>

            <div class="notification-actions">
              <button v-if="!notification.read" class="read-btn" title="Mark as read">
                <div class="dot"></div>
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
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'

const loading = ref(false)
const notifications = ref([])

const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.read).length
})

function getAuthToken() {
  return localStorage.getItem('access_token')
}

async function loadNotifications() {
  loading.value = true
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/notifications/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    // Backend now filters by current user automatically
    notifications.value = response.data || []
  } catch (error) {
    console.error('Error loading notifications:', error)
  } finally {
    loading.value = false
  }
}

async function markAsRead(notification) {
  if (notification.read) return

  try {
    const token = getAuthToken()
    await axios.post(`/api/notifications/mark-read/${notification.id}`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    })
    notification.read = true
  } catch (error) {
    console.error('Error marking notification as read:', error)
  }
}

async function markAllAsRead() {
  try {
    const unread = notifications.value.filter(n => !n.read)
    await Promise.all(unread.map(n => markAsRead(n)))
  } catch (error) {
    console.error('Error marking all as read:', error)
  }
}

function formatTime(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  
  // If less than 24 hours, show relative time
  if (diff < 24 * 60 * 60 * 1000) {
    if (diff < 60 * 60 * 1000) {
      const minutes = Math.floor(diff / (60 * 1000))
      return `${minutes}m ago`
    }
    const hours = Math.floor(diff / (60 * 60 * 1000))
    return `${hours}h ago`
  }
  
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
}

function getNotificationIcon(message) {
  if (!message) return 'fas fa-bell'
  const msg = message.toLowerCase()
  if (msg.includes('hired') || msg.includes('congratulations')) return 'fas fa-check-circle'
  if (msg.includes('offer')) return 'fas fa-envelope'
  if (msg.includes('interview')) return 'fas fa-calendar-alt'
  if (msg.includes('technical test') || msg.includes('test')) return 'fas fa-code'
  if (msg.includes('completed')) return 'fas fa-check-double'
  return 'fas fa-bell'
}

function getNotificationIconClass(message) {
  if (!message) return 'type-info'
  const msg = message.toLowerCase()
  if (msg.includes('hired') || msg.includes('congratulations')) return 'type-success'
  if (msg.includes('offer')) return 'type-offer'
  if (msg.includes('interview')) return 'type-interview'
  if (msg.includes('technical test') || msg.includes('test')) return 'type-test'
  if (msg.includes('completed')) return 'type-success'
  return 'type-info'
}

onMounted(() => {
  loadNotifications()
})
</script>

<style scoped>
.hr-notifications-page {
  padding: 24px;
  background: #f8f9fa;
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.header-left h1 {
  margin: 0;
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 700;
}

.action-btn {
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  border: none;
}

.action-btn.secondary {
  background: white;
  border: 1px solid #ddd;
  color: #555;
}

.action-btn.secondary:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #ccc;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #95a5a6;
}

.loading-state i,
.empty-state i {
  font-size: 3rem;
  margin-bottom: 20px;
}

/* Notifications List */
.notifications-list {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  overflow: hidden;
}

.notification-item {
  display: flex;
  gap: 20px;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item:hover {
  background: #f8f9fa;
}

.notification-item.unread {
  background: #f0f4ff;
}

.notification-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.type-info { 
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.type-success { 
  background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
  color: white;
}

.type-offer { 
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  color: white;
}

.type-interview { 
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
}

.type-test { 
  background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
  color: white;
}

.type-warning { 
  background: #fff3cd;
  color: #856404;
}

.type-error { 
  background: #f8d7da;
  color: #721c24;
}

.notification-content {
  flex: 1;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 15px;
}

.notification-header p {
  margin: 0;
  color: #2c3e50;
  font-size: 0.95rem;
  line-height: 1.6;
  flex: 1;
}

.time {
  font-size: 0.85rem;
  color: #95a5a6;
  flex-shrink: 0;
}

.notification-actions {
  display: flex;
  align-items: center;
}

.read-btn {
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
}

.dot {
  width: 10px;
  height: 10px;
  background: #667eea;
  border-radius: 50%;
}
</style>
