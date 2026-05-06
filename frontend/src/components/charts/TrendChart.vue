<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  title: {
    type: String,
    default: 'Score Trend'
  },
  height: {
    type: Number,
    default: 300
  }
})

const chartData = computed(() => {
  const labels = props.data.map((_, index) => `Round ${index + 1}`)
  const scores = props.data.map(item => item.score || 0)

  return {
    labels,
    datasets: [
      {
        label: 'Validation Score',
        data: scores,
        borderColor: '#5cb8d9',
        backgroundColor: 'rgba(92, 184, 217, 0.1)',
        borderWidth: 3,
        tension: 0.4,
        fill: true,
        pointRadius: 6,
        pointHoverRadius: 8,
        pointBackgroundColor: '#5cb8d9',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointHoverBackgroundColor: '#4aa8c9',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 3
      }
    ]
  }
})

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
          return `Score: ${(context.parsed.y * 100).toFixed(1)}%`
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 1,
      ticks: {
        callback: (value) => `${(value * 100).toFixed(0)}%`,
        color: '#6e7575',
        font: {
          size: 12
        }
      },
      grid: {
        color: 'rgba(216, 229, 229, 0.5)',
        drawBorder: false
      }
    },
    x: {
      ticks: {
        color: '#6e7575',
        font: {
          size: 12
        }
      },
      grid: {
        display: false
      }
    }
  },
  interaction: {
    intersect: false,
    mode: 'index'
  }
}))
</script>

<template>
  <div class="trend-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div v-if="data.length > 0" class="chart-stats">
        <div class="stat">
          <span class="stat-label">Latest</span>
          <span class="stat-value">{{ (data[data.length - 1]?.score * 100 || 0).toFixed(1) }}%</span>
        </div>
        <div class="stat">
          <span class="stat-label">Best</span>
          <span class="stat-value">{{ (Math.max(...data.map(d => d.score || 0)) * 100).toFixed(1) }}%</span>
        </div>
      </div>
    </div>
    <div class="chart-container" :style="{ height: `${height}px` }">
      <Line v-if="data.length > 0" :data="chartData" :options="chartOptions" />
      <div v-else class="chart-empty">
        <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
          <path d="M8 48L20 36L32 40L56 16" stroke="#d8e5e5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="20" cy="36" r="4" fill="#addeef"/>
          <circle cx="32" cy="40" r="4" fill="#a5e7a5"/>
          <circle cx="56" cy="16" r="4" fill="#5cb8d9"/>
        </svg>
        <p class="empty-text">No data available yet</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.trend-chart {
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

.chart-stats {
  display: flex;
  gap: var(--space-24);
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--space-4);
}

.stat-label {
  font-size: var(--text-micro-size);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: var(--text-link-heading-size);
  font-weight: 700;
  color: var(--color-action-blue);
}

.chart-container {
  position: relative;
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

  .chart-stats {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
