<template>
  <div class="code-viewer">
    <div class="code-header">
      <div class="code-info">
        <span class="text-control font-semibold">{{ filename }}</span>
        <span class="text-micro text-secondary">{{ language }}</span>
      </div>
      <div class="code-actions">
        <AppleButton 
          variant="ghost" 
          size="small"
          @click="copyCode"
        >
          {{ copied ? '已复制' : '复制代码' }}
        </AppleButton>
        <AppleButton 
          variant="ghost" 
          size="small"
          @click="downloadCode"
        >
          下载
        </AppleButton>
      </div>
    </div>
    
    <div class="code-content" ref="codeContainer">
      <div v-if="showLineNumbers" class="line-numbers">
        <span 
          v-for="n in lineCount" 
          :key="n"
          class="line-number"
        >
          {{ n }}
        </span>
      </div>
      <pre class="code-block"><code>{{ code }}</code></pre>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AppleButton from './AppleButton.vue'

const props = defineProps({
  code: {
    type: String,
    required: true
  },
  language: {
    type: String,
    default: 'python'
  },
  filename: {
    type: String,
    default: 'code.py'
  },
  showLineNumbers: {
    type: Boolean,
    default: true
  }
})

const codeContainer = ref(null)
const copied = ref(false)

const lineCount = computed(() => {
  return props.code.split('\n').length
})

const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(props.code)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('复制失败:', err)
  }
}

const downloadCode = () => {
  const blob = new Blob([props.code], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = props.filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.code-viewer {
  background: linear-gradient(135deg, var(--color-graphite-a) 0%, var(--color-graphite-b) 100%);
  border-radius: var(--radius-large);
  overflow: hidden;
  border: 2px solid rgba(173, 222, 239, 0.2);
  box-shadow: var(--shadow-strong);
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-24);
  border-bottom: 2px solid rgba(173, 222, 239, 0.15);
  background: linear-gradient(135deg, rgba(165, 231, 165, 0.08) 0%, rgba(173, 222, 239, 0.08) 100%);
}

.code-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  color: var(--color-white);
}

.code-info .font-semibold {
  color: var(--color-primary-green);
  font-size: 15px;
}

.code-actions {
  display: flex;
  gap: var(--space-12);
}

.code-content {
  display: flex;
  overflow-x: auto;
  max-height: 700px;
  overflow-y: auto;
}

.line-numbers {
  display: flex;
  flex-direction: column;
  padding: var(--space-24) var(--space-14);
  background: linear-gradient(90deg, var(--color-graphite-b) 0%, var(--color-graphite-a) 100%);
  color: var(--color-text-secondary);
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.7;
  user-select: none;
  text-align: right;
  border-right: 2px solid rgba(173, 222, 239, 0.15);
  flex-shrink: 0;
}

.line-number {
  min-width: 45px;
  opacity: 0.6;
  transition: opacity var(--transition-fast);
}

.line-number:hover {
  opacity: 1;
}

.code-block {
  flex: 1;
  margin: 0;
  padding: var(--space-24);
  color: #e8f5e9;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.7;
  overflow-x: auto;
  white-space: pre;
  background: transparent;
}

.code-block code {
  font-family: inherit;
  font-size: inherit;
  line-height: inherit;
  color: inherit;
}

/* 自定义滚动条 */
.code-content::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

.code-content::-webkit-scrollbar-track {
  background: var(--color-graphite-b);
  border-radius: var(--radius-small);
}

.code-content::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, rgba(165, 231, 165, 0.3) 0%, rgba(173, 222, 239, 0.3) 100%);
  border-radius: var(--radius-small);
  border: 2px solid var(--color-graphite-b);
}

.code-content::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, rgba(165, 231, 165, 0.5) 0%, rgba(173, 222, 239, 0.5) 100%);
}

@media (max-width: 640px) {
  .code-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-12);
  }
  
  .code-actions {
    width: 100%;
  }
  
  .code-actions button {
    flex: 1;
  }
  
  .line-numbers {
    padding: var(--space-12) var(--space-8);
  }
  
  .line-number {
    min-width: 30px;
  }
  
  .code-block {
    font-size: 12px;
  }
}
</style>
