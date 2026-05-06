import { ref } from 'vue'
import * as api from '../services/api'

export function useHistory() {
  const history = ref([])
  const loading = ref(false)
  const error = ref(null)

  // 获取历史记录
  const fetchHistory = async () => {
    try {
      loading.value = true
      error.value = null
      
      const data = await api.getHistory()
      history.value = data.history || []
      
      return data
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  // 删除单条历史记录
  const deleteHistoryItem = async (id) => {
    try {
      error.value = null
      
      await api.deleteHistory(id)
      
      // 从本地列表中移除
      history.value = history.value.filter(item => item.id !== id)
      
      return true
    } catch (err) {
      error.value = err
      throw err
    }
  }

  // 清空所有历史记录
  const clearAllHistory = async () => {
    try {
      error.value = null
      
      // 删除所有记录
      await Promise.all(
        history.value.map(item => api.deleteHistory(item.id))
      )
      
      history.value = []
      
      return true
    } catch (err) {
      error.value = err
      throw err
    }
  }

  // 下载历史记录的代码
  const downloadHistoryCode = async (id) => {
    try {
      error.value = null
      await api.downloadCode(id)
      return true
    } catch (err) {
      error.value = err
      throw err
    }
  }

  // 下载历史记录的报告
  const downloadHistoryReport = async (id) => {
    try {
      error.value = null
      await api.downloadReport(id)
      return true
    } catch (err) {
      error.value = err
      throw err
    }
  }

  return {
    history,
    loading,
    error,
    fetchHistory,
    deleteHistoryItem,
    clearAllHistory,
    downloadHistoryCode,
    downloadHistoryReport
  }
}
