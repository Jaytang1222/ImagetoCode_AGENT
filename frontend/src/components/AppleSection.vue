<template>
  <section :class="sectionClasses">
    <slot />
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  background: {
    type: String,
    default: 'white',
    validator: (value) => ['black', 'white', 'pale-gray', 'graphite-a', 'graphite-b', 'surface', 'dark', 'gradient-hero'].includes(value)
  },
  spacing: {
    type: String,
    default: 'large',
    validator: (value) => ['small', 'medium', 'large', 'xlarge'].includes(value)
  }
})

const sectionClasses = computed(() => {
  const classes = ['apple-section']
  
  // Background classes
  classes.push(`apple-section--bg-${props.background}`)
  
  // Spacing classes
  classes.push(`apple-section--spacing-${props.spacing}`)
  
  return classes.join(' ')
})
</script>

<style scoped>
.apple-section {
  width: 100%;
  position: relative;
}

/* Background Colors */
.apple-section--bg-black {
  background-color: var(--color-black);
  color: var(--color-white);
}

.apple-section--bg-white {
  background-color: var(--color-white);
  color: var(--color-near-black);
}

.apple-section--bg-pale-gray {
  background-color: var(--color-pale-gray);
  color: var(--color-near-black);
}

.apple-section--bg-surface {
  background-color: var(--color-surface-accent);
  color: var(--color-near-black);
}

.apple-section--bg-dark {
  background: linear-gradient(180deg, var(--color-graphite-a) 0%, var(--color-graphite-b) 100%);
  color: var(--color-white);
}

.apple-section--bg-gradient-hero {
  background: linear-gradient(135deg, #e8f5e8 0%, #e3f4f9 50%, #f0f9f9 100%);
  color: var(--color-near-black);
  position: relative;
  overflow: hidden;
}

.apple-section--bg-gradient-hero::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(165, 231, 165, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.apple-section--bg-gradient-hero::after {
  content: '';
  position: absolute;
  bottom: -50%;
  left: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(173, 222, 239, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.apple-section--bg-graphite-a {
  background-color: var(--color-graphite-a);
  color: var(--color-white);
}

.apple-section--bg-graphite-b {
  background-color: var(--color-graphite-b);
  color: var(--color-white);
}

/* Spacing - Small */
.apple-section--spacing-small {
  padding-top: var(--space-32);
  padding-bottom: var(--space-32);
}

/* Spacing - Medium */
.apple-section--spacing-medium {
  padding-top: var(--space-48);
  padding-bottom: var(--space-48);
}

/* Spacing - Large */
.apple-section--spacing-large {
  padding-top: var(--space-64);
  padding-bottom: var(--space-64);
}

/* Spacing - XLarge */
.apple-section--spacing-xlarge {
  padding-top: var(--space-96);
  padding-bottom: var(--space-96);
}

/* Responsive spacing adjustments */
@media (max-width: 640px) {
  .apple-section--spacing-small {
    padding-top: var(--space-24);
    padding-bottom: var(--space-24);
  }

  .apple-section--spacing-medium {
    padding-top: var(--space-32);
    padding-bottom: var(--space-32);
  }

  .apple-section--spacing-large {
    padding-top: var(--space-48);
    padding-bottom: var(--space-48);
  }

  .apple-section--spacing-xlarge {
    padding-top: var(--space-64);
    padding-bottom: var(--space-64);
  }
}
</style>
