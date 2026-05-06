<script setup>
import { computed } from 'vue'

const props = defineProps({
  agents: {
    type: Array,
    required: true
  },
  currentRound: {
    type: Number,
    default: 0
  },
  isRunning: {
    type: Boolean,
    default: false
  }
})

const getAgentIcon = (agentId) => {
  const icons = {
    agent1: 'M8 4L14 2L20 4L22 10L20 16L14 18L8 16L6 10L8 4Z',
    agent2: 'M12 4L20 8V16L12 20L4 16V8L12 4Z',
    agent3: 'M4 8L12 4L20 8L20 16L12 20L4 16L4 8Z',
    agent4: 'M12 2L22 8L22 16L12 22L2 16L2 8L12 2Z'
  }
  return icons[agentId] || icons.agent1
}

const getStatusColor = (status) => {
  const colors = {
    idle: '#d8e5e5',
    running: '#5cb8d9',
    completed: '#a5e7a5',
    error: '#ff6b6b'
  }
  return colors[status] || colors.idle
}

const getStatusLabel = (status) => {
  const labels = {
    idle: 'Idle',
    running: 'Running',
    completed: 'Done',
    error: 'Error'
  }
  return labels[status] || 'Unknown'
}
</script>

<template>
  <div class="pipeline-flow">
    <div class="flow-header">
      <div class="flow-title-section">
        <h3 class="flow-title">Multi-Agent Pipeline</h3>
        <p class="flow-subtitle">Real-time collaboration workflow</p>
      </div>
      <div v-if="isRunning" class="flow-round">
        <span class="round-label">Round</span>
        <span class="round-value">{{ currentRound }}</span>
      </div>
    </div>

    <div class="flow-container">
      <!-- Input Node -->
      <div class="flow-node input-node">
        <div class="node-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <rect x="4" y="4" width="16" height="16" rx="2" stroke="currentColor" stroke-width="2"/>
            <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="node-label">Input</div>
      </div>

      <!-- Arrow -->
      <div class="flow-arrow">
        <svg width="40" height="24" viewBox="0 0 40 24" fill="none">
          <path d="M0 12H35M35 12L28 5M35 12L28 19" stroke="#d8e5e5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <!-- Agent Nodes -->
      <div 
        v-for="(agent, index) in agents" 
        :key="agent.id"
        class="flow-segment"
      >
        <div 
          class="flow-node agent-node"
          :class="{ active: agent.status === 'running' }"
          :style="{ '--status-color': getStatusColor(agent.status) }"
        >
          <div class="node-status-indicator" :class="agent.status">
            <div v-if="agent.status === 'running'" class="status-pulse"></div>
          </div>
          <div class="node-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
              <path :d="getAgentIcon(agent.id)" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="node-content">
            <div class="node-title">{{ agent.title }}</div>
            <div class="node-description">{{ agent.description }}</div>
            <div class="node-status">{{ getStatusLabel(agent.status) }}</div>
          </div>
          <div v-if="agent.progress !== null" class="node-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${agent.progress}%` }"></div>
            </div>
          </div>
        </div>

        <!-- Arrow between agents -->
        <div v-if="index < agents.length - 1" class="flow-arrow">
          <svg width="40" height="24" viewBox="0 0 40 24" fill="none">
            <path 
              d="M0 12H35M35 12L28 5M35 12L28 19" 
              :stroke="agent.status === 'completed' ? '#a5e7a5' : '#d8e5e5'" 
              stroke-width="2" 
              stroke-linecap="round" 
              stroke-linejoin="round"
            />
          </svg>
        </div>
      </div>

      <!-- Arrow to output -->
      <div class="flow-arrow">
        <svg width="40" height="24" viewBox="0 0 40 24" fill="none">
          <path 
            d="M0 12H35M35 12L28 5M35 12L28 19" 
            :stroke="agents[agents.length - 1]?.status === 'completed' ? '#a5e7a5' : '#d8e5e5'" 
            stroke-width="2" 
            stroke-linecap="round" 
            stroke-linejoin="round"
          />
        </svg>
      </div>

      <!-- Output Node -->
      <div class="flow-node output-node">
        <div class="node-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
            <path d="M12 12L12 22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M12 12L2 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M12 12L22 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="node-label">Output</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pipeline-flow {
  background: linear-gradient(135deg, rgba(165, 231, 165, 0.05) 0%, rgba(173, 222, 239, 0.05) 100%);
  border-radius: var(--radius-large);
  padding: var(--space-32);
  border: 1px solid var(--color-soft-border);
  box-shadow: var(--shadow-medium);
}

.flow-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-32);
}

.flow-title-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.flow-title {
  font-size: var(--text-utility-size);
  font-weight: 600;
  color: var(--color-text-primary);
}

.flow-subtitle {
  font-size: var(--text-control-size);
  color: var(--color-text-secondary);
}

.flow-round {
  display: flex;
  align-items: center;
  gap: var(--space-12);
  padding: var(--space-10) var(--space-20);
  background: var(--color-surface-light);
  border-radius: var(--radius-pill);
  border: 2px solid var(--color-action-blue);
}

.round-label {
  font-size: var(--text-control-size);
  color: var(--color-text-secondary);
  font-weight: 500;
}

.round-value {
  font-size: var(--text-link-heading-size);
  font-weight: 700;
  color: var(--color-action-blue);
}

.flow-container {
  display: flex;
  align-items: center;
  gap: var(--space-12);
  overflow-x: auto;
  padding: var(--space-20) 0;
}

.flow-segment {
  display: flex;
  align-items: center;
  gap: var(--space-12);
}

.flow-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-8);
  padding: var(--space-16);
  background: var(--color-surface-light);
  border-radius: var(--radius-medium);
  border: 2px solid var(--color-soft-border);
  transition: all var(--transition-base);
  min-width: 100px;
}

.input-node,
.output-node {
  min-width: 80px;
}

.node-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
}

.node-label {
  font-size: var(--text-micro-size);
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.agent-node {
  position: relative;
  min-width: 160px;
  padding: var(--space-20);
  border-color: var(--status-color);
}

.agent-node.active {
  box-shadow: 0 0 0 3px rgba(92, 184, 217, 0.2);
  transform: translateY(-4px);
}

.node-status-indicator {
  position: absolute;
  top: var(--space-12);
  right: var(--space-12);
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--status-color);
}

.node-status-indicator.running {
  background: var(--color-action-blue);
}

.status-pulse {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 50%;
  border: 2px solid var(--color-action-blue);
  animation: pulse-ring 1.5s ease-out infinite;
}

@keyframes pulse-ring {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.8);
    opacity: 0;
  }
}

.node-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  text-align: center;
}

.node-title {
  font-size: var(--text-control-size);
  font-weight: 600;
  color: var(--color-text-primary);
}

.node-description {
  font-size: var(--text-micro-size);
  color: var(--color-text-secondary);
}

.node-status {
  font-size: var(--text-micro-size);
  font-weight: 600;
  color: var(--status-color);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: var(--space-4);
}

.node-progress {
  width: 100%;
  margin-top: var(--space-8);
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: var(--color-soft-border);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-action-blue);
  border-radius: 2px;
  transition: width var(--transition-base);
}

.flow-arrow {
  flex-shrink: 0;
}

/* Responsive */
@media (max-width: 1023px) {
  .flow-container {
    flex-direction: column;
    align-items: stretch;
  }

  .flow-segment {
    flex-direction: column;
  }

  .flow-arrow {
    transform: rotate(90deg);
    margin: var(--space-8) 0;
  }

  .agent-node {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .pipeline-flow {
    padding: var(--space-20);
  }

  .flow-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-16);
  }
}
</style>
