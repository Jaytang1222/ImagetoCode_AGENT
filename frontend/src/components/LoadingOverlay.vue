<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="visible" class="loading-overlay" @click="handleOverlayClick">
        <div class="loading-content" @click.stop>
          <div class="loading-spinner">
            <svg class="spinner" viewBox="0 0 50 50">
              <circle
                class="spinner-path"
                cx="25"
                cy="25"
                r="20"
                fill="none"
                stroke-width="4"
              ></circle>
            </svg>
          </div>
          <p v-if="message" class="loading-message text-body">{{ message }}</p>
          <AppleButton 
            v-if="cancellable"
            variant="ghost"
            size="small"
            @click="handleCancel"
          >
            取消
          </AppleButton>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import AppleButton from './AppleButton.vue'

defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  message: {
    type: String,
    default: ''
  },
  cancellable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['cancel'])

const handleCancel = () => {
  emit('cancel')
}

const handleOverlayClick = () => {
  // 点击遮罩层不做任何操作，防止误触
}
</script>

<style scoped>
.loading-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  z-index: 9998;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-24);
  padding: var(--space-48);
  background-color: var(--color-white);
  border-radius: var(--radius-xlarge);
  box-shadow: var(--shadow-strong);
  max-width: 400px;
}

.loading-spinner {
  width: 64px;
  height: 64px;
}

.spinner {
  animation: rotate 2s linear infinite;
  width: 100%;
  height: 100%;
}

.spinner-path {
  stroke: var(--color-action-blue);
  stroke-linecap: round;
  animation: dash 1.5s ease-in-out infinite;
}

@keyframes rotate {
  100% {
    transform: rotate(360deg);
  }
}

@keyframes dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}

.loading-message {
  color: var(--color-near-black);
  text-align: center;
  max-width: 300px;
}

/* Overlay动画 */
.overlay-enter-active,
.overlay-leave-active {
  transition: all var(--transition-base);
}

.overlay-enter-from,
.overlay-leave-to {
  opacity: 0;
}

.overlay-enter-from .loading-content,
.overlay-leave-to .loading-content {
  transform: scale(0.9);
  opacity: 0;
}

@media (max-width: 640px) {
  .loading-content {
    padding: var(--space-32);
    margin: var(--space-20);
  }
}
</style>
