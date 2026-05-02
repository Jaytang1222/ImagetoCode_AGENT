<template>
  <div class="apple-input-wrapper">
    <label v-if="label" :for="inputId" class="apple-input__label">
      {{ label }}
    </label>
    <input
      :id="inputId"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="inputClasses"
      @input="handleInput"
      @focus="handleFocus"
      @blur="handleBlur"
    />
    <span v-if="helperText" class="apple-input__helper">
      {{ helperText }}
    </span>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  helperText: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  error: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'focus', 'blur'])

const inputId = `apple-input-${Math.random().toString(36).substr(2, 9)}`
const isFocused = ref(false)

const inputClasses = computed(() => {
  const classes = ['apple-input']
  
  if (props.disabled) {
    classes.push('apple-input--disabled')
  }
  
  if (props.error) {
    classes.push('apple-input--error')
  }
  
  if (isFocused.value) {
    classes.push('apple-input--focused')
  }
  
  return classes.join(' ')
})

const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
}

const handleFocus = (event) => {
  isFocused.value = true
  emit('focus', event)
}

const handleBlur = (event) => {
  isFocused.value = false
  emit('blur', event)
}
</script>

<style scoped>
.apple-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--space-10);
}

.apple-input__label {
  font-family: var(--font-text);
  font-size: var(--text-control-size);
  font-weight: 600;
  line-height: var(--text-control-line);
  letter-spacing: var(--text-control-spacing);
  color: var(--color-text-primary);
}

.apple-input {
  font-family: var(--font-text);
  font-size: var(--text-body-size);
  font-weight: var(--text-body-weight);
  line-height: var(--text-body-line);
  letter-spacing: var(--text-body-spacing);
  color: var(--color-text-primary);
  background-color: var(--color-white);
  border: 2px solid var(--color-soft-border);
  border-radius: var(--radius-medium);
  padding: var(--space-12) var(--space-17);
  transition: all var(--transition-base);
  outline: none;
}

.apple-input::placeholder {
  color: var(--color-text-secondary);
}

.apple-input:hover:not(.apple-input--disabled) {
  border-color: var(--color-primary-blue);
  background-color: rgba(173, 222, 239, 0.03);
}

.apple-input--focused {
  border-color: var(--color-primary-blue);
  box-shadow: 0 0 0 4px rgba(173, 222, 239, 0.15);
  background-color: var(--color-white);
}

.apple-input--error {
  border-color: #ef5350;
}

.apple-input--error:focus {
  box-shadow: 0 0 0 4px rgba(239, 83, 80, 0.15);
}

.apple-input--disabled {
  background-color: var(--color-pale-gray);
  color: var(--color-text-secondary);
  cursor: not-allowed;
  opacity: 0.6;
  border-color: var(--color-soft-border);
}

.apple-input__helper {
  font-family: var(--font-text);
  font-size: var(--text-micro-size);
  font-weight: var(--text-micro-weight);
  line-height: var(--text-micro-line);
  letter-spacing: var(--text-micro-spacing);
  color: var(--color-secondary-gray);
}
</style>
