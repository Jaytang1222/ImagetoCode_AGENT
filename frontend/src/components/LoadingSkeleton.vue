<script setup>
defineProps({
  type: {
    type: String,
    default: 'card', // card, text, chart, image
    validator: (value) => ['card', 'text', 'chart', 'image', 'list'].includes(value)
  },
  count: {
    type: Number,
    default: 1
  }
})
</script>

<template>
  <div class="skeleton-wrapper">
    <!-- Card Skeleton -->
    <div v-if="type === 'card'" class="skeleton-card" v-for="n in count" :key="n">
      <div class="skeleton-header">
        <div class="skeleton-circle"></div>
        <div class="skeleton-lines">
          <div class="skeleton-line short"></div>
          <div class="skeleton-line shorter"></div>
        </div>
      </div>
      <div class="skeleton-body">
        <div class="skeleton-line"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line medium"></div>
      </div>
    </div>

    <!-- Text Skeleton -->
    <div v-if="type === 'text'" class="skeleton-text" v-for="n in count" :key="n">
      <div class="skeleton-line"></div>
      <div class="skeleton-line medium"></div>
      <div class="skeleton-line short"></div>
    </div>

    <!-- Chart Skeleton -->
    <div v-if="type === 'chart'" class="skeleton-chart">
      <div class="skeleton-chart-header">
        <div class="skeleton-line short"></div>
      </div>
      <div class="skeleton-chart-body">
        <div class="skeleton-bars">
          <div class="skeleton-bar" style="height: 60%"></div>
          <div class="skeleton-bar" style="height: 80%"></div>
          <div class="skeleton-bar" style="height: 45%"></div>
          <div class="skeleton-bar" style="height: 90%"></div>
          <div class="skeleton-bar" style="height: 70%"></div>
        </div>
      </div>
    </div>

    <!-- Image Skeleton -->
    <div v-if="type === 'image'" class="skeleton-image"></div>

    <!-- List Skeleton -->
    <div v-if="type === 'list'" class="skeleton-list">
      <div class="skeleton-list-item" v-for="n in count" :key="n">
        <div class="skeleton-circle small"></div>
        <div class="skeleton-line"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.skeleton-wrapper {
  width: 100%;
}

/* Base Skeleton Styles */
.skeleton-line,
.skeleton-circle,
.skeleton-card,
.skeleton-chart,
.skeleton-image,
.skeleton-bar {
  background: linear-gradient(
    90deg,
    rgba(216, 229, 229, 0.3) 0%,
    rgba(216, 229, 229, 0.5) 50%,
    rgba(216, 229, 229, 0.3) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: var(--radius-small);
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

/* Card Skeleton */
.skeleton-card {
  padding: var(--space-24);
  background: var(--color-surface-light);
  border-radius: var(--radius-large);
  border: 1px solid var(--color-soft-border);
  margin-bottom: var(--space-16);
}

.skeleton-header {
  display: flex;
  gap: var(--space-16);
  margin-bottom: var(--space-20);
}

.skeleton-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  flex-shrink: 0;
}

.skeleton-circle.small {
  width: 32px;
  height: 32px;
}

.skeleton-lines {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-8);
}

.skeleton-line {
  height: 16px;
  width: 100%;
}

.skeleton-line.short {
  width: 60%;
}

.skeleton-line.shorter {
  width: 40%;
}

.skeleton-line.medium {
  width: 80%;
}

.skeleton-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-12);
}

/* Text Skeleton */
.skeleton-text {
  display: flex;
  flex-direction: column;
  gap: var(--space-12);
  margin-bottom: var(--space-16);
}

/* Chart Skeleton */
.skeleton-chart {
  background: var(--color-surface-light);
  border-radius: var(--radius-large);
  padding: var(--space-24);
  border: 1px solid var(--color-soft-border);
}

.skeleton-chart-header {
  margin-bottom: var(--space-24);
}

.skeleton-chart-body {
  height: 300px;
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  padding: var(--space-20);
}

.skeleton-bars {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  gap: var(--space-16);
  width: 100%;
  height: 100%;
}

.skeleton-bar {
  flex: 1;
  border-radius: var(--radius-small);
}

/* Image Skeleton */
.skeleton-image {
  width: 100%;
  height: 300px;
  border-radius: var(--radius-large);
}

/* List Skeleton */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-12);
}

.skeleton-list-item {
  display: flex;
  align-items: center;
  gap: var(--space-16);
  padding: var(--space-16);
  background: var(--color-surface-light);
  border-radius: var(--radius-medium);
  border: 1px solid var(--color-soft-border);
}
</style>
