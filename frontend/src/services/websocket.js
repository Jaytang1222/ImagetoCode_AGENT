// WebSocket服务 - 实时状态更新

class WebSocketService {
  constructor() {
    this.ws = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 3000
    this.listeners = new Map()
    this.isConnecting = false
  }

  connect(url) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket已连接')
      return
    }

    if (this.isConnecting) {
      console.log('WebSocket正在连接中...')
      return
    }

    this.isConnecting = true

    try {
      this.ws = new WebSocket(url)

      this.ws.onopen = () => {
        console.log('WebSocket连接成功')
        this.isConnecting = false
        this.reconnectAttempts = 0
        this.emit('connected')
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.handleMessage(data)
        } catch (error) {
          console.error('解析WebSocket消息失败:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket错误:', error)
        this.isConnecting = false
        this.emit('error', error)
      }

      this.ws.onclose = () => {
        console.log('WebSocket连接关闭')
        this.isConnecting = false
        this.emit('disconnected')
        this.attemptReconnect(url)
      }
    } catch (error) {
      console.error('创建WebSocket连接失败:', error)
      this.isConnecting = false
      this.emit('error', error)
    }
  }

  disconnect() {
    if (this.ws) {
      // 使用正常关闭码 1000
      this.ws.close(1000, 'Client disconnect')
      this.ws = null
    }
    this.reconnectAttempts = this.maxReconnectAttempts // 阻止重连
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket未连接，无法发送消息')
    }
  }

  handleMessage(data) {
    const { type, payload } = data

    switch (type) {
      case 'agent_status':
        this.emit('agentStatus', payload)
        break
      case 'progress_update':
        this.emit('progressUpdate', payload)
        break
      case 'round_complete':
        this.emit('roundComplete', payload)
        break
      case 'pipeline_complete':
        this.emit('pipelineComplete', payload)
        break
      case 'pipeline_stop':
        this.emit('pipelineStop', payload)
        break
      case 'pipeline_error':
        this.emit('pipelineError', payload)
        break
      case 'validation_result':
        this.emit('validationResult', payload)
        break
      default:
        console.warn('未知的消息类型:', type)
    }
  }

  attemptReconnect(url) {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('达到最大重连次数，停止重连')
      this.emit('reconnectFailed')
      return
    }

    this.reconnectAttempts++
    console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)

    setTimeout(() => {
      this.connect(url)
    }, this.reconnectDelay)
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  off(event, callback) {
    if (!this.listeners.has(event)) return

    const callbacks = this.listeners.get(event)
    const index = callbacks.indexOf(callback)
    if (index > -1) {
      callbacks.splice(index, 1)
    }
  }

  emit(event, data) {
    if (!this.listeners.has(event)) return

    const callbacks = this.listeners.get(event)
    callbacks.forEach(callback => {
      try {
        callback(data)
      } catch (error) {
        console.error(`执行事件回调失败 (${event}):`, error)
      }
    })
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN
  }
}

// 单例模式
export const wsService = new WebSocketService()

// 便捷方法
export const connectWebSocket = (pipelineId) => {
  const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
  const url = `${wsUrl}/${pipelineId}`
  wsService.connect(url)
}

export const disconnectWebSocket = () => {
  wsService.disconnect()
}
