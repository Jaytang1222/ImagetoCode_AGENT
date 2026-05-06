<template>
  <AppleCard :variant="variant" class="agent-status-card">
    <div class="agent-header">
      <div class="agent-info">
        <h3 class="text-utility">{{ title }}</h3>
        <p class="text-control text-secondary">{{ description }}</p>
      </div>
      <div :class="['status-indicator', `status-indicator--${status}`]">
        <span class="status-dot"></span>
      </div>
    </div>
    
    <div v-if="status !== 'idle'" class="agent-content">
      <div v-if="currentTask" class="current-task">
        <p class="text-control">{{ currentTask }}</p>
      </div>
      
      <div v-if="progress !== null" class="progress-bar">
        <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
      </div>
      
      <div v-if="message" class="agent-message">
        <p class="text-micro text-secondary">{{ message }}</p>
      </div>
    </div>
  </AppleCard>
</template>

<script setup>
import AppleCard from './AppleCard.vue'

defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  status: {
    type: String,
    default: 'idle',
    validator: (value) => ['idle', 'running', 'success', 'error'].includes(value)
  },
  currentTask: {
    type: String,
    default: ''
  },
  progress: {
    type: Number,
    default: null
  },
  message: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'dark'
  }
})
</script>

<style scoped>
.agent-status-card {
  height: 100%;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-14);
  margin-bottom: var(--space-24);
  padding-bottom: var(--space-20);
  border-bottom: 1px solid rgba(173, 222, 239, 0.15);
}

.agent-info {
  flex: 1;
}

.agent-info h3 {
  margin-bottom: var(--space-10);
  color: var(--color-primary-green);
}

.status-indicator {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-circle);
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(165, 231, 165, 0.15) 0%, rgba(173, 222, 239, 0.15) 100%);
  border: 2px solid rgba(173, 222, 239, 0.3);
}

.status-dot {
  width: 14px;
  height: 14px;
  border-radius: var(--radius-circle);
  transition: all var(--transition-base);
  box-shadow: 0 0 8px currentColor;
}

.status-indicator--idle .status-dot {
  background-color: var(--color-text-secondary);
  box-shadow: none;
}

.status-indicator--running .status-dot {
  background-color: var(--color-primary-blue);
  animation: pulse 2s ease-in-out infinite;
}

.status-indicator--success .status-dot {
  background-color: var(--color-primary-green);
}

.status-indicator--error .status-dot {
  background-color: #ef5350;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.2);
  }
}

.agent-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-12);
}

.current-task {
  padding: var(--space-14);
  background: linear-gradient(135deg, rgba(165, 231, 165, 0.1) 0%, rgba(173, 222, 239, 0.1) 100%);
  border-radius: var(--radius-medium);
  border: 1px solid rgba(173, 222, 239, 0.2);
}

.progress-bar {
  width: 100%;
  height: 6px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-pill);
  overflow: hidden;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
}

.progress-fill {
  height: 100%;
  background: var(--color-accent-gradient);
  transition: width var(--transition-slow);
  border-radius: var(--radius-pill);
  box-shadow: 0 0 8px rgba(173, 222, 239, 0.5);
}

.agent-message {
  padding-top: var(--space-12);
  border-top: 1px solid rgba(173, 222, 239, 0.15);
}
</style>
