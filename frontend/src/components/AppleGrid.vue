<template>
  <div :class="gridClasses">
    <slot />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  columns: {
    type: [Number, Object],
    default: () => ({
      mobile: 1,
      tablet: 2,
      desktop: 3
    })
  },
  gap: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  }
})

const gridClasses = computed(() => {
  const classes = ['apple-grid']
  
  // Gap classes
  classes.push(`apple-grid--gap-${props.gap}`)
  
  // Column classes (if number provided)
  if (typeof props.columns === 'number') {
    classes.push(`apple-grid--cols-${props.columns}`)
  } else {
    classes.push('apple-grid--responsive')
  }
  
  return classes.join(' ')
})
</script>

<style scoped>
.apple-grid {
  display: grid;
  width: 100%;
}

/* Gap Sizes */
.apple-grid--gap-small {
  gap: var(--space-12);
}

.apple-grid--gap-medium {
  gap: var(--space-20);
}

.apple-grid--gap-large {
  gap: var(--space-32);
}

/* Fixed Column Counts */
.apple-grid--cols-1 {
  grid-template-columns: repeat(1, 1fr);
}

.apple-grid--cols-2 {
  grid-template-columns: repeat(2, 1fr);
}

.apple-grid--cols-3 {
  grid-template-columns: repeat(3, 1fr);
}

.apple-grid--cols-4 {
  grid-template-columns: repeat(4, 1fr);
}

.apple-grid--cols-5 {
  grid-template-columns: repeat(5, 1fr);
}

.apple-grid--cols-6 {
  grid-template-columns: repeat(6, 1fr);
}

/* Responsive Grid (default behavior) */
.apple-grid--responsive {
  grid-template-columns: repeat(1, 1fr);
}

@media (min-width: 641px) {
  .apple-grid--responsive {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .apple-grid--responsive {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Responsive adjustments for fixed columns */
@media (max-width: 640px) {
  .apple-grid--cols-2,
  .apple-grid--cols-3,
  .apple-grid--cols-4,
  .apple-grid--cols-5,
  .apple-grid--cols-6 {
    grid-template-columns: repeat(1, 1fr);
  }
}

@media (min-width: 641px) and (max-width: 1023px) {
  .apple-grid--cols-3,
  .apple-grid--cols-4,
  .apple-grid--cols-5,
  .apple-grid--cols-6 {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .apple-grid--cols-5,
  .apple-grid--cols-6 {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (min-width: 1441px) {
  .apple-grid--cols-5 {
    grid-template-columns: repeat(5, 1fr);
  }
  
  .apple-grid--cols-6 {
    grid-template-columns: repeat(6, 1fr);
  }
}
</style>
