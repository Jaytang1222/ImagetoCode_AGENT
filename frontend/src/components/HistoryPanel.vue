<template>
  <div class="history-panel">
    <div class="history-header">
      <h3 class="text-utility">执行历史</h3>
      <AppleButton 
        v-if="history.length > 0"
        variant="ghost" 
        size="small"
        @click="clearAllHistory"
      >
        清空历史
      </AppleButton>
    </div>
    
    <div v-if="loading" class="history-loading">
      <div class="loading-spinner-small"></div>
      <p class="text-control text-secondary">加载中...</p>
    </div>
    
    <div v-else-if="history.length === 0" class="history-empty">
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
        <path d="M32 8V32L44 44M56 32C56 45.2548 45.2548 56 32 56C18.7452 56 8 45.2548 8 32C8 18.7452 18.7452 8 32 8C45.2548 8 56 18.7452 56 32Z" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <p class="text-body text-secondary">暂无执行历史</p>
    </div>
    
    <div v-else class="history-list">
      <div 
        v-for="item in history"
        :key="item.id"
        :class="['history-item', { 'history-item--selected': selectedId === item.id }]"
        @click="selectHistory(item)"
      >
        <div class="history-item-content">
          <div class="history-info">
            <span class="text-control font-semibold">{{ item.filename }}</span>
            <span class="text-micro text-secondary">{{ formatDate(item.timestamp) }}</span>
          </div>
          
          <div class="history-meta">
            <div class="history-rounds">
              <span class="text-micro text-secondary">轮次:</span>
              <span class="text-control">{{ item.rounds }}</span>
            </div>
            <div class="history-score" :class="getScoreClass(item.score)">
              <span class="text-control font-semibold">{{ formatScore(item.score) }}</span>
            </div>
            <div :class="['history-status', `status--${item.status}`]">
              <span class="text-micro">{{ getStatusText(item.status) }}</span>
            </div>
          </div>
        </div>
        
        <div class="history-actions">
          <button 
            class="action-button"
            @click.stop="viewHistory(item)"
            title="查看详情"
          >
            <svg width="16" height="16" viewBox="0 0 16 16">
              <path d="M1 8C1 8 3.5 3 8 3C12.5 3 15 8 15 8C15 8 12.5 13 8 13C3.5 13 1 8 1 8Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
              <circle cx="8" cy="8" r="2" stroke="currentColor" stroke-width="1.5" fill="none"/>
            </svg>
          </button>
          <button 
            class="action-button"
            @click.stop="downloadHistory(item)"
            title="下载结果"
          >
            <svg width="16" height="16" viewBox="0 0 16 16">
              <path d="M8 2V10M8 10L5 7M8 10L11 7M2 14H14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button 
            class="action-button action-button--danger"
            @click.stop="deleteHistory(item)"
            title="删除"
          >
            <svg width="16" height="16" viewBox="0 0 16 16">
              <path d="M2 4H14M6 4V2H10V4M3 4L4 14H12L13 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppleButton from './AppleButton.vue'

const props = defineProps({
  history: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select', 'view', 'download', 'delete', 'clear', 'refresh'])

const selectedId = ref(null)

const selectHistory = (item) => {
  selectedId.value = item.id
  emit('select', item)
}

const viewHistory = (item) => {
  emit('view', item)
}

const downloadHistory = (item) => {
  emit('download', item)
}

const deleteHistory = (item) => {
  if (confirm(`确定要删除 "${item.filename}" 的执行记录吗？`)) {
    emit('delete', item.id)
  }
}

const clearAllHistory = () => {
  if (confirm('确定要清空所有历史记录吗？此操作不可恢复。')) {
    emit('clear')
  }
}

const formatDate = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  // 小于1分钟
  if (diff < 60000) {
    return '刚刚'
  }
  // 小于1小时
  if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  }
  // 小于24小时
  if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  }
  // 小于7天
  if (diff < 604800000) {
    return `${Math.floor(diff / 86400000)}天前`
  }
  
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatScore = (score) => {
  return score ? score.toFixed(4) : '0.0000'
}

const getScoreClass = (score) => {
  if (!score) return 'score-low'
  if (score >= 0.7) return 'score-high'
  if (score >= 0.5) return 'score-medium'
  return 'score-low'
}

const getStatusText = (status) => {
  const statusMap = {
    completed: '已完成',
    failed: '失败',
    stopped: '已停止',
    running: '运行中'
  }
  return statusMap[status] || status
}

onMounted(() => {
  emit('refresh')
})
</script>

<style scoped>
.history-panel {
  background-color: var(--color-white);
  border-radius: var(--radius-large);
  padding: var(--space-24);
  border: 1px solid var(--color-soft-border);
  max-height: 600px;
  display: flex;
  flex-direction: column;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-20);
  padding-bottom: var(--space-20);
  border-bottom: 1px solid var(--color-soft-border);
}

.history-loading,
.history-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-20);
  padding: var(--space-48);
  color: var(--color-secondary-gray);
}

.loading-spinner-small {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-soft-border);
  border-top-color: var(--color-action-blue);
  border-radius: var(--radius-circle);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.history-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-12);
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-20);
  background-color: var(--color-pale-gray);
  border-radius: var(--radius-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 2px solid transparent;
}

.history-item:hover {
  background-color: rgba(245, 245, 247, 0.8);
  transform: translateX(4px);
}

.history-item--selected {
  border-color: var(--color-action-blue);
  background-color: rgba(0, 113, 227, 0.05);
}

.history-item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-12);
}

.history-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.history-meta {
  display: flex;
  gap: var(--space-20);
  align-items: center;
}

.history-rounds {
  display: flex;
  gap: var(--space-4);
  align-items: center;
}

.history-score {
  padding: var(--space-4) var(--space-8);
  border-radius: var(--radius-small);
}

.score-high {
  background-color: rgba(52, 199, 89, 0.15);
  color: #34c759;
}

.score-medium {
  background-color: rgba(255, 149, 0, 0.15);
  color: #ff9500;
}

.score-low {
  background-color: rgba(255, 59, 48, 0.15);
  color: #ff3b30;
}

.history-status {
  padding: var(--space-4) var(--space-12);
  border-radius: var(--radius-pill);
  font-size: var(--text-micro-size);
}

.status--completed {
  background-color: rgba(52, 199, 89, 0.15);
  color: #34c759;
}

.status--failed {
  background-color: rgba(255, 59, 48, 0.15);
  color: #ff3b30;
}

.status--stopped {
  background-color: rgba(142, 142, 147, 0.15);
  color: var(--color-secondary-gray);
}

.status--running {
  background-color: rgba(0, 113, 227, 0.15);
  color: var(--color-action-blue);
}

.history-actions {
  display: flex;
  gap: var(--space-8);
  flex-shrink: 0;
}

.action-button {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  border-radius: var(--radius-small);
  color: var(--color-secondary-gray);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-button:hover {
  background-color: var(--color-white);
  color: var(--color-near-black);
}

.action-button--danger:hover {
  background-color: rgba(255, 59, 48, 0.1);
  color: #ff3b30;
}

/* 自定义滚动条 */
.history-list::-webkit-scrollbar {
  width: 6px;
}

.history-list::-webkit-scrollbar-track {
  background: transparent;
}

.history-list::-webkit-scrollbar-thumb {
  background: var(--color-soft-border);
  border-radius: var(--radius-pill);
}

.history-list::-webkit-scrollbar-thumb:hover {
  background: var(--color-mid-border);
}

@media (max-width: 640px) {
  .history-panel {
    max-height: 400px;
  }
  
  .history-item {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-12);
  }
  
  .history-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
