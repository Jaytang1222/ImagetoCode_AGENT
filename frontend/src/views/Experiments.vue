<script setup>
import { ref } from 'vue'
import { useAgentStore } from '../stores/agentStore'
import { usePipeline } from '../composables/usePipeline'
import ImageUploader from '../components/ImageUploader.vue'
import ConfigPanel from '../components/ConfigPanel.vue'
import PipelineFlow from '../components/pipeline/PipelineFlow.vue'
import ComparisonView from '../components/ComparisonView.vue'
import AppleButton from '../components/AppleButton.vue'
import ToastNotification from '../components/ToastNotification.vue'
import LoadingOverlay from '../components/LoadingOverlay.vue'

const store = useAgentStore()
const pipeline = usePipeline()
const toast = ref(null)
const loading = ref(false)
const loadingMessage = ref('')

const handleImageUpload = (file, preview) => {
  store.uploadImage(file, preview)
  toast.value?.success('Image uploaded successfully')
}

const handleImageRemove = () => {
  store.removeImage()
  toast.value?.info('Image removed')
}

const handleConfigSave = (newConfig) => {
  store.updateConfig(newConfig)
  toast.value?.success('Configuration saved')
}

const startPipeline = async () => {
  if (!store.canStart) {
    toast.value?.warning('Please upload a reference chart first')
    return
  }
  
  try {
    loading.value = true
    loadingMessage.value = 'Starting pipeline...'
    
    await pipeline.startPipeline(store.uploadedImage)
    
    loading.value = false
    toast.value?.success('Pipeline started successfully')
  } catch (error) {
    loading.value = false
    toast.value?.error(error.message || 'Failed to start pipeline')
    console.error('Pipeline start error:', error)
  }
}

const stopPipeline = async () => {
  try {
    loading.value = true
    loadingMessage.value = 'Stopping pipeline...'
    
    await pipeline.stopPipeline()
    
    loading.value = false
    toast.value?.info('Pipeline stopped')
  } catch (error) {
    loading.value = false
    toast.value?.error('Failed to stop pipeline: ' + error.message)
  }
}
</script>

<template>
  <div class="experiments">
    <ToastNotification ref="toast" />
    <LoadingOverlay 
      :visible="loading"
      :message="loadingMessage"
      :cancellable="store.isRunning"
      @cancel="stopPipeline"
    />

    <!-- Page Header -->
    <section class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">Experiment Control</h1>
          <p class="page-subtitle">Configure and execute chart reproduction experiments</p>
        </div>
        <div class="header-actions">
          <AppleButton 
            v-if="!store.isRunning"
            variant="primary" 
            size="large"
            @click="startPipeline"
            :disabled="!store.canStart"
          >
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" style="margin-right: 6px;">
              <path d="M5 3L13 9L5 15V3Z" fill="currentColor"/>
            </svg>
            Start Experiment
          </AppleButton>
          <AppleButton 
            v-else
            variant="secondary" 
            size="large"
            @click="stopPipeline"
          >
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" style="margin-right: 6px;">
              <rect x="4" y="4" width="10" height="10" fill="currentColor"/>
            </svg>
            Stop Execution
          </AppleButton>
        </div>
      </div>
    </section>

    <!-- Configuration Panel -->
    <section class="config-section">
      <div class="section-container">
        <div class="config-grid">
          <!-- Left: Image Upload -->
          <div class="config-panel">
            <div class="panel-header">
              <div class="panel-title-group">
                <h2 class="panel-title">Reference Chart</h2>
                <span class="step-badge">Step 1</span>
              </div>
              <p class="panel-subtitle">Upload the chart you want to reproduce</p>
            </div>
            <div class="panel-content">
              <ImageUploader 
                @upload="handleImageUpload"
                @remove="handleImageRemove"
              />
            </div>
          </div>

          <!-- Right: Configuration -->
          <div class="config-panel">
            <div class="panel-header">
              <div class="panel-title-group">
                <h2 class="panel-title">System Configuration</h2>
                <span class="step-badge">Step 2</span>
              </div>
              <p class="panel-subtitle">Adjust generation parameters</p>
            </div>
            <div class="panel-content">
              <ConfigPanel 
                :config="store.config"
                @save="handleConfigSave"
              />
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Pipeline Visualization -->
    <section v-if="store.isRunning || store.pipelineStatus !== 'idle'" class="pipeline-section">
      <div class="section-container">
        <div class="section-header">
          <h2 class="section-title">Pipeline Execution</h2>
          <p class="section-subtitle">Real-time multi-agent collaboration workflow</p>
        </div>
        <PipelineFlow 
          :agents="store.agents"
          :current-round="store.currentRound"
          :is-running="store.isRunning"
        />
      </div>
    </section>

    <!-- Results Comparison -->
    <section v-if="store.results.generatedImage" class="results-section">
      <div class="section-container">
        <div class="section-header">
          <h2 class="section-title">Visual Comparison</h2>
          <p class="section-subtitle">Side-by-side comparison of reference and generated charts</p>
        </div>
        <ComparisonView
          :original-image="store.uploadedImagePreview"
          :generated-image="store.results.generatedImage"
          :score="store.results.validationScore"
          :passed="store.results.validationPassed"
        />
      </div>
    </section>

    <!-- Empty State -->
    <section v-if="!store.hasUploadedImage && !store.isRunning" class="empty-state">
      <div class="empty-content">
        <div class="empty-icon">
          <svg width="120" height="120" viewBox="0 0 120 120" fill="none">
            <rect x="20" y="20" width="80" height="80" rx="8" stroke="#d8e5e5" stroke-width="3" stroke-dasharray="8 8"/>
            <path d="M60 45V75M45 60H75" stroke="#addeef" stroke-width="3" stroke-linecap="round"/>
          </svg>
        </div>
        <h3 class="empty-title">No Experiment Running</h3>
        <p class="empty-description">Upload a reference chart to begin your first experiment</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.experiments {
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

/* Configuration Section */
.config-section {
  padding: var(--space-48) var(--space-32);
}

.section-container {
  max-width: 1440px;
  margin: 0 auto;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-32);
}

.config-panel {
  background: var(--color-surface-light);
  border-radius: var(--radius-large);
  border: 1px solid var(--color-soft-border);
  box-shadow: var(--shadow-medium);
  overflow: hidden;
  transition: all var(--transition-base);
}

.config-panel:hover {
  box-shadow: var(--shadow-strong);
  transform: translateY(-2px);
}

.panel-header {
  padding: var(--space-32) var(--space-32) var(--space-24);
  border-bottom: 1px solid var(--color-soft-border);
  background: linear-gradient(135deg, rgba(165, 231, 165, 0.05) 0%, rgba(173, 222, 239, 0.05) 100%);
}

.panel-title-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-8);
}

.panel-title {
  font-size: var(--text-utility-size);
  font-weight: 600;
  color: var(--color-text-primary);
}

.step-badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-4) var(--space-12);
  background: var(--color-primary-green);
  color: var(--color-graphite-a);
  border-radius: var(--radius-pill);
  font-size: var(--text-micro-size);
  font-weight: 600;
  letter-spacing: 0.5px;
}

.panel-subtitle {
  font-size: var(--text-control-size);
  color: var(--color-text-secondary);
}

.panel-content {
  padding: var(--space-32);
}

/* Pipeline Section */
.pipeline-section {
  padding: var(--space-48) var(--space-32);
  background: var(--color-surface-elevated);
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
  line-height: 1.5;
}

/* Results Section */
.results-section {
  padding: var(--space-48) var(--space-32);
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

.empty-icon {
  margin-bottom: var(--space-16);
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

  .config-grid {
    grid-template-columns: 1fr;
    gap: var(--space-24);
  }
}

@media (max-width: 640px) {
  .page-header {
    padding: var(--space-32) var(--space-20) var(--space-24);
  }

  .config-section,
  .pipeline-section,
  .results-section {
    padding: var(--space-32) var(--space-20);
  }

  .panel-header,
  .panel-content {
    padding: var(--space-24);
  }

  .header-actions {
    flex-direction: column;
  }

  .header-actions button {
    width: 100%;
  }
}
</style>
