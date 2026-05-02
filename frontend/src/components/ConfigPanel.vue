<template>
  <AppleCard variant="product" class="config-panel">
    <h3 class="text-utility mb-20">配置参数</h3>
    
    <div class="config-form">
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
      
      <div class="switch-group">
        <label class="switch-label">
          <input
            v-model="localConfig.strictMode"
            type="checkbox"
            class="switch-input"
          />
          <span class="switch-slider"></span>
          <span class="switch-text">
            <span class="text-control font-semibold">严格算法模式</span>
            <span class="text-micro text-secondary">启用完整的Agent分发流程</span>
          </span>
        </label>
      </div>
      
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
      strictMode: true
    })
  }
})

const emit = defineEmits(['update:config', 'save'])

const defaultConfig = {
  maxLoops: 5,
  threshold: 0.75,
  strictMode: true
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
      strictMode: localConfig.value.strictMode
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

.switch-group {
  padding: var(--space-24);
  background: linear-gradient(135deg, rgba(165, 231, 165, 0.08) 0%, rgba(173, 222, 239, 0.08) 100%);
  border-radius: var(--radius-medium);
  border: 1px solid rgba(173, 222, 239, 0.2);
}

.switch-label {
  display: flex;
  align-items: center;
  gap: var(--space-12);
  cursor: pointer;
}

.switch-input {
  display: none;
}

.switch-slider {
  position: relative;
  width: 52px;
  height: 30px;
  background-color: var(--color-soft-border);
  border-radius: var(--radius-pill);
  transition: background-color var(--transition-base);
  flex-shrink: 0;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.switch-slider::before {
  content: '';
  position: absolute;
  width: 26px;
  height: 26px;
  left: 2px;
  top: 2px;
  background-color: var(--color-white);
  border-radius: var(--radius-circle);
  transition: transform var(--transition-base);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.switch-input:checked + .switch-slider {
  background: var(--color-accent-gradient);
}

.switch-input:checked + .switch-slider::before {
  transform: translateX(22px);
}

.switch-text {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
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
