import { ref, computed } from 'vue'
import { useAgentStore } from '../stores/agentStore'
import * as api from '../services/api'
import { wsService, connectWebSocket, disconnectWebSocket } from '../services/websocket'

export function usePipeline() {
  const store = useAgentStore()
  const pipelineId = ref(null)
  const error = ref(null)

  // 上传图片并启动流水线
  const startPipeline = async (file) => {
    try {
      error.value = null
      
      // 1. 上传图片
      const uploadResult = await api.uploadImage(file)
      const imagePath = uploadResult.path
      
      // 2. 启动流水线
      const pipelineResult = await api.startPipeline(store.config, imagePath)
      pipelineId.value = pipelineResult.pipeline_id
      
      // 3. 更新store状态
      store.startPipeline()
      
      // 4. 连接WebSocket监听实时状态
      connectWebSocket(pipelineId.value)
      setupWebSocketListeners()
      
      return pipelineResult
    } catch (err) {
      error.value = err
      store.completePipeline(false)
      throw err
    }
  }

  // 停止流水线
  const stopPipeline = async () => {
    try {
      if (!pipelineId.value) return
      
      await api.stopPipeline(pipelineId.value)
      store.stopPipeline()
      // 不要立即断开，等待 Backend 发送停止消息并主动关闭连接
      // disconnectWebSocket() 会在收到 pipeline_stop 消息后自动调用
    } catch (err) {
      error.value = err
      throw err
    }
  }

  // 获取流水线状态
  const getPipelineStatus = async () => {
    try {
      if (!pipelineId.value) return null
      
      const status = await api.getPipelineStatus(pipelineId.value)
      return status
    } catch (err) {
      error.value = err
      throw err
    }
  }

  // 获取结果
  const getResults = async (round = null) => {
    try {
      if (!pipelineId.value) return null
      
      const results = await api.getResults(pipelineId.value, round)
      
      // 更新store中的结果
      store.updateResults({
        generatedCode: results.code,
        generatedImage: results.image_url,
        validationScore: results.score,
        validationPassed: results.passed,
        dimensions: results.dimensions,
        reports: results.reports
      })
      
      return results
    } catch (err) {
      error.value = err
      throw err
    }
  }

  // 设置WebSocket监听器
  const setupWebSocketListeners = () => {
    // Agent状态更新
    wsService.on('agentStatus', (data) => {
      store.updateAgentStatus(data.agent_id, {
        status: data.status,
        currentTask: data.task,
        progress: data.progress,
        message: data.message
      })
    })

    // 进度更新
    wsService.on('progressUpdate', (data) => {
      if (data.round) {
        store.currentRound = data.round
      }
    })

    // 轮次完成
    wsService.on('roundComplete', async (data) => {
      // 获取当前轮次的结果
      await getResults(data.round)
      
      if (data.passed) {
        // 验证通过，流水线完成
        store.completePipeline(true)
        disconnectWebSocket()
      } else if (data.round < store.config.maxLoops) {
        // 进入下一轮
        store.nextRound()
      } else {
        // 达到最大轮数，流水线完成但未通过
        store.completePipeline(false)
        disconnectWebSocket()
      }
    })

    // 流水线完成
    wsService.on('pipelineComplete', async (data) => {
      await getResults()
      // 使用 execution_completed 判断执行是否完成，而不是 success（验证结果）
      const executionSuccess = data.execution_completed !== false
      store.completePipeline(executionSuccess)
      disconnectWebSocket()
    })
    
    // 流水线停止
    wsService.on('pipelineStop', (data) => {
      // Backend 会主动关闭连接，延迟断开以确保消息接收完毕
      setTimeout(() => {
        disconnectWebSocket()
      }, 500)
    })

    // 流水线错误
    wsService.on('pipelineError', (data) => {
      error.value = new Error(data.message)
      store.completePipeline(false)
      disconnectWebSocket()
    })

    // 验证结果
    wsService.on('validationResult', (data) => {
      store.updateResults({
        validationScore: data.score,
        validationPassed: data.passed,
        dimensions: data.dimensions
      })
    })

    // 连接错误
    wsService.on('error', (err) => {
      console.error('WebSocket错误:', err)
      error.value = err
    })

    // 重连失败
    wsService.on('reconnectFailed', () => {
      error.value = new Error('WebSocket连接失败，请刷新页面重试')
    })
  }

  // 清理
  const cleanup = () => {
    disconnectWebSocket()
    pipelineId.value = null
    error.value = null
  }

  return {
    pipelineId,
    error,
    startPipeline,
    stopPipeline,
    getPipelineStatus,
    getResults,
    cleanup
  }
}
