<template>
  <div v-if="hasError" class="error-boundary">
    <div class="error-content">
      <div class="error-icon">
        <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
          <circle cx="32" cy="32" r="28" stroke="currentColor" stroke-width="3"/>
          <path d="M32 20V36M32 44H32.02" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
        </svg>
      </div>
      
      <h2 class="text-product mb-12">出错了</h2>
      <p class="text-body text-secondary mb-32">{{ errorMessage }}</p>
      
      <div v-if="showDetails" class="error-details">
        <pre class="error-stack">{{ errorStack }}</pre>
      </div>
      
      <div class="error-actions">
        <AppleButton variant="primary" @click="handleRetry">
          重试
        </AppleButton>
        <AppleButton variant="ghost" @click="handleReset">
          返回首页
        </AppleButton>
        <AppleButton 
          v-if="!showDetails && errorStack"
          variant="ghost" 
          size="small"
          @click="showDetails = true"
        >
          查看详情
        </AppleButton>
      </div>
    </div>
  </div>
  <slot v-else />
</template>

<script setup>
import { ref, onErrorCaptured } from 'vue'
import AppleButton from './AppleButton.vue'

const emit = defineEmits(['retry', 'reset'])

const hasError = ref(false)
const errorMessage = ref('')
const errorStack = ref('')
const showDetails = ref(false)

onErrorCaptured((err, instance, info) => {
  hasError.value = true
  errorMessage.value = err.message || '发生了未知错误'
  errorStack.value = err.stack || ''
  
  console.error('ErrorBoundary捕获错误:', err, info)
  
  // 阻止错误继续传播
  return false
})

const handleRetry = () => {
  hasError.value = false
  errorMessage.value = ''
  errorStack.value = ''
  showDetails.value = false
  emit('retry')
}

const handleReset = () => {
  hasError.value = false
  errorMessage.value = ''
  errorStack.value = ''
  showDetails.value = false
  emit('reset')
  
  // 刷新页面
  window.location.href = '/'
}

// 暴露方法供外部调用
const captureError = (error) => {
  hasError.value = true
  errorMessage.value = error.message || '发生了未知错误'
  errorStack.value = error.stack || ''
}

defineExpose({
  captureError
})
</script>

<style scoped>
.error-boundary {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-32);
  background-color: var(--color-pale-gray);
}

.error-content {
  max-width: 600px;
  width: 100%;
  text-align: center;
  background-color: var(--color-white);
  padding: var(--space-48);
  border-radius: var(--radius-xlarge);
  box-shadow: var(--shadow-medium);
}

.error-icon {
  color: #ff3b30;
  margin-bottom: var(--space-24);
  display: flex;
  justify-content: center;
}

.error-details {
  margin-bottom: var(--space-32);
  padding: var(--space-20);
  background-color: var(--color-pale-gray);
  border-radius: var(--radius-medium);
  max-height: 300px;
  overflow-y: auto;
  text-align: left;
}

.error-stack {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
  color: var(--color-near-black);
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}

.error-actions {
  display: flex;
  gap: var(--space-12);
  justify-content: center;
  flex-wrap: wrap;
}

@media (max-width: 640px) {
  .error-content {
    padding: var(--space-32);
  }
  
  .error-actions {
    flex-direction: column;
  }
  
  .error-actions button {
    width: 100%;
  }
}
</style>
