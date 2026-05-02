<template>
  <div class="progress-indicator">
    <svg class="progress-ring" :width="size" :height="size">
      <defs>
        <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#a5e7a5;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#addeef;stop-opacity:1" />
        </linearGradient>
      </defs>
      <circle
        class="progress-ring__background"
        :stroke-width="strokeWidth"
        :r="normalizedRadius"
        :cx="center"
        :cy="center"
      />
      <circle
        class="progress-ring__progress"
        :stroke-width="strokeWidth"
        :stroke-dasharray="circumference + ' ' + circumference"
        :style="{ strokeDashoffset: strokeDashoffset }"
        :r="normalizedRadius"
        :cx="center"
        :cy="center"
      />
    </svg>
    
    <div class="progress-content">
      <div class="progress-text">
        <span class="text-hero-l">{{ currentRound }}</span>
        <span class="text-body text-secondary">/{{ maxRounds }}</span>
      </div>
      <p class="text-control text-secondary">{{ statusText }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentRound: {
    type: Number,
    default: 0
  },
  maxRounds: {
    type: Number,
    default: 5
  },
  status: {
    type: String,
    default: 'idle',
    validator: (value) => ['idle', 'running', 'completed', 'failed'].includes(value)
  },
  size: {
    type: Number,
    default: 180
  },
  strokeWidth: {
    type: Number,
    default: 10
  }
})

const center = computed(() => props.size / 2)
const normalizedRadius = computed(() => center.value - props.strokeWidth / 2)
const circumference = computed(() => normalizedRadius.value * 2 * Math.PI)

const progress = computed(() => {
  if (props.maxRounds === 0) return 0
  return (props.currentRound / props.maxRounds) * 100
})

const strokeDashoffset = computed(() => {
  return circumference.value - (progress.value / 100) * circumference.value
})

const statusText = computed(() => {
  switch (props.status) {
    case 'idle':
      return '等待开始'
    case 'running':
      return '正在执行'
    case 'completed':
      return '已完成'
    case 'failed':
      return '执行失败'
    default:
      return ''
  }
})
</script>

<style scoped>
.progress-indicator {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.progress-ring {
  transform: rotate(-90deg);
}

.progress-ring__background {
  fill: none;
  stroke: rgba(173, 222, 239, 0.2);
  stroke-width: 2;
}

.progress-ring__progress {
  fill: none;
  stroke: url(#progressGradient);
  stroke-linecap: round;
  transition: stroke-dashoffset var(--transition-slow);
  filter: drop-shadow(0 0 6px rgba(173, 222, 239, 0.5));
}

.progress-content {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-8);
}

.progress-text {
  display: flex;
  align-items: baseline;
  gap: var(--space-8);
}

.progress-text .text-hero-l {
  background: var(--color-accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
}

@media (max-width: 640px) {
  .progress-indicator {
    transform: scale(0.8);
  }
}
</style>
