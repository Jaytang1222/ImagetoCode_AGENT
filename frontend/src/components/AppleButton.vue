<template>
  <button 
    :class="buttonClasses" 
    :disabled="disabled"
    @click="handleClick"
  >
    <slot />
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'dark', 'ghost', 'pill', 'capsule'].includes(value)
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large', 'xlarge'].includes(value)
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const buttonClasses = computed(() => {
  const classes = ['apple-button']
  
  // Variant classes
  classes.push(`apple-button--${props.variant}`)
  
  // Size classes
  classes.push(`apple-button--${props.size}`)
  
  // Disabled state
  if (props.disabled) {
    classes.push('apple-button--disabled')
  }
  
  return classes.join(' ')
})

const handleClick = (event) => {
  if (!props.disabled) {
    emit('click', event)
  }
}
</script>

<style scoped>
.apple-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-text);
  font-weight: 400;
  cursor: pointer;
  transition: all var(--transition-fast);
  border: none;
  outline: none;
  text-decoration: none;
  white-space: nowrap;
}

.apple-button:focus-visible {
  outline: 2px solid var(--color-action-blue);
  outline-offset: 2px;
}

.apple-button:active:not(.apple-button--disabled) {
  transform: scale(0.98);
}

/* Variant: Primary */
.apple-button--primary {
  background: var(--color-accent-gradient);
  color: var(--color-graphite-a);
  border-radius: var(--radius-medium);
  font-weight: 600;
  box-shadow: var(--shadow-subtle);
}

.apple-button--primary:hover:not(.apple-button--disabled) {
  box-shadow: var(--shadow-medium);
  transform: translateY(-1px);
}

/* Variant: Secondary */
.apple-button--secondary {
  background-color: var(--color-white);
  color: var(--color-action-blue);
  border: 2px solid var(--color-primary-blue);
  border-radius: var(--radius-medium);
  font-weight: 600;
}

.apple-button--secondary:hover:not(.apple-button--disabled) {
  background-color: var(--color-primary-blue);
  color: var(--color-graphite-a);
  box-shadow: var(--shadow-subtle);
}

/* Variant: Dark */
.apple-button--dark {
  background-color: var(--color-graphite-a);
  color: var(--color-white);
  border-radius: var(--radius-medium);
  font-weight: 600;
}

.apple-button--dark:hover:not(.apple-button--disabled) {
  background-color: var(--color-graphite-b);
}

/* Variant: Ghost */
.apple-button--ghost {
  background-color: transparent;
  color: var(--color-action-blue);
  border: 1px solid var(--color-soft-border);
  border-radius: var(--radius-medium);
}

.apple-button--ghost:hover:not(.apple-button--disabled) {
  border-color: var(--color-primary-blue);
  background-color: rgba(173, 222, 239, 0.1);
}

/* Variant: Pill */
.apple-button--pill {
  background-color: var(--color-action-blue);
  color: var(--color-white);
  border-radius: var(--radius-pill);
}

.apple-button--pill:hover:not(.apple-button--disabled) {
  background-color: var(--color-link-blue);
}

/* Variant: Capsule */
.apple-button--capsule {
  background-color: var(--color-action-blue);
  color: var(--color-white);
  border-radius: var(--radius-capsule-small);
}

.apple-button--capsule:hover:not(.apple-button--disabled) {
  background-color: var(--color-link-blue);
}

/* Size: Small */
.apple-button--small {
  padding: var(--space-6) var(--space-12);
  font-size: var(--text-control-size);
  line-height: var(--text-control-line);
  letter-spacing: var(--text-control-spacing);
}

/* Size: Medium */
.apple-button--medium {
  padding: var(--space-8) var(--space-20);
  font-size: var(--text-body-size);
  line-height: var(--text-body-line);
  letter-spacing: var(--text-body-spacing);
}

/* Size: Large */
.apple-button--large {
  padding: var(--space-14) var(--space-40);
  font-size: var(--text-link-heading-size);
  line-height: var(--text-link-heading-line);
  letter-spacing: var(--text-link-heading-spacing);
}

/* Size: XLarge */
.apple-button--xlarge {
  padding: var(--space-17) var(--space-48);
  font-size: var(--text-subhead-size);
  line-height: var(--text-subhead-line);
  letter-spacing: var(--text-subhead-spacing);
  font-weight: 600;
}

/* Disabled State */
.apple-button--disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
