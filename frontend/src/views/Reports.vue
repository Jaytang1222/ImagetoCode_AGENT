<script setup>
import { ref, computed } from 'vue'
import { useAgentStore } from '../stores/agentStore'
import { useHistory } from '../composables/useHistory'
import CodeViewer from '../components/CodeViewer.vue'
import ValidationReport from '../components/ValidationReport.vue'
import AppleButton from '../components/AppleButton.vue'
import ToastNotification from '../components/ToastNotification.vue'

const store = useAgentStore()
const historyManager = useHistory()
const toast = ref(null)

const downloadCode = async () => {
  if (!store.results.generatedCode) {
    toast.value?.warning('No code available to download')
    return
  }
  
  try {
    const blob = new Blob([store.results.generatedCode], { type: 'text/plain' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'generated_chart.py'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    toast.value?.success('Code downloaded successfully')
  } catch (error) {
    toast.value?.error('Failed to download code')
  }
}

const downloadReport = async () => {
  if (!store.results.reports || store.results.reports.length === 0) {
    toast.value?.warning('No report available to download')
    return
  }
  
  try {
    const reportText = store.results.reports.join('\n\n')
    const blob = new Blob([reportText], { type: 'text/plain' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'validation_report.txt'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    toast.value?.success('Report downloaded successfully')
  } catch (error) {
    toast.value?.error('Failed to download report')
  }
}

const hasResults = computed(() => {
  return store.results.generatedCode || store.results.reports.length > 0
})
</script>

<template>
  <div class="reports">
    <ToastNotification ref="toast" />

    <!-- Page Header -->
    <section class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">Code & Reports</h1>
          <p class="page-subtitle">Generated code and detailed validation reports</p>
        </div>
        <div v-if="hasResults" class="header-actions">
          <AppleButton variant="secondary" @click="downloadCode">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" style="margin-right: 6px;">
              <path d="M9 2V12M9 12L5 8M9 12L13 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M2 12V14C2 15.1 2.9 16 4 16H14C15.1 16 16 15.1 16 14V12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            Download Code
          </AppleButton>
          <AppleButton variant="secondary" @click="downloadReport">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" style="margin-right: 6px;">
              <path d="M4 2H10L14 6V14C14 15.1 13.1 16 12 16H4C2.9 16 2 15.1 2 14V4C2 2.9 2.9 2 4 2Z" stroke="currentColor" stroke-width="2"/>
              <path d="M10 2V6H14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            Download Report
          </AppleButton>
        </div>
      </div>
    </section>

    <!-- Main Content -->
    <div v-if="hasResults" class="content-wrapper">
      <!-- Code Section -->
      <section v-if="store.results.generatedCode" class="code-section">
        <div class="section-container">
          <div class="section-header">
            <div class="header-left">
              <h2 class="section-title">Generated Code</h2>
              <p class="section-subtitle">Production-ready Matplotlib Python code</p>
            </div>
            <div class="code-meta">
              <div class="meta-item">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/>
                  <path d="M8 4V8L11 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                <span>Round {{ store.currentRound }}</span>
              </div>
              <div class="meta-item">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M2 4H14M2 8H14M2 12H14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                <span>{{ store.results.generatedCode.split('\n').length }} lines</span>
              </div>
            </div>
          </div>
          <CodeViewer
            :code="store.results.generatedCode"
            language="python"
            filename="generated_chart.py"
          />
        </div>
      </section>

      <!-- Validation Report Section -->
      <section v-if="store.results.reports.length > 0" class="validation-section">
        <div class="section-container">
          <div class="section-header">
            <div class="header-left">
              <h2 class="section-title">Validation Report</h2>
              <p class="section-subtitle">Detailed quality assessment across multiple dimensions</p>
            </div>
            <div v-if="store.results.validationScore !== null" class="score-badge" :class="{ passed: store.results.validationPassed }">
              <span class="score-label">Overall Score</span>
              <span class="score-value">{{ (store.results.validationScore * 100).toFixed(1) }}%</span>
            </div>
          </div>
          <ValidationReport
            :dimensions="store.results.dimensions"
            :reports="store.results.reports"
            :current-round="store.currentRound"
          />
        </div>
      </section>

      <!-- Summary Section -->
      <section class="summary-section">
        <div class="section-container">
          <div class="summary-card">
            <div class="summary-header">
              <h3 class="summary-title">Experiment Summary</h3>
            </div>
            <div class="summary-grid">
              <div class="summary-item">
                <span class="summary-label">Status</span>
                <span class="summary-value" :class="store.pipelineStatus">
                  {{ store.pipelineStatus }}
                </span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Iterations</span>
                <span class="summary-value">{{ store.currentRound }} / {{ store.config.maxLoops }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Validation</span>
                <span class="summary-value" :class="{ passed: store.results.validationPassed }">
                  {{ store.results.validationPassed ? 'Passed' : 'Not Passed' }}
                </span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Model Provider</span>
                <span class="summary-value">{{ store.config.modelProvider }}</span>
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
            <rect x="30" y="20" width="60" height="80" rx="4" stroke="#d8e5e5" stroke-width="3"/>
            <path d="M45 35H75M45 50H75M45 65H60" stroke="#addeef" stroke-width="3" stroke-linecap="round"/>
            <circle cx="85" cy="85" r="20" fill="rgba(165, 231, 165, 0.2)" stroke="#a5e7a5" stroke-width="3"/>
            <path d="M78 85L82 89L92 79" stroke="#a5e7a5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h3 class="empty-title">No Reports Available</h3>
        <p class="empty-description">Complete an experiment to generate code and validation reports</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.reports {
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-32);
}

.header-text {
  flex: 1;
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

.header-actions {
  display: flex;
  gap: var(--space-12);
}

/* Content Wrapper */
.content-wrapper {
  padding-bottom: var(--space-64);
}

/* Code Section */
.code-section {
  padding: var(--space-48) var(--space-32);
}

.section-container {
  max-width: 1440px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-32);
  padding-bottom: var(--space-24);
  border-bottom: 2px solid var(--color-soft-border);
}

.header-left {
  flex: 1;
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
  line-height: 1.5;
}

.code-meta {
  display: flex;
  gap: var(--space-24);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: var(--space-8);
  padding: var(--space-8) var(--space-16);
  background: var(--color-surface-accent);
  border-radius: var(--radius-pill);
  font-size: var(--text-control-size);
  color: var(--color-text-secondary);
  font-weight: 500;
}

.meta-item svg {
  color: var(--color-action-blue);
}

/* Validation Section */
.validation-section {
  padding: var(--space-48) var(--space-32);
  background: var(--color-surface-elevated);
}

.score-badge {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--space-4);
  padding: var(--space-16) var(--space-24);
  background: var(--color-surface-light);
  border-radius: var(--radius-medium);
  border: 2px solid var(--color-soft-border);
}

.score-badge.passed {
  border-color: var(--color-success-green);
  background: rgba(165, 231, 165, 0.1);
}

.score-label {
  font-size: var(--text-micro-size);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.score-value {
  font-size: var(--text-promo-size);
  font-weight: 700;
  color: var(--color-action-blue);
}

.score-badge.passed .score-value {
  color: var(--color-primary-green-dark);
}

/* Summary Section */
.summary-section {
  padding: var(--space-48) var(--space-32);
}

.summary-card {
  background: var(--color-surface-light);
  border-radius: var(--radius-large);
  padding: var(--space-32);
  border: 1px solid var(--color-soft-border);
  box-shadow: var(--shadow-medium);
}

.summary-header {
  margin-bottom: var(--space-24);
  padding-bottom: var(--space-16);
  border-bottom: 1px solid var(--color-soft-border);
}

.summary-title {
  font-size: var(--text-utility-size);
  font-weight: 600;
  color: var(--color-text-primary);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-32);
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-8);
}

.summary-label {
  font-size: var(--text-micro-size);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.summary-value {
  font-size: var(--text-link-heading-size);
  font-weight: 700;
  color: var(--color-text-primary);
  text-transform: capitalize;
}

.summary-value.running {
  color: var(--color-action-blue);
}

.summary-value.completed {
  color: var(--color-success-green);
}

.summary-value.failed {
  color: #ff6b6b;
}

.summary-value.passed {
  color: var(--color-primary-green-dark);
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
@media (max-width: 1023px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions button {
    flex: 1;
  }

  .section-header {
    flex-direction: column;
    gap: var(--space-20);
  }

  .code-meta,
  .score-badge {
    width: 100%;
  }

  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .page-header,
  .code-section,
  .validation-section,
  .summary-section {
    padding-left: var(--space-20);
    padding-right: var(--space-20);
  }

  .header-actions {
    flex-direction: column;
  }

  .code-meta {
    flex-direction: column;
    gap: var(--space-12);
  }

  .summary-grid {
    grid-template-columns: 1fr;
    gap: var(--space-20);
  }
}
</style>
