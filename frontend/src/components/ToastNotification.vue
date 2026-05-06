<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="['toast', `toast--${toast.type}`]"
        >
          <div class="toast-icon">
            <svg v-if="toast.type === 'success'" width="20" height="20" viewBox="0 0 20 20">
              <path d="M7 10L9 12L13 8M19 10C19 14.9706 14.9706 19 10 19C5.02944 19 1 14.9706 1 10C1 5.02944 5.02944 1 10 1C14.9706 1 19 5.02944 19 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            </svg>
            <svg v-else-if="toast.type === 'error'" width="20" height="20" viewBox="0 0 20 20">
              <path d="M13 7L7 13M7 7L13 13M19 10C19 14.9706 14.9706 19 10 19C5.02944 19 1 14.9706 1 10C1 5.02944 5.02944 1 10 1C14.9706 1 19 5.02944 19 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            </svg>
            <svg v-else-if="toast.type === 'warning'" width="20" height="20" viewBox="0 0 20 20">
              <path d="M10 7V11M10 14H10.01M19 10C19 14.9706 14.9706 19 10 19C5.02944 19 1 14.9706 1 10C1 5.02944 5.02944 1 10 1C14.9706 1 19 5.02944 19 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 20 20">
              <path d="M10 11V7M10 14H10.01M19 10C19 14.9706 14.9706 19 10 19C5.02944 19 1 14.9706 1 10C1 5.02944 5.02944 1 10 1C14.9706 1 19 5.02944 19 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            </svg>
          </div>
          <div class="toast-content">
            <p class="toast-message text-control">{{ toast.message }}</p>
          </div>
          <button 
            class="toast-close"
            @click="removeToast(toast.id)"
          >
            <svg width="16" height="16" viewBox="0 0 16 16">
              <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const toasts = ref([])
let toastId = 0

const addToast = (message, type = 'info', duration = 3000) => {
  const id = toastId++
  toasts.value.push({ id, message, type })
  
  if (duration > 0) {
    setTimeout(() => {
      removeToast(id)
    }, duration)
  }
  
  return id
}

const removeToast = (id) => {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

defineExpose({
  addToast,
  removeToast,
  success: (message, duration) => addToast(message, 'success', duration),
  error: (message, duration) => addToast(message, 'error', duration),
  warning: (message, duration) => addToast(message, 'warning', duration),
  info: (message, duration) => addToast(message, 'info', duration)
})
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: var(--space-20);
  right: var(--space-20);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: var(--space-12);
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: var(--space-12);
  min-width: 320px;
  max-width: 480px;
  padding: var(--space-20);
  background-color: var(--color-white);
  border-radius: var(--radius-medium);
  box-shadow: var(--shadow-strong);
  pointer-events: auto;
  border-left: 4px solid;
}

.toast--success {
  border-left-color: #34c759;
}

.toast--error {
  border-left-color: #ff3b30;
}

.toast--warning {
  border-left-color: #ff9500;
}

.toast--info {
  border-left-color: var(--color-action-blue);
}

.toast-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast--success .toast-icon {
  color: #34c759;
}

.toast--error .toast-icon {
  color: #ff3b30;
}

.toast--warning .toast-icon {
  color: #ff9500;
}

.toast--info .toast-icon {
  color: var(--color-action-blue);
}

.toast-content {
  flex: 1;
}

.toast-message {
  color: var(--color-near-black);
  margin: 0;
}

.toast-close {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-secondary-gray);
  background: none;
  border: none;
  cursor: pointer;
  border-radius: var(--radius-small);
  transition: all var(--transition-fast);
}

.toast-close:hover {
  background-color: var(--color-pale-gray);
  color: var(--color-near-black);
}

/* Toast动画 */
.toast-enter-active,
.toast-leave-active {
  transition: all var(--transition-base);
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

@media (max-width: 640px) {
  .toast-container {
    top: var(--space-12);
    right: var(--space-12);
    left: var(--space-12);
  }
  
  .toast {
    min-width: auto;
    max-width: none;
  }
}
</style>
