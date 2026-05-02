<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useAgentStore } from './stores/agentStore'
import { usePipeline } from './composables/usePipeline'
import { useHistory } from './composables/useHistory'
import AppleButton from './components/AppleButton.vue'
import AppleContainer from './components/AppleContainer.vue'
import AppleSection from './components/AppleSection.vue'
import AppleGrid from './components/AppleGrid.vue'
import ImageUploader from './components/ImageUploader.vue'
import ConfigPanel from './components/ConfigPanel.vue'
import AgentStatusCard from './components/AgentStatusCard.vue'
import ProgressIndicator from './components/ProgressIndicator.vue'
import ComparisonView from './components/ComparisonView.vue'
import CodeViewer from './components/CodeViewer.vue'
import ValidationReport from './components/ValidationReport.vue'
import ToastNotification from './components/ToastNotification.vue'
import LoadingOverlay from './components/LoadingOverlay.vue'
import HistoryPanel from './components/HistoryPanel.vue'
import ErrorBoundary from './components/ErrorBoundary.vue'

// 使用store和composables
const store = useAgentStore()
const pipeline = usePipeline()
const historyManager = useHistory()

// Toast和Loading引用
const toast = ref(null)
const loading = ref(false)
const loadingMessage = ref('')
const showHistory = ref(false)

// 事件处理
const handleImageUpload = (file, preview) => {
  store.uploadImage(file, preview)
  toast.value?.success('图片上传成功')
}

const handleImageRemove = () => {
  store.removeImage()
  toast.value?.info('已清除图片')
}

const handleConfigSave = (newConfig) => {
  store.updateConfig(newConfig)
  toast.value?.success('配置已保存')
}

const startPipeline = async () => {
  if (!store.canStart) {
    toast.value?.warning('请先上传参考图表')
    return
  }
  
  try {
    loading.value = true
    loadingMessage.value = '正在启动流水线...'
    
    await pipeline.startPipeline(store.uploadedImage)
    
    loading.value = false
    toast.value?.success('流水线已启动')
  } catch (error) {
    loading.value = false
    
    const errorMessage = error.message || '启动失败'
    toast.value?.error(errorMessage)
    
    console.error('启动流水线失败:', error)
  }
}

const stopPipeline = async () => {
  try {
    loading.value = true
    loadingMessage.value = '正在停止...'
    
    await pipeline.stopPipeline()
    
    loading.value = false
    toast.value?.info('已停止执行')
  } catch (error) {
    loading.value = false
    toast.value?.error('停止失败: ' + error.message)
  }
}

// 历史记录相关
const toggleHistory = () => {
  showHistory.value = !showHistory.value
  if (showHistory.value) {
    historyManager.fetchHistory().catch(err => {
      toast.value?.error('加载历史记录失败: ' + err.message)
    })
  }
}

const handleHistorySelect = (item) => {
  console.log('选中历史记录:', item)
}

const handleHistoryView = async (item) => {
  try {
    loading.value = true
    loadingMessage.value = '加载历史记录...'
    
    // 这里应该调用API获取历史记录的详细信息
    // 然后更新store中的结果
    
    loading.value = false
    toast.value?.success('已加载历史记录')
  } catch (error) {
    loading.value = false
    toast.value?.error('加载失败: ' + error.message)
  }
}

const handleHistoryDownload = async (item) => {
  try {
    await historyManager.downloadHistoryCode(item.id)
    toast.value?.success('下载成功')
  } catch (error) {
    toast.value?.error('下载失败: ' + error.message)
  }
}

const handleHistoryDelete = async (id) => {
  try {
    await historyManager.deleteHistoryItem(id)
    toast.value?.success('已删除')
  } catch (error) {
    toast.value?.error('删除失败: ' + error.message)
  }
}

const handleHistoryClear = async () => {
  try {
    loading.value = true
    loadingMessage.value = '清空中...'
    
    await historyManager.clearAllHistory()
    
    loading.value = false
    toast.value?.success('已清空所有历史记录')
  } catch (error) {
    loading.value = false
    toast.value?.error('清空失败: ' + error.message)
  }
}

const handleHistoryRefresh = () => {
  historyManager.fetchHistory().catch(err => {
    toast.value?.error('刷新失败: ' + err.message)
  })
}

// 下载功能
const downloadCode = async () => {
  if (!pipeline.pipelineId.value) {
    toast.value?.warning('暂无可下载的代码')
    return
  }
  
  try {
    await historyManager.downloadHistoryCode(pipeline.pipelineId.value)
    toast.value?.success('代码下载成功')
  } catch (error) {
    toast.value?.error('下载失败: ' + error.message)
  }
}

const downloadReport = async () => {
  if (!pipeline.pipelineId.value) {
    toast.value?.warning('暂无可下载的报告')
    return
  }
  
  try {
    await historyManager.downloadHistoryReport(pipeline.pipelineId.value)
    toast.value?.success('报告下载成功')
  } catch (error) {
    toast.value?.error('下载失败: ' + error.message)
  }
}

// 生命周期
onMounted(() => {
  // 可以在这里做一些初始化工作
})

onUnmounted(() => {
  // 清理资源
  pipeline.cleanup()
})

// 监听pipeline错误
watch(() => pipeline.error.value, (error) => {
  if (error) {
    toast.value?.error('执行失败: ' + error.message)
  }
})
</script>

<template>
  <ErrorBoundary>
    <div id="app">
      <!-- Toast通知 -->
      <ToastNotification ref="toast" />
      
      <!-- Loading遮罩 -->
      <LoadingOverlay 
        :visible="loading"
        :message="loadingMessage"
        :cancellable="store.isRunning"
        @cancel="stopPipeline"
      />

      <!-- Hero Section -->
      <AppleSection background="gradient-hero" spacing="xlarge">
        <AppleContainer size="wide">
          <div class="hero-content">
            <div class="hero-badge">
              <span class="badge-text">AI-Powered Chart Reproduction</span>
            </div>
            <h1 class="text-hero-l hero-title">多智能体图表复现系统</h1>
            <p class="text-body hero-description">
              基于阿里云 DashScope API 的多智能体流水线<br/>从参考图表自动生成高质量 Matplotlib 代码
            </p>
            <div class="hero-actions">
              <AppleButton 
                variant="primary"
                size="large"
                @click="toggleHistory"
              >
                {{ showHistory ? '隐藏历史记录' : '查看历史记录' }}
              </AppleButton>
            </div>
          </div>
        </AppleContainer>
      </AppleSection>

      <!-- History Section -->
      <AppleSection 
        v-if="showHistory"
        background="white" 
        spacing="large"
      >
        <AppleContainer size="wide">
          <div class="section-header">
            <h2 class="text-section">历史记录</h2>
            <p class="text-body text-secondary">查看和管理您的图表生成历史</p>
          </div>
          <HistoryPanel
            :history="historyManager.history.value"
            :loading="historyManager.loading.value"
            @select="handleHistorySelect"
            @view="handleHistoryView"
            @download="handleHistoryDownload"
            @delete="handleHistoryDelete"
            @clear="handleHistoryClear"
            @refresh="handleHistoryRefresh"
          />
        </AppleContainer>
      </AppleSection>

      <!-- Upload & Config Section -->
      <AppleSection background="surface" spacing="large">
        <AppleContainer size="wide">
          <div class="section-header">
            <h2 class="text-section">开始创建</h2>
            <p class="text-body text-secondary">上传参考图表并配置生成参数</p>
          </div>
          
          <div class="upload-config-grid">
            <div class="content-card">
              <div class="card-header">
                <h3 class="text-utility">上传参考图表</h3>
                <span class="card-badge">Step 1</span>
              </div>
              <ImageUploader 
                @upload="handleImageUpload"
                @remove="handleImageRemove"
              />
            </div>
            <div class="content-card">
              <div class="card-header">
                <h3 class="text-utility">系统配置</h3>
                <span class="card-badge">Step 2</span>
              </div>
              <ConfigPanel 
                :config="store.config"
                @save="handleConfigSave"
              />
            </div>
          </div>
          
          <div class="action-buttons">
            <AppleButton 
              v-if="!store.isRunning"
              variant="primary" 
              size="xlarge"
              @click="startPipeline"
              :disabled="!store.canStart"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" style="margin-right: 8px;">
                <path d="M6 4L14 10L6 16V4Z" fill="currentColor"/>
              </svg>
              开始生成图表
            </AppleButton>
            <AppleButton 
              v-else
              variant="secondary" 
              size="xlarge"
              @click="stopPipeline"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" style="margin-right: 8px;">
                <rect x="5" y="5" width="10" height="10" fill="currentColor"/>
              </svg>
              停止执行
            </AppleButton>
          </div>
        </AppleContainer>
      </AppleSection>

      <!-- Agent Status Section -->
      <AppleSection background="white" spacing="large">
        <AppleContainer size="wide">
          <div class="section-header">
            <h2 class="text-section">执行状态</h2>
            <p class="text-body text-secondary">实时监控多智能体协作流程</p>
          </div>
          
          <div class="progress-wrapper">
            <ProgressIndicator 
              :current-round="store.currentRound"
              :max-rounds="store.config.maxLoops"
              :status="store.pipelineStatus"
            />
          </div>
          
          <div class="agents-grid">
            <AgentStatusCard
              v-for="agent in store.agents"
              :key="agent.id"
              :title="agent.title"
              :description="agent.description"
              :status="agent.status"
              :current-task="agent.currentTask"
              :progress="agent.progress"
              :message="agent.message"
            />
          </div>
        </AppleContainer>
      </AppleSection>

      <!-- Results Section -->
      <AppleSection 
        v-if="store.results.generatedImage || store.isRunning"
        background="dark" 
        spacing="large"
      >
        <AppleContainer size="wide">
          <div class="section-header">
            <h2 class="text-section">对比结果</h2>
            <p class="text-body text-secondary">原始图表与生成图表的视觉对比</p>
          </div>
          <ComparisonView
            :original-image="store.uploadedImagePreview"
            :generated-image="store.results.generatedImage"
            :score="store.results.validationScore"
            :passed="store.results.validationPassed"
          />
        </AppleContainer>
      </AppleSection>

      <!-- Code & Reports Section -->
      <AppleSection 
        v-if="store.results.generatedCode"
        background="surface" 
        spacing="large"
      >
        <AppleContainer size="wide">
          <div class="code-section-header">
            <div>
              <h2 class="text-section">生成代码</h2>
              <p class="text-body text-secondary">可直接运行的 Python Matplotlib 代码</p>
            </div>
            <div class="code-actions">
              <AppleButton variant="secondary" @click="downloadCode">
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none" style="margin-right: 6px;">
                  <path d="M9 2V12M9 12L5 8M9 12L13 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <path d="M2 12V14C2 15.1046 2.89543 16 4 16H14C15.1046 16 16 15.1046 16 14V12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                下载代码
              </AppleButton>
              <AppleButton variant="secondary" @click="downloadReport">
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none" style="margin-right: 6px;">
                  <path d="M4 2H10L14 6V14C14 15.1046 13.1046 16 12 16H4C2.89543 16 2 15.1046 2 14V4C2 2.89543 2.89543 2 4 2Z" stroke="currentColor" stroke-width="2"/>
                  <path d="M10 2V6H14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                下载报告
              </AppleButton>
            </div>
          </div>
          
          <CodeViewer
            :code="store.results.generatedCode"
            language="python"
            filename="generated_chart.py"
          />
          
          <div class="validation-section">
            <ValidationReport
              :dimensions="store.results.dimensions"
              :reports="store.results.reports"
              :current-round="store.currentRound"
            />
          </div>
        </AppleContainer>
      </AppleSection>

      <!-- Footer -->
      <AppleSection background="dark" spacing="medium">
        <AppleContainer size="wide">
          <div class="footer-content">
            <div class="footer-brand">
              <h4 class="text-utility">多智能体图表复现框架</h4>
              <p class="text-control text-secondary">基于先进的 AI 技术，让图表复现变得简单高效</p>
            </div>
            <div class="footer-info">
              <p class="text-control text-secondary">© 2026 All Rights Reserved</p>
            </div>
          </div>
        </AppleContainer>
      </AppleSection>
    </div>
  </ErrorBoundary>
</template>

<style scoped>
#app {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8faf9 0%, #ffffff 100%);
}

/* Hero Section Styles */
.hero-content {
  text-align: center;
  max-width: 900px;
  margin: 0 auto;
  padding: var(--space-48) 0;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-8) var(--space-20);
  background: var(--color-accent-gradient);
  border-radius: var(--radius-pill);
  margin-bottom: var(--space-32);
  box-shadow: var(--shadow-subtle);
}

.badge-text {
  font-size: var(--text-control-size);
  font-weight: 600;
  color: var(--color-graphite-a);
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.hero-title {
  margin-bottom: var(--space-24);
  background: linear-gradient(135deg, #2a5555 0%, #1a3f3f 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin-bottom: var(--space-40);
  font-size: 18px;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: var(--space-20);
}

/* Section Headers */
.section-header {
  text-align: center;
  max-width: 800px;
  margin: 0 auto var(--space-56);
}

.section-header h2 {
  margin-bottom: var(--space-12);
  color: var(--color-text-primary);
}

.section-header p {
  font-size: 17px;
  line-height: 1.5;
}

/* Upload & Config Grid */
.upload-config-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-40);
  width: 100%;
}

@media (max-width: 1023px) {
  .upload-config-grid {
    grid-template-columns: 1fr;
    gap: var(--space-32);
  }
}

/* Content Cards */
.content-card {
  background: var(--color-surface-light);
  border-radius: var(--radius-large);
  padding: var(--space-32);
  box-shadow: var(--shadow-medium);
  border: 1px solid rgba(165, 231, 165, 0.2);
  transition: all var(--transition-base);
  height: 100%;
  width: 100%;
}

.content-card:hover {
  box-shadow: var(--shadow-strong);
  transform: translateY(-2px);
  border-color: rgba(165, 231, 165, 0.4);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-24);
}

.card-badge {
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

/* Action Buttons */
.action-buttons {
  display: flex;
  justify-content: center;
  margin-top: var(--space-64);
  gap: var(--space-20);
}

.action-buttons button {
  min-width: 240px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* Agents Grid */
.agents-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-24);
  width: 100%;
}

@media (max-width: 1439px) {
  .agents-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-20);
  }
}

@media (max-width: 833px) {
  .agents-grid {
    grid-template-columns: 1fr;
    gap: var(--space-20);
  }
}

/* Progress Wrapper */
.progress-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: var(--space-48);
  padding: var(--space-32);
  background: var(--color-surface-accent);
  border-radius: var(--radius-large);
  border: 1px solid rgba(173, 222, 239, 0.3);
}

/* Code Section */
.code-section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-32);
  padding-bottom: var(--space-24);
  border-bottom: 2px solid rgba(165, 231, 165, 0.2);
}

.code-section-header h2 {
  margin-bottom: var(--space-8);
}

.code-actions {
  display: flex;
  gap: var(--space-12);
  flex-shrink: 0;
}

.code-actions button {
  display: inline-flex;
  align-items: center;
}

.validation-section {
  margin-top: var(--space-56);
  padding-top: var(--space-48);
  border-top: 2px solid rgba(173, 222, 239, 0.2);
}

/* Footer */
.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-32) 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-brand h4 {
  color: var(--color-primary-green);
  margin-bottom: var(--space-8);
}

.footer-info {
  text-align: right;
}

/* Responsive Styles */
@media (max-width: 1024px) {
  .hero-content {
    padding: var(--space-32) 0;
  }
  
  .section-header {
    margin-bottom: var(--space-40);
  }
  
  .content-card {
    padding: var(--space-24);
  }
  
  .upload-config-grid {
    gap: var(--space-24);
  }
  
  .code-section-header {
    flex-direction: column;
    gap: var(--space-20);
  }
  
  .code-actions {
    width: 100%;
  }
  
  .code-actions button {
    flex: 1;
  }
}

@media (max-width: 640px) {
  .hero-badge {
    padding: var(--space-6) var(--space-14);
  }
  
  .badge-text {
    font-size: 11px;
  }
  
  .hero-description {
    font-size: 16px;
  }
  
  .hero-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .hero-actions button {
    width: 100%;
  }
  
  .upload-config-grid {
    gap: var(--space-24);
  }
  
  .action-buttons {
    flex-direction: column;
    margin-top: var(--space-48);
  }
  
  .action-buttons button {
    width: 100%;
    min-width: unset;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-12);
  }
  
  .progress-wrapper {
    padding: var(--space-20);
  }
  
  .footer-content {
    flex-direction: column;
    text-align: center;
    gap: var(--space-20);
  }
  
  .footer-info {
    text-align: center;
  }
}

/* Desktop Enhancements */
@media (min-width: 1440px) {
  .hero-content {
    max-width: 1100px;
    padding: var(--space-64) 0;
  }
  
  .hero-description {
    font-size: 20px;
  }
  
  .section-header {
    max-width: 900px;
    margin-bottom: var(--space-64);
  }
  
  .content-card {
    padding: var(--space-40);
  }
  
  .action-buttons button {
    min-width: 280px;
  }
}
</style>
