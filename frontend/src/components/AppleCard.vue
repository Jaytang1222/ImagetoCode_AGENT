<template>
  <div :class="cardClasses">
    <div v-if="$slots.image" class="apple-card__image">
      <slot name="image" />
    </div>
    <div class="apple-card__content">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'editorial',
    validator: (value) => ['editorial', 'product', 'dark'].includes(value)
  },
  hoverable: {
    type: Boolean,
    default: false
  }
})

const cardClasses = computed(() => {
  const classes = ['apple-card']
  
  // Variant classes
  classes.push(`apple-card--${props.variant}`)
  
  // Hoverable state
  if (props.hoverable) {
    classes.push('apple-card--hoverable')
  }
  
  return classes.join(' ')
})
</script>

<style scoped>
.apple-card {
  display: flex;
  flex-direction: column;
  border-radius: var(--radius-large);
  overflow: hidden;
  transition: all var(--transition-base);
}

/* Variant: Editorial */
.apple-card--editorial {
  background: linear-gradient(135deg, rgba(165, 231, 165, 0.05) 0%, rgba(173, 222, 239, 0.05) 100%);
  border: 1px solid rgba(173, 222, 239, 0.2);
  box-shadow: var(--shadow-subtle);
}

.apple-card--editorial .apple-card__content {
  padding: var(--space-32);
}

/* Variant: Product */
.apple-card--product {
  background-color: var(--color-white);
  border: 1px solid rgba(165, 231, 165, 0.2);
  box-shadow: var(--shadow-subtle);
}

.apple-card--product .apple-card__content {
  padding: var(--space-24);
}

/* Variant: Dark */
.apple-card--dark {
  background: linear-gradient(135deg, var(--color-graphite-a) 0%, var(--color-graphite-b) 100%);
  color: var(--color-white);
  border: 1px solid rgba(173, 222, 239, 0.15);
  box-shadow: var(--shadow-medium);
}

.apple-card--dark .apple-card__content {
  padding: var(--space-32);
}

/* Hoverable State */
.apple-card--hoverable {
  cursor: pointer;
}

.apple-card--hoverable:hover {
  transform: translateY(-2px);
}

.apple-card--editorial.apple-card--hoverable:hover {
  box-shadow: var(--shadow-strong);
  border-color: rgba(165, 231, 165, 0.4);
  transform: translateY(-4px);
}

.apple-card--product.apple-card--hoverable:hover {
  border-color: var(--color-primary-blue);
  box-shadow: var(--shadow-medium);
  transform: translateY(-4px);
}

.apple-card--dark.apple-card--hoverable:hover {
  background: linear-gradient(135deg, var(--color-graphite-b) 0%, var(--color-graphite-c) 100%);
  box-shadow: var(--shadow-strong);
  transform: translateY(-4px);
}

/* Image Container */
.apple-card__image {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-pale-gray);
}

.apple-card--dark .apple-card__image {
  background-color: var(--color-graphite-b);
}

.apple-card__image :deep(img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Content Container */
.apple-card__content {
  display: flex;
  flex-direction: column;
  gap: var(--space-12);
}
</style>
