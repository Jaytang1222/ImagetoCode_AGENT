<template>
  <div class="comparison-view">
    <div class="comparison-grid">
      <div class="image-container">
        <div class="image-label">
          <span class="text-control text-secondary">原始图表</span>
        </div>
        <div class="image-wrapper">
          <img v-if="originalImage" :src="originalImage" alt="原始图表" />
          <div v-else class="image-placeholder">
            <p class="text-body text-secondary">暂无图片</p>
          </div>
        </div>
      </div>
      
      <div class="image-container">
        <div class="image-label">
          <span class="text-control text-secondary">生成图表</span>
        </div>
        <div class="image-wrapper">
          <img v-if="generatedImage" :src="generatedImage" alt="生成图表" />
          <div v-else class="image-placeholder">
            <p class="text-body text-secondary">等待生成</p>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="score !== null" class="score-display">
      <div class="score-content">
        <p class="text-subhead text-secondary mb-12">相似度分数</p>
        <div class="score-value">
          <span class="text-hero-xl" :class="scoreColorClass">{{ formattedScore }}</span>
          <span class="text-body text-secondary">/ 1.00</span>
        </div>
        <div class="score-bar">
          <div class="score-fill" :style="{ width: `${score * 100}%` }"></div>
        </div>
        <p v-if="passed !== null" class="score-status text-body-emphasis" :class="passed ? 'status-success' : 'status-failed'">
          {{ passed ? '✓ 验证通过' : '✗ 未通过验证' }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  originalImage: {
    type: String,
    default: null
  },
  generatedImage: {
    type: String,
    default: null
  },
  score: {
    type: Number,
    default: null
  },
  passed: {
    type: Boolean,
    default: null
  }
})

const formattedScore = computed(() => {
  return props.score !== null ? props.score.toFixed(4) : '0.0000'
})

const scoreColorClass = computed(() => {
  if (props.score === null) return ''
  if (props.score >= 0.75) return 'score-high'
  if (props.score >= 0.5) return 'score-medium'
  return 'score-low'
})
</script>

<style scoped>
.comparison-view {
  width: 100%;
}

.comparison-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-40);
  margin-bottom: var(--space-56);
}

.image-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-14);
}

.image-label {
  text-align: center;
  padding: var(--space-8) var(--space-20);
  background: rgba(165, 231, 165, 0.15);
  border-radius: var(--radius-medium);
  border: 1px solid rgba(165, 231, 165, 0.3);
}

.image-label span {
  font-weight: 600;
  color: var(--color-primary-green);
}

.image-wrapper {
  background: linear-gradient(135deg, var(--color-graphite-a) 0%, var(--color-graphite-b) 100%);
  border-radius: var(--radius-large);
  overflow: hidden;
  aspect-ratio: 16 / 9;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(173, 222, 239, 0.2);
  box-shadow: var(--shadow-medium);
  transition: all var(--transition-base);
}

.image-wrapper:hover {
  border-color: rgba(173, 222, 239, 0.4);
  box-shadow: var(--shadow-strong);
  transform: translateY(-2px);
}

.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.score-display {
  display: flex;
  justify-content: center;
  padding: var(--space-40);
  background: linear-gradient(135deg, rgba(165, 231, 165, 0.08) 0%, rgba(173, 222, 239, 0.08) 100%);
  border-radius: var(--radius-large);
  border: 2px solid rgba(173, 222, 239, 0.2);
  box-shadow: var(--shadow-subtle);
}

.score-content {
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.score-value {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: var(--space-14);
  margin-bottom: var(--space-24);
}

.score-high {
  color: var(--color-primary-green);
  filter: drop-shadow(0 2px 8px rgba(165, 231, 165, 0.4));
}

.score-medium {
  color: #ffa726;
  filter: drop-shadow(0 2px 8px rgba(255, 167, 38, 0.4));
}

.score-low {
  color: #ef5350;
  filter: drop-shadow(0 2px 8px rgba(239, 83, 80, 0.4));
}

.score-bar {
  width: 100%;
  height: 10px;
  background: var(--color-surface-accent);
  border-radius: var(--radius-pill);
  overflow: hidden;
  margin-bottom: var(--space-24);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #ef5350 0%, #ffa726 50%, var(--color-primary-green) 100%);
  border-radius: var(--radius-pill);
  transition: width var(--transition-slow);
  box-shadow: 0 0 10px rgba(165, 231, 165, 0.5);
}

.score-status {
  padding: var(--space-14) var(--space-32);
  border-radius: var(--radius-medium);
  display: inline-block;
  font-weight: 600;
  box-shadow: var(--shadow-subtle);
}

.status-success {
  background: linear-gradient(135deg, rgba(165, 231, 165, 0.2) 0%, rgba(165, 231, 165, 0.3) 100%);
  color: var(--color-primary-green-dark);
  border: 2px solid var(--color-primary-green);
}

.status-failed {
  background: linear-gradient(135deg, rgba(239, 83, 80, 0.2) 0%, rgba(239, 83, 80, 0.3) 100%);
  color: #d32f2f;
  border: 2px solid #ef5350;
}

@media (max-width: 833px) {
  .comparison-grid {
    grid-template-columns: 1fr;
    gap: var(--space-24);
  }
}
</style>
