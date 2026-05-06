<template>
  <div class="validation-report">
    <div class="report-header">
      <h3 class="text-utility">验证报告</h3>
      <span class="text-control text-secondary">第 {{ currentRound }} 轮</span>
    </div>
    
    <div class="dimensions-grid">
      <div 
        v-for="dimension in dimensionsList"
        :key="dimension.key"
        class="dimension-card"
      >
        <div class="dimension-header">
          <span class="text-control font-semibold">{{ dimension.label }}</span>
          <span class="text-body-emphasis" :class="getScoreClass(dimension.score)">
            {{ formatScore(dimension.score) }}
          </span>
        </div>
        <div class="dimension-bar">
          <div 
            class="dimension-fill"
            :style="{ width: `${dimension.score * 100}%` }"
          ></div>
        </div>
        <p v-if="dimension.description" class="text-micro text-secondary">
          {{ dimension.description }}
        </p>
      </div>
    </div>
    
    <div v-if="reports && reports.length > 0" class="reports-section">
      <h4 class="text-subhead mb-20">详细报告</h4>
      <div class="reports-list">
        <div 
          v-for="(report, index) in reports"
          :key="index"
          class="report-item"
        >
          <div 
            class="report-item-header"
            @click="toggleReport(index)"
          >
            <div class="report-info">
              <span class="text-control font-semibold">{{ report.title }}</span>
              <span class="text-micro text-secondary">{{ report.timestamp }}</span>
            </div>
            <svg 
              class="expand-icon"
              :class="{ 'expanded': expandedReports.includes(index) }"
              width="20" 
              height="20" 
              viewBox="0 0 20 20"
            >
              <path 
                d="M5 7.5L10 12.5L15 7.5" 
                stroke="currentColor" 
                stroke-width="2" 
                stroke-linecap="round" 
                stroke-linejoin="round"
                fill="none"
              />
            </svg>
          </div>
          <div 
            v-if="expandedReports.includes(index)"
            class="report-content"
          >
            <pre class="report-text">{{ report.content }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  dimensions: {
    type: Object,
    default: () => ({
      color: 0,
      text: 0,
      structure: 0,
      vlm: 0
    })
  },
  reports: {
    type: Array,
    default: () => []
  },
  currentRound: {
    type: Number,
    default: 0
  }
})

const expandedReports = ref([])

const dimensionsList = computed(() => [
  {
    key: 'color',
    label: '颜色一致性',
    score: props.dimensions.color || 0,
    description: 'RGB直方图 + 网格色块匹配 + HSV距离'
  },
  {
    key: 'text',
    label: '文本一致性',
    score: props.dimensions.text || 0,
    description: 'OCR + BLEU评分 + 布局偏差'
  },
  {
    key: 'structure',
    label: '结构一致性',
    score: props.dimensions.structure || 0,
    description: 'SSIM + 空间拓扑关系'
  },
  {
    key: 'vlm',
    label: 'VLM感知',
    score: props.dimensions.vlm || 0,
    description: '语义和整体观感补充'
  }
])

const formatScore = (score) => {
  return score ? score.toFixed(4) : '0.0000'
}

const getScoreClass = (score) => {
  if (!score) return 'score-low'
  if (score >= 0.75) return 'score-high'
  if (score >= 0.5) return 'score-medium'
  return 'score-low'
}

const toggleReport = (index) => {
  const idx = expandedReports.value.indexOf(index)
  if (idx > -1) {
    expandedReports.value.splice(idx, 1)
  } else {
    expandedReports.value.push(index)
  }
}
</script>

<style scoped>
.validation-report {
  background-color: var(--color-white);
  border-radius: var(--radius-large);
  padding: var(--space-32);
  border: 1px solid var(--color-soft-border);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-32);
}

.dimensions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-20);
  margin-bottom: var(--space-40);
}

.dimension-card {
  padding: var(--space-20);
  background-color: var(--color-pale-gray);
  border-radius: var(--radius-medium);
}

.dimension-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-12);
}

.dimension-bar {
  width: 100%;
  height: 6px;
  background-color: var(--color-soft-border);
  border-radius: var(--radius-pill);
  overflow: hidden;
  margin-bottom: var(--space-12);
}

.dimension-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff3b30 0%, #ff9500 50%, #34c759 100%);
  border-radius: var(--radius-pill);
  transition: width var(--transition-base);
}

.score-high {
  color: #34c759;
}

.score-medium {
  color: #ff9500;
}

.score-low {
  color: #ff3b30;
}

.reports-section {
  padding-top: var(--space-32);
  border-top: 1px solid var(--color-soft-border);
}

.reports-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-12);
}

.report-item {
  border: 1px solid var(--color-soft-border);
  border-radius: var(--radius-medium);
  overflow: hidden;
}

.report-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-20);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.report-item-header:hover {
  background-color: var(--color-pale-gray);
}

.report-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.expand-icon {
  color: var(--color-secondary-gray);
  transition: transform var(--transition-fast);
  flex-shrink: 0;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.report-content {
  padding: var(--space-20);
  background-color: var(--color-pale-gray);
  border-top: 1px solid var(--color-soft-border);
}

.report-text {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: var(--color-near-black);
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}

@media (max-width: 833px) {
  .dimensions-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .validation-report {
    padding: var(--space-20);
  }
  
  .report-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-8);
  }
}
</style>
