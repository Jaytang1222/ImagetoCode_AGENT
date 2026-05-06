<script setup>
import { onMounted, onUnmounted, watch } from 'vue'
import { usePipeline } from './composables/usePipeline'
import Navbar from './components/layout/Navbar.vue'
import ErrorBoundary from './components/ErrorBoundary.vue'

const pipeline = usePipeline()

// 生命周期
onMounted(() => {
  // 初始化工作
})

onUnmounted(() => {
  // 清理资源
  pipeline.cleanup()
})
</script>

<template>
  <ErrorBoundary>
    <div id="app">
      <Navbar />
      <main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </ErrorBoundary>
</template>

<style>
#app {
  min-height: 100vh;
  background: var(--color-pale-gray);
}

.main-content {
  width: 100%;
}

/* Page Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
