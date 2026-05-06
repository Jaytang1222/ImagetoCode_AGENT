<template>
  <a 
    :href="href"
    :class="linkClasses"
    :target="target"
    :rel="target === '_blank' ? 'noopener noreferrer' : undefined"
    @click="handleClick"
  >
    <slot />
  </a>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  href: {
    type: String,
    default: '#'
  },
  variant: {
    type: String,
    default: 'link',
    validator: (value) => ['link', 'action', 'bright'].includes(value)
  },
  underline: {
    type: String,
    default: 'hover',
    validator: (value) => ['always', 'hover', 'none'].includes(value)
  },
  target: {
    type: String,
    default: undefined
  }
})

const emit = defineEmits(['click'])

const linkClasses = computed(() => {
  const classes = ['apple-link']
  
  // Variant classes
  classes.push(`apple-link--${props.variant}`)
  
  // Underline classes
  classes.push(`apple-link--underline-${props.underline}`)
  
  return classes.join(' ')
})

const handleClick = (event) => {
  emit('click', event)
}
</script>

<style scoped>
.apple-link {
  font-family: var(--font-text);
  font-size: inherit;
  font-weight: inherit;
  line-height: inherit;
  cursor: pointer;
  transition: all var(--transition-fast);
  text-decoration: none;
  position: relative;
}

.apple-link:focus-visible {
  outline: 2px solid var(--color-action-blue);
  outline-offset: 2px;
  border-radius: 2px;
}

/* Variant: Link (Body Link Blue) */
.apple-link--link {
  color: var(--color-link-blue);
}

.apple-link--link:hover {
  color: var(--color-action-blue);
}

/* Variant: Action (Action Blue) */
.apple-link--action {
  color: var(--color-action-blue);
}

.apple-link--action:hover {
  color: var(--color-link-blue);
}

/* Variant: Bright (High-Luminance Link Blue) */
.apple-link--bright {
  color: var(--color-bright-link-blue);
}

.apple-link--bright:hover {
  color: var(--color-action-blue);
}

/* Underline: Always */
.apple-link--underline-always {
  text-decoration: underline;
}

/* Underline: Hover */
.apple-link--underline-hover {
  text-decoration: none;
}

.apple-link--underline-hover:hover {
  text-decoration: underline;
}

/* Underline: None */
.apple-link--underline-none {
  text-decoration: none;
}
</style>
