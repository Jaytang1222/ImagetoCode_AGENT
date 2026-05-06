// API服务层 - 与后端通信

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

class ApiError extends Error {
  constructor(message, status, data) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new ApiError(
      error.message || `HTTP ${response.status}: ${response.statusText}`,
      response.status,
      error
    )
  }
  return response.json()
}

// 上传图片
export const uploadImage = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData
  })

  return handleResponse(response)
}

// 启动流水线
export const startPipeline = async (config, imagePath) => {
  const requestBody = {
    image_path: imagePath,
    max_loops: config.maxLoops,
    threshold: config.threshold,
    model_provider: config.modelProvider || 'qwen'
  }
  
  const response = await fetch(`${API_BASE_URL}/pipeline/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(requestBody)
  })

  return handleResponse(response)
}

// 获取流水线状态
export const getPipelineStatus = async (pipelineId) => {
  const response = await fetch(`${API_BASE_URL}/pipeline/${pipelineId}/status`)
  return handleResponse(response)
}

// 停止流水线
export const stopPipeline = async (pipelineId) => {
  const response = await fetch(`${API_BASE_URL}/pipeline/${pipelineId}/stop`, {
    method: 'POST'
  })

  return handleResponse(response)
}

// 获取结果
export const getResults = async (pipelineId, round) => {
  const url = round 
    ? `${API_BASE_URL}/results/${pipelineId}?round=${round}`
    : `${API_BASE_URL}/results/${pipelineId}`
  
  const response = await fetch(url)
  return handleResponse(response)
}

// 下载代码
export const downloadCode = async (pipelineId) => {
  const response = await fetch(`${API_BASE_URL}/download/${pipelineId}/code`)
  
  if (!response.ok) {
    throw new ApiError('下载失败', response.status)
  }
  
  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'generated_code.py'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}

// 下载报告
export const downloadReport = async (pipelineId) => {
  const response = await fetch(`${API_BASE_URL}/download/${pipelineId}/report`)
  
  if (!response.ok) {
    throw new ApiError('下载失败', response.status)
  }
  
  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'validation_report.txt'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}

// 获取历史记录
export const getHistory = async () => {
  const response = await fetch(`${API_BASE_URL}/history`)
  return handleResponse(response)
}

// 删除历史记录
export const deleteHistory = async (pipelineId) => {
  const response = await fetch(`${API_BASE_URL}/history/${pipelineId}`, {
    method: 'DELETE'
  })

  return handleResponse(response)
}

export { ApiError }
