<script setup>
import { computed } from 'vue'
import { useAgentStore } from '../stores/agentStore'
import TrendChart from '../components/charts/TrendChart.vue'
import RadarChart from '../components/charts/RadarChart.vue'
import ProgressIndicator from '../components/ProgressIndicator.vue'

const store = useAgentStore()

// Mock数据用于展示
const mockIterationData = computed(() => {
  const data = []
  for (let i = 1; i <= store.currentRound; i++) {
    data.push({
      score: Math.min(0.4 + (i * 0.12) + (Math.random() * 0.05), 0.95)
    })
  }
  if (store.results.validationScore && data.length > 0) {
    data[data.length - 1].score = store.results.validationScore
  }
  return data
})

const dimensionScores = computed(() => {
  const dims = store.results.dimensions
  return [
    { name: 'Color Consistency', value: dims.color, color: '#a5e7a5' },
    { name: 'Text Accuracy', value: dims.text, color: '#addeef' },
    { name: 'Structure Match', value: dims.structure, color: '#5cb8d9' },
    { name: 'Visual Similarity', value: dims.vlm, color: '#7dd17d' }
  ]
})

const hasData = computed(() => {
  return store.results.validationScore !== null || store.currentRound > 0
})
</script>

<template>
  <div class="visualization">
    <!-- Page Header -->
    <section class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">Visualization & Analytics</h1>
          <p class="page-subtitle">Deep insights into experiment performance and quality metrics</p>
        </div>
      </div>
    </section>

    <!-- Main Content -->
    <div v-if="hasData" class="content-wrapper">
      <!-- Progress Overview -->
      <section class="progress-section">
        <div class="section-container">
          <div class="progress-card">
            <div class="progress-header">
              <h2 class="progress-title">Execution Progress</h2>
              <div class="progress-stats">
                <span class="stat-item">
                  <span class="stat-label">Round:</span>
                  <span class="stat-value">{{ store.currentRound }} / {{ store.config.maxLoops }}</span>
                </span>
                <span class="stat-item">
                  <span class="stat-label">Status:</span>
                  <span class="stat-value" :class="store.pipelineStatus">{{ store.pipelineStatus }}</span>
                </span>
              </div>
            </div>
            <ProgressIndicator 
              :current-round="store.currentRound"
              :max-rounds="store.config.maxLoops"
              :status="store.pipelineStatus"
            />
          </div>
        </div>
      </section>

      <!-- Charts Grid -->
      <section class="charts-section">
        <div class="section-container">
          <div class="charts-grid">
            <!-- Trend Chart -->
            <div class="chart-card full-width">
              <TrendChart 
                :data="mockIterationData" 
                title="Iteration Score Trend"
                :height="400"
              />
            </div>

            <!-- Radar Chart -->
            <div class="chart-card">
              <RadarChart 
                :dimensions="store.results.dimensions"
                title="Multi-Dimensional Quality Analysis"
                :height="400"
              />
            </div>

            <!-- Dimension Breakdown -->
            <div class="chart-card">
              <div class="dimension-breakdown">
                <div class="breakdown-header">
                  <h3 class="breakdown-title">Dimension Scores</h3>
                  <p class="breakdown-subtitle">Individual metric performance</p>
                </div>
                <div class="dimension-list">
                  <div 
                    v-for="dim in dimensionScores" 
                    :key="dim.name"
                    class="dimension-item"
                  >
                    <div class="dimension-info">
                      <span class="dimension-name">{{ dim.name }}</span>
                      <span class="dimension-value">{{ (dim.value * 100).toFixed(1) }}%</span>
                    </div>
                    <div class="dimension-bar">
                      <div 
                        class="dimension-fill" 
                        :style="{ 
                          width: `${dim.value * 100}%`,
                          background: dim.color
                        }"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Agent Performance -->
      <section class="agents-section">
        <div class="section-container">
          <div class="section-header">
            <h2 class="section-title">Agent Performance</h2>
            <p class="section-subtitle">Individual agent status and contributions</p>
          </div>
          <div class="agents-grid">
            <div 
              v-for="agent in store.agents" 
              :key="agent.id"
              class="agent-card"
              :class="agent.status"
            >
              <div class="agent-header">
                <div class="agent-icon" :class="agent.status">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                  </svg>
                </div>
                <div class="agent-info">
                  <h3 class="agent-title">{{ agent.title }}</h3>
                  <p class="agent-description">{{ agent.description }}</p>
                </div>
              </div>
              <div class="agent-status">
                <span class="status-badge" :class="agent.status">{{ agent.status }}</span>
              </div>
              <div v-if="agent.currentTask" class="agent-task">
                <span class="task-label">Current Task:</span>
                <span class="task-text">{{ agent.currentTask }}</span>
              </div>
              <div v-if="agent.progress !== null" class="agent-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: `${agent.progress}%` }"></div>
                </div>
                <span class="progress-text">{{ agent.progress }}%</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Empty State -->
    <section v-else class="empty-state">
      <div class="empty-content">
        <div class="empty-icon">
          <svg width="120" height="120" viewBox="0 0 120 120" fill="none">
            <path d="M20 80L40 60L60 70L100 30" stroke="#d8e5e5" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="40" cy="60" r="8" fill="#addeef"/>
            <circle cx="60" cy="70" r="8" fill="#a5e7a5"/>
            <circle cx="100" cy="30" r="8" fill="#5cb8d9"/>
          </svg>
        </div>
        <h3 class="empty-title">No Data Available</h3>
        <p class="empty-description">Run an experiment to see visualization and analytics</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.visualization {
  min-height: calc(100vh - 64px);
  background: linear-gradient(180deg, #f8faf9 0%, #ffffff 100%);
}

/* Page Header */
.page-header {
  padding: var(--space-48) var(--space-32) var(--space-32);
  border-bottom: 1px solid var(--color-soft-border);
  background: var(--color-surface-light);
}

.header-content {
  max-width: 1440px;
  margin: 0 auto;
}

.page-title {
  font-size: var(--text-section-size);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-8);
}

.page-subtitle {
  font-size: 17px;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

/* Content Wrapper */
.content-wrapper {
  padding-bottom: var(--space-64);
}

/* Progress Section */
.progress-section {
  padding: var(--space-48) var(--space-32);
}

.section-container {
  max-width: 1440px;
  margin: 0 auto;
}

.progress-card {
  background: var(--color-surface-light);
  border-radius: var(--radius-large);
  padding: var(--space-32);
  border: 1px solid var(--color-soft-border);
  box-shadow: var(--shadow-medium);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-32);
  padding-bottom: var(--space-20);
  border-bottom: 1px solid var(--color-soft-border);
}

.progress-title {
  font-size: var(--text-utility-size);
  font-weight: 600;
  color: var(--color-text-primary);
}

.progress-stats {
  display: flex;
  gap: var(--space-32);
}

.stat-item {
  display: flex;
  gap: var(--space-8);
  align-items: center;
}

.stat-label {
  font-size: var(--text-control-size);
  color: var(--color-text-secondary);
}

.stat-value {
  font-size: var(--text-control-size);
  font-weight: 600;
  color: var(--color-text-primary);
}

.stat-value.running {
  color: var(--color-action-blue);
}

.stat-value.completed {
  color: var(--color-success-green);
}

.stat-value.failed {
  color: #ff6b6b;
}

/* Charts Section */
.charts-section {
  padding: 0 var(--space-32) var(--space-48);
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-32);
}

.chart-card {
  min-height: 450px;
}

.chart-card.full-width {
  grid-column: 1 / -1;
}

/* Dimension Breakdown */
.dimension-breakdown {
  background: var(--color-surface-light);
  border-radius: var(--radius-large);
  padding: var(--space-24);
  border: 1px solid var(--color-soft-border);
  box-shadow: var(--shadow-subtle);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.breakdown-header {
  margin-bottom: var(--space-24);
  padding-bottom: var(--space-12);
  border-bottom: 1px solid var(--color-soft-border);
}

.breakdown-title {
  font-size: var(--text-subhead-size);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-4);
}

.breakdown-subtitle {
  font-size: var(--text-micro-size);
  color: var(--color-text-secondary);
}

.dimension-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-24);
  flex: 1;
}

.dimension-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-8);
}

.dimension-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dimension-name {
  font-size: var(--text-control-size);
  font-weight: 500;
  color: var(--color-text-primary);
}

.dimension-value {
  font-size: var(--text-control-size);
  font-weight: 700;
  color: var(--color-action-blue);
}

.dimension-bar {
  height: 8px;
  background: rgba(216, 229, 229, 0.3);
  border-radius: 4px;
  overflow: hidden;
}

.dimension-fill {
  height: 100%;
  border-radius: 4px;
  transition: width var(--transition-base);
}

/* Agents Section */
.agents-section {
  padding: 0 var(--space-32) var(--space-48);
}

.section-header {
  text-align: center;
  margin-bottom: var(--space-40);
}

.section-title {
  font-size: var(--text-product-size);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-8);
}

.section-subtitle {
  font-size: 17px;
  color: var(--color-text-secondary);
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-24);
}

.agent-card {
  background: var(--color-surface-light);
  border-radius: var(--radius-large);
  padding: var(--space-24);
  border: 2px solid var(--color-soft-border);
  box-shadow: var(--shadow-subtle);
  transition: all var(--transition-base);
}

.agent-card:hover {
  box-shadow: var(--shadow-medium);
  transform: translateY(-2px);
}

.agent-card.running {
  border-color: var(--color-action-blue);
  box-shadow: 0 0 0 3px rgba(92, 184, 217, 0.1);
}

.agent-header {
  display: flex;
  gap: var(--space-16);
  margin-bottom: var(--space-16);
}

.agent-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-medium);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface-accent);
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.agent-icon.running {
  background: rgba(92, 184, 217, 0.1);
  color: var(--color-action-blue);
}

.agent-icon.completed {
  background: rgba(165, 231, 165, 0.1);
  color: var(--color-primary-green-dark);
}

.agent-info {
  flex: 1;
}

.agent-title {
  font-size: var(--text-subhead-size);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-4);
}

.agent-description {
  font-size: var(--text-micro-size);
  color: var(--color-text-secondary);
}

.agent-status {
  margin-bottom: var(--space-12);
}

.status-badge {
  display: inline-flex;
  padding: var(--space-4) var(--space-12);
  border-radius: var(--radius-pill);
  font-size: var(--text-micro-size);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.idle {
  background: rgba(216, 229, 229, 0.3);
  color: var(--color-text-secondary);
}

.status-badge.running {
  background: rgba(92, 184, 217, 0.2);
  color: var(--color-link-blue);
}

.status-badge.completed {
  background: rgba(165, 231, 165, 0.2);
  color: var(--color-primary-green-dark);
}

.agent-task {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  margin-bottom: var(--space-12);
  padding: var(--space-12);
  background: var(--color-surface-accent);
  border-radius: var(--radius-small);
}

.task-label {
  font-size: var(--text-micro-size);
  color: var(--color-text-secondary);
  font-weight: 600;
}

.task-text {
  font-size: var(--text-control-size);
  color: var(--color-text-primary);
}

.agent-progress {
  display: flex;
  align-items: center;
  gap: var(--space-12);
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: rgba(216, 229, 229, 0.3);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #5cb8d9;
  border-radius: 3px;
  transition: width var(--transition-base);
}

.progress-text {
  font-size: var(--text-micro-size);
  font-weight: 600;
  color: var(--color-text-secondary);
  min-width: 40px;
  text-align: right;
}

/* Empty State */
.empty-state {
  padding: var(--space-80) var(--space-32);
}

.empty-content {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-24);
}

.empty-title {
  font-size: var(--text-promo-size);
  font-weight: 600;
  color: var(--color-text-primary);
}

.empty-description {
  font-size: 17px;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

/* Responsive */
@media (max-width: 1279px) {
  .agents-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1023px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }

  .progress-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-16);
  }
}

@media (max-width: 640px) {
  .page-header,
  .progress-section,
  .charts-section,
  .agents-section {
    padding-left: var(--space-20);
    padding-right: var(--space-20);
  }

  .agents-grid {
    grid-template-columns: 1fr;
  }

  .progress-stats {
    flex-direction: column;
    gap: var(--space-12);
    width: 100%;
  }
}
</style>
