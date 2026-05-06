<template>
  <div :class="containerClasses">
    <slot />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'default',
    validator: (value) => ['narrow', 'default', 'wide', 'full'].includes(value)
  },
  padding: {
    type: Boolean,
    default: true
  }
})

const containerClasses = computed(() => {
  const classes = ['apple-container']
  
  // Size classes
  classes.push(`apple-container--${props.size}`)
  
  // Padding control
  if (props.padding) {
    classes.push('apple-container--padded')
  }
  
  return classes.join(' ')
})
</script>

<style scoped>
.apple-container {
  width: 100%;
  margin-left: auto;
  margin-right: auto;
}

/* Size: Narrow (for reading content) */
.apple-container--narrow {
  max-width: 768px;
}

/* Size: Default (standard content) */
.apple-container--default {
  max-width: 1280px;
}

/* Size: Wide (marketing pages) */
.apple-container--wide {
  max-width: 1600px;
}

/* Size: Full (no max-width) */
.apple-container--full {
  max-width: none;
}

/* Padding */
.apple-container--padded {
  padding-left: var(--space-20);
  padding-right: var(--space-20);
}

/* Responsive padding adjustments */
@media (min-width: 641px) {
  .apple-container--padded {
    padding-left: var(--space-40);
    padding-right: var(--space-40);
  }
}

@media (min-width: 1024px) {
  .apple-container--padded {
    padding-left: var(--space-64);
    padding-right: var(--space-64);
  }
}

@media (min-width: 1440px) {
  .apple-container--padded {
    padding-left: var(--space-80);
    padding-right: var(--space-80);
  }
}
</style>
