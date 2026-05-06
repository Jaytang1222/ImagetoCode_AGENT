<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Radar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
)

const props = defineProps({
  dimensions: {
    type: Object,
    default: () => ({
      color: 0,
      text: 0,
      structure: 0,
      vlm: 0
    })
  },
  title: {
    type: String,
    default: 'Multi-Dimensional Analysis'
  },
  height: {
    type: Number,
    default: 350
  }
})

const chartData = computed(() => ({
  labels: ['Color Consistency', 'Text Accuracy', 'Structure Match', 'Visual Similarity'],
  datasets: [
    {
      label: 'Current Score',
      data: [
        props.dimensions.color || 0,
        props.dimensions.text || 0,
        props.dimensions.structure || 0,
        props.dimensions.vlm || 0
      ],
      backgroundColor: 'rgba(92, 184, 217, 0.2)',
      borderColor: '#5cb8d9',
      borderWidth: 3,
      pointBackgroundColor: '#5cb8d9',
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: 6,
      pointHoverRadius: 8,
      pointHoverBackgroundColor: '#4aa8c9',
      pointHoverBorderWidth: 3
    }
  ]
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(26, 47, 47, 0.95)',
      titleColor: '#a5e7a5',
      bodyColor: '#ffffff',
      borderColor: '#a5e7a5',
      borderWidth: 1,
      padding: 12,
      displayColors: false,
      callbacks: {
        label: (context) => {
          return `${context.label}: ${(context.parsed.r * 100).toFixed(1)}%`
        }
      }
    }
  },
  scales: {
    r: {
      beginAtZero: true,
      max: 1,
      ticks: {
        stepSize: 0.2,
        callback: (value) => `${(value * 100).toFixed(0)}%`,
        color: '#6e7575',
        font: {
          size: 11
        },
        backdropColor: 'transparent'
      },
      grid: {
        color: 'rgba(216, 229, 229, 0.5)'
      },
      angleLines: {
        color: 'rgba(216, 229, 229, 0.5)'
      },
      pointLabels: {
        color: '#3a4545',
        font: {
          size: 13,
          weight: '600'
        },
        padding: 12
      }
    }
  }
}))

const hasData = computed(() => {
  return Object.values(props.dimensions).some(v => v > 0)
})
</script>

<template>
  <div class="radar-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div v-if="hasData" class="chart-legend">
        <div class="legend-item">
          <div class="legend-dot"></div>
          <span class="legend-label">Current Round</span>
        </div>
      </div>
    </div>
    <div class="chart-container" :style="{ height: `${height}px` }">
      <Radar v-if="hasData" :data="chartData" :options="chartOptions" />
      <div v-else class="chart-empty">
        <svg width="80" height="80" viewBox="0 0 80 80" fill="none">
          <polygon points="40,10 70,30 60,60 20,60 10,30" stroke="#d8e5e5" stroke-width="2" fill="rgba(173, 222, 239, 0.1)"/>
          <circle cx="40" cy="10" r="4" fill="#addeef"/>
          <circle cx="70" cy="30" r="4" fill="#a5e7a5"/>
          <circle cx="60" cy="60" r="4" fill="#5cb8d9"/>
          <circle cx="20" cy="60" r="4" fill="#7dd17d"/>
          <circle cx="10" cy="30" r="4" fill="#7bc9e3"/>
        </svg>
        <p class="empty-text">Waiting for validation results</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.radar-chart {
  background: var(--color-surface-light);
  border-radius: var(--radius-large);
  padding: var(--space-24);
  border: 1px solid var(--color-soft-border);
  box-shadow: var(--shadow-subtle);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-20);
  padding-bottom: var(--space-12);
  border-bottom: 1px solid var(--color-soft-border);
}

.chart-title {
  font-size: var(--text-subhead-size);
  font-weight: 600;
  color: var(--color-text-primary);
}

.chart-legend {
  display: flex;
  gap: var(--space-16);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--space-8);
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--color-action-blue);
  border: 2px solid var(--color-surface-light);
  box-shadow: 0 0 0 1px var(--color-action-blue);
}

.legend-label {
  font-size: var(--text-micro-size);
  color: var(--color-text-secondary);
  font-weight: 500;
}

.chart-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: var(--space-16);
}

.empty-text {
  font-size: var(--text-control-size);
  color: var(--color-text-secondary);
}

@media (max-width: 640px) {
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-12);
  }
}
</style>
