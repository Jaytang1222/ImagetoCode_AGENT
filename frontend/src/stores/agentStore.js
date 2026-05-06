import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useAgentStore = defineStore('agent', () => {
  // 上传相关
  const uploadedImage = ref(null)
  const uploadedImagePreview = ref(null)

  // 配置
  const config = ref({
    maxLoops: 5,
    threshold: 0.75,
    modelProvider: 'qwen'
  })

  // 执行状态
  const isRunning = ref(false)
  const currentRound = ref(0)
  const pipelineStatus = ref('idle') // idle, running, completed, failed

  // Agent状态
  const agents = ref([
    {
      id: 'agent1',
      title: 'Agent 1',
      description: '代码生成',
      status: 'idle',
      currentTask: '',
      progress: null,
      message: ''
    },
    {
      id: 'agent2',
      title: 'Agent 2',
      description: '视觉评估',
      status: 'idle',
      currentTask: '',
      progress: null,
      message: ''
    },
    {
      id: 'agent3',
      title: 'Agent 3',
      description: '代码评判',
      status: 'idle',
      currentTask: '',
      progress: null,
      message: ''
    },
    {
      id: 'agent4',
      title: 'Agent 4',
      description: '反馈优化',
      status: 'idle',
      currentTask: '',
      progress: null,
      message: ''
    }
  ])

  // 结果
  const results = ref({
    generatedCode: '',
    generatedImage: null,
    validationScore: null,
    validationPassed: null,
    reports: [],
    dimensions: {
      color: 0,
      text: 0,
      structure: 0,
      vlm: 0
    }
  })

  // Computed
  const hasUploadedImage = computed(() => uploadedImage.value !== null)
  const canStart = computed(() => hasUploadedImage.value && !isRunning.value)

  // Actions
  const uploadImage = (file, preview) => {
    uploadedImage.value = file
    uploadedImagePreview.value = preview
  }

  const removeImage = () => {
    uploadedImage.value = null
    uploadedImagePreview.value = null
    resetResults()
  }

  const updateConfig = (newConfig) => {
    config.value = { ...config.value, ...newConfig }
  }

  const updateAgentStatus = (agentId, updates) => {
    const agent = agents.value.find(a => a.id === agentId)
    if (agent) {
      Object.assign(agent, updates)
    }
  }

  const resetAgents = () => {
    agents.value.forEach(agent => {
      agent.status = 'idle'
      agent.currentTask = ''
      agent.progress = null
      agent.message = ''
    })
  }

  const updateResults = (newResults) => {
    results.value = { ...results.value, ...newResults }
  }

  const resetResults = () => {
    results.value = {
      generatedCode: '',
      generatedImage: null,
      validationScore: null,
      validationPassed: null,
      reports: [],
      dimensions: {
        color: 0,
        text: 0,
        structure: 0,
        vlm: 0
      }
    }
  }

  const startPipeline = () => {
    isRunning.value = true
    pipelineStatus.value = 'running'
    currentRound.value = 1
    resetAgents()
  }

  const stopPipeline = () => {
    isRunning.value = false
    pipelineStatus.value = 'idle'
    currentRound.value = 0
    resetAgents()
  }

  const completePipeline = (success = true) => {
    isRunning.value = false
    pipelineStatus.value = success ? 'completed' : 'failed'
  }

  const nextRound = () => {
    if (currentRound.value < config.value.maxLoops) {
      currentRound.value++
      resetAgents()
    }
  }

  const resetState = () => {
    removeImage()
    stopPipeline()
    resetResults()
  }

  return {
    // State
    uploadedImage,
    uploadedImagePreview,
    config,
    isRunning,
    currentRound,
    pipelineStatus,
    agents,
    results,

    // Computed
    hasUploadedImage,
    canStart,

    // Actions
    uploadImage,
    removeImage,
    updateConfig,
    updateAgentStatus,
    resetAgents,
    updateResults,
    resetResults,
    startPipeline,
    stopPipeline,
    completePipeline,
    nextRound,
    resetState
  }
})
