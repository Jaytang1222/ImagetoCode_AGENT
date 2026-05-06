<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAgentStore } from '../stores/agentStore'
import AppleButton from '../components/AppleButton.vue'
import TrendChart from '../components/charts/TrendChart.vue'
import RadarChart from '../components/charts/RadarChart.vue'

const router = useRouter()
const store = useAgentStore()

// Mock历史数据用于展示趋势
const mockTrendData = computed(() => {
  if (!store.results.validationScore) return []
  return [
    { score: 0.45 },
    { score: 0.62 },
    { score: 0.71 },
    { score: store.results.validationScore }
  ]
})

const systemStatus = computed(() => {
  if (store.isRunning) return 'Running'
  if (store.pipelineStatus === 'completed') return 'Completed'
  if (store.pipelineStatus === 'failed') return 'Failed'
  return 'Idle'
})

const statusColor = computed(() => {
  const colors = {
    'Running': '#5cb8d9',
    'Completed': '#a5e7a5',
    'Failed': '#ff6b6b',
    'Idle': '#6e7575'
  }
  return colors[systemStatus.value]
})

const latestScore = computed(() => {
  return store.results.validationScore 
    ? (store.results.validationScore * 100).toFixed(1) 
    : '--'
})

const averageScore = computed(() => {
  if (mockTrendData.value.length === 0) return '--'
  const avg = mockTrendData.value.reduce((sum, d) => sum + d.score, 0) / mockTrendData.value.length
  return (avg * 100).toFixed(1)
})

const navigateToExperiments = () => {
  router.push('/experiments')
}

const navigateToVisualization = () => {
  router.push('/visualization')
}
</script>

<template>
  <div class="dashboard">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.5"/>
            <path d="M8 4V8L11 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <span>Real-time AI System</span>
        </div>
        <h1 class="hero-title">Multi-Agent Chart Reproduction</h1>
        <p class="hero-description">
          Transform reference charts into production-ready Matplotlib code using advanced AI collaboration
        </p>
        <div class="hero-actions">
          <AppleButton variant="primary" size="xlarge" @click="navigateToExperiments">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" style="margin-right: 8px;">
              <path d="M6 4L14 10L6 16V4Z" fill="currentColor"/>
            </svg>
            Start New Experiment
          </AppleButton>
          <AppleButton variant="secondary" size="xlarge" @click="navigateToVisualization">
            View Analytics
          </AppleButton>
        </div>
      </div>
    </section>

    <!-- Stats Overview -->
    <section class="stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #a5e7a5 0%, #7dd17d 100%);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="9" stroke="white" stroke-width="2"/>
              <path d="M12 6V12L16 14" stroke="white" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-label">System Status</div>
            <div class="stat-value" :style="{ color: statusColor }">{{ systemStatus }}</div>
            <div class="stat-meta">{{ store.isRunning ? `Round ${store.currentRound}` : 'Ready to start' }}</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #5cb8d9 0%, #4aa8c9 100%);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M3 17L9 11L13 15L21 7" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M16 7H21V12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-label">Latest Score</div>
            <div class="stat-value">{{ latestScore }}%</div>
            <div class="stat-meta">{{ store.results.validationPassed ? 'Validation passed' : 'Last experiment' }}</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #addeef 0%, #7bc9e3 100%);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <rect x="3" y="3" width="18" height="18" rx="2" stroke="white" stroke-width="2"/>
              <path d="M3 9H21M9 3V21" stroke="white" stroke-width="2"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-label">Average Score</div>
            <div class="stat-value">{{ averageScore }}%</div>
            <div class="stat-meta">Across all iterations</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #7dd17d 0%, #5cb8d9 100%);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" stroke="white" stroke-width="2" stroke-linejoin="round"/>
              <path d="M12 12V22M12 12L2 7M12 12L22 7" stroke="white" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-label">Configuration</div>
            <div class="stat-value">{{ store.config.maxLoops }}</div>
            <div class="stat-meta">Max iterations</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Charts Section -->
    <section class="charts-section">
      <div class="section-header">
        <h2 class="section-title">Performance Analytics</h2>
        <p class="section-subtitle">Real-time insights into system performance and quality metrics</p>
      </div>
      
      <div class="charts-grid">
        <div class="chart-wrapper">
          <TrendChart 
            :data="mockTrendData" 
            title="Score Evolution"
            :height="320"
          />
        </div>
        <div class="chart-wrapper">
          <RadarChart 
            :dimensions="store.results.dimensions"
            title="Quality Dimensions"
            :height="320"
          />
        </div>
      </div>
    </section>

    <!-- Quick Actions -->
    <section class="actions-section">
      <div class="action-card primary-action">
        <div class="action-content">
          <h3 class="action-title">Ready to Create?</h3>
          <p class="action-description">Upload a reference chart and let our AI agents generate production-ready code</p>
          <AppleButton variant="primary" size="large" @click="navigateToExperiments">
            Start Experiment
          </AppleButton>
        </div>
        <div class="action-visual">
          <svg width="200" height="160" viewBox="0 0 200 160" fill="none">
            <rect x="20" y="20" width="160" height="120" rx="8" fill="url(#action-gradient)" opacity="0.1"/>
            <path d="M40 100L70 70L100 85L130 50L160 65" stroke="url(#action-gradient)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="70" cy="70" r="6" fill="#a5e7a5"/>
            <circle cx="100" cy="85" r="6" fill="#addeef"/>
            <circle cx="130" cy="50" r="6" fill="#5cb8d9"/>
            <defs>
              <linearGradient id="action-gradient" x1="0" y1="0" x2="200" y2="160">
                <stop offset="0%" stop-color="#a5e7a5"/>
                <stop offset="100%" stop-color="#addeef"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.dashboard {
  min-height: calc(100vh - 64px);
  background: linear-gradient(180deg, #f8faf9 0%, #ffffff 100%);
}

/* Hero Section */
.hero-section {
  padding: var(--space-80) var(--space-32) var(--space-64);
  text-align: center;
}

.hero-content {
  max-width: 900px;
  margin: 0 auto;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-8);
  padding: var(--space-8) var(--space-20);
  background: var(--color-accent-gradient);
  border-radius: var(--radius-pill);
  margin-bottom: var(--space-32);
  font-size: var(--text-control-size);
  font-weight: 600;
  color: var(--color-graphite-a);
  letter-spacing: 0.5px;
}

.hero-title {
  font-size: var(--text-hero-l-size);
  font-weight: 600;
  line-height: var(--text-hero-l-line);
  letter-spacing: var(--text-hero-l-spacing);
  color: var(--color-text-primary);
  margin-bottom: var(--space-24);
  background: linear-gradient(135deg, #1a2f2f 0%, #264040 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 18px;
  line-height: 1.6;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-40);
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: var(--space-20);
}

/* Stats Section */
.stats-section {
  padding: 0 var(--space-32) var(--space-64);
  max-width: 1440px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-24);
}

.stat-card {
  display: flex;
  gap: var(--space-20);
  padding: var(--space-32);
  background: var(--color-surface-light);
  border-radius: var(--radius-large);
  border: 1px solid var(--color-soft-border);
  box-shadow: var(--shadow-subtle);
  transition: all var(--transition-base);
}

.stat-card:hover {
  box-shadow: var(--shadow-medium);
  transform: translateY(-2px);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-medium);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  flex: 1;
}

.stat-label {
  font-size: var(--text-micro-size);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.stat-value {
  font-size: var(--text-promo-size);
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.2;
}

.stat-meta {
  font-size: var(--text-micro-size);
  color: var(--color-text-secondary);
}

/* Charts Section */
.charts-section {
  padding: 0 var(--space-32) var(--space-64);
  max-width: 1440px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: var(--space-48);
}

.section-title {
  font-size: var(--text-section-size);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-12);
}

.section-subtitle {
  font-size: 17px;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-32);
}

.chart-wrapper {
  min-height: 400px;
}

/* Actions Section */
.actions-section {
  padding: 0 var(--space-32) var(--space-80);
  max-width: 1440px;
  margin: 0 auto;
}

.action-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-48);
  background: linear-gradient(135deg, rgba(165, 231, 165, 0.1) 0%, rgba(173, 222, 239, 0.1) 100%);
  border-radius: var(--radius-xlarge);
  border: 2px solid var(--color-soft-border);
  gap: var(--space-48);
}

.action-content {
  flex: 1;
  max-width: 500px;
}

.action-title {
  font-size: var(--text-product-size);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-16);
}

.action-description {
  font-size: 17px;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin-bottom: var(--space-32);
}

.action-visual {
  flex-shrink: 0;
}

/* Responsive */
@media (max-width: 1279px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1023px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }

  .action-card {
    flex-direction: column;
    text-align: center;
  }

  .action-content {
    max-width: 100%;
  }
}

@media (max-width: 640px) {
  .hero-section {
    padding: var(--space-48) var(--space-20) var(--space-40);
  }

  .hero-actions {
    flex-direction: column;
    width: 100%;
  }

  .hero-actions button {
    width: 100%;
  }

  .stats-section,
  .charts-section,
  .actions-section {
    padding-left: var(--space-20);
    padding-right: var(--space-20);
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: var(--space-16);
  }

  .stat-card {
    padding: var(--space-24);
  }

  .action-card {
    padding: var(--space-32);
  }

  .action-visual {
    display: none;
  }
}
</style>
