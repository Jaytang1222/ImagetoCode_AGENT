<template>
  <AppleCard variant="product" class="config-panel">
    <h3 class="text-utility mb-20">配置参数</h3>
    
    <div class="config-form">
      <!-- 模型提供商选择 -->
      <div class="form-group">
        <label class="form-label">模型提供商</label>
        <select v-model="localConfig.modelProvider" class="apple-select">
          <option value="qwen">阿里云通义千问 (Qwen)</option>
          <option value="openai">OpenAI GPT</option>
          <option value="gemini">Google Gemini</option>
          <option value="doubao">字节跳动豆包 (Doubao)</option>
        </select>
        <p class="helper-text">选择用于图表生成和评估的AI模型</p>
      </div>


      
      <AppleInput
        v-model="localConfig.maxLoops"
        type="number"
        label="最大迭代轮数"
        placeholder="5"
        helperText="系统将最多执行的优化轮数"
        :min="1"
        :max="10"
      />
      
      <AppleInput
        v-model="localConfig.threshold"
        type="number"
        label="验证通过阈值"
        placeholder="0.75"
        helperText="相似度分数达到此值即通过验证（0-1之间）"
        step="0.05"
        :min="0"
        :max="1"
      />
      
      <div class="button-group">
        <AppleButton 
          variant="primary" 
          @click="handleSave"
          :disabled="!isValid"
        >
          保存配置
        </AppleButton>
        <AppleButton 
          variant="ghost" 
          @click="handleReset"
        >
          重置默认
        </AppleButton>
      </div>
    </div>
  </AppleCard>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import AppleCard from './AppleCard.vue'
import AppleInput from './AppleInput.vue'
import AppleButton from './AppleButton.vue'

const props = defineProps({
  config: {
    type: Object,
    default: () => ({
      maxLoops: 5,
      threshold: 0.75,
      modelProvider: 'qwen'
    })
  }
})

const emit = defineEmits(['update:config', 'save'])

const defaultConfig = {
  maxLoops: 5,
  threshold: 0.75,
  modelProvider: 'qwen'
}

const localConfig = ref({ ...props.config })



const isValid = computed(() => {
  const loops = Number(localConfig.value.maxLoops)
  const threshold = Number(localConfig.value.threshold)
  return loops >= 1 && loops <= 10 && threshold >= 0 && threshold <= 1
})

watch(() => props.config, (newConfig) => {
  localConfig.value = { ...newConfig }
}, { deep: true })

const handleSave = () => {
  if (isValid.value) {
    const config = {
      maxLoops: Number(localConfig.value.maxLoops),
      threshold: Number(localConfig.value.threshold),
      modelProvider: localConfig.value.modelProvider || 'qwen'
    }
    emit('update:config', config)
    emit('save', config)
  }
}

const handleReset = () => {
  localConfig.value = { ...defaultConfig }
  emit('update:config', defaultConfig)
}
</script>

<style scoped>
.config-panel {
  height: 100%;
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-24);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-8);
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-primary);
  letter-spacing: -0.01em;
}

.apple-select {
  width: 100%;
  padding: 10px 12px;
  font-size: 15px;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', sans-serif;
  color: var(--color-text-primary);
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  outline: none;
  transition: all 0.2s ease;
  cursor: pointer;
}

.apple-select:hover {
  border-color: var(--color-border-hover);
}

.apple-select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(0, 125, 250, 0.1);
}

.helper-text {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin: 0;
  line-height: 1.4;
}

.button-group {
  display: flex;
  gap: var(--space-12);
  padding-top: var(--space-8);
}

.button-group button {
  flex: 1;
}

@media (max-width: 640px) {
  .button-group {
    flex-direction: column;
  }
  
  .button-group button {
    width: 100%;
  }
}
</style>
