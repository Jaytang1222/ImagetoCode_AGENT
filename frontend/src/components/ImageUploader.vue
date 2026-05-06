<template>
  <div class="image-uploader">
    <div 
      :class="['upload-zone', { 'upload-zone--dragging': isDragging, 'upload-zone--has-image': imagePreview }]"
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        accept="image/png,image/jpeg,image/jpg"
        @change="handleFileSelect"
        style="display: none;"
      />
      
      <div v-if="!imagePreview" class="upload-prompt">
        <svg class="upload-icon" width="48" height="48" viewBox="0 0 48 48" fill="none">
          <path d="M24 8V32M24 8L16 16M24 8L32 16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M8 32V36C8 38.2091 9.79086 40 12 40H36C38.2091 40 40 38.2091 40 36V32" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <p class="text-body-emphasis">拖拽图片到此处或点击上传</p>
        <p class="text-control text-secondary">支持 PNG、JPG 格式</p>
      </div>
      
      <div v-else class="image-preview">
        <img :src="imagePreview" alt="上传的图片" />
        <div class="image-overlay">
          <AppleButton variant="ghost" size="small" @click.stop="removeImage">
            更换图片
          </AppleButton>
        </div>
      </div>
    </div>
    
    <div v-if="error" class="upload-error">
      <p class="text-control" style="color: #ff3b30;">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppleButton from './AppleButton.vue'

const props = defineProps({
  maxSize: {
    type: Number,
    default: 10 * 1024 * 1024 // 10MB
  }
})

const emit = defineEmits(['upload', 'remove'])

const fileInput = ref(null)
const imagePreview = ref(null)
const isDragging = ref(false)
const error = ref('')
const uploadedFile = ref(null)

const validateFile = (file) => {
  error.value = ''
  
  if (!file) {
    return false
  }
  
  const validTypes = ['image/png', 'image/jpeg', 'image/jpg']
  if (!validTypes.includes(file.type)) {
    error.value = '请上传 PNG 或 JPG 格式的图片'
    return false
  }
  
  if (file.size > props.maxSize) {
    error.value = `图片大小不能超过 ${props.maxSize / 1024 / 1024}MB`
    return false
  }
  
  return true
}

const processFile = (file) => {
  if (!validateFile(file)) {
    return
  }
  
  uploadedFile.value = file
  
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
    emit('upload', file, e.target.result)
  }
  reader.readAsDataURL(file)
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  processFile(file)
}

const handleDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  processFile(file)
}

const triggerFileInput = () => {
  if (!imagePreview.value) {
    fileInput.value.click()
  }
}

const removeImage = () => {
  imagePreview.value = null
  uploadedFile.value = null
  error.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  emit('remove')
}

defineExpose({
  removeImage
})
</script>

<style scoped>
.image-uploader {
  width: 100%;
}

.upload-zone {
  width: 100%;
  min-height: 360px;
  background: linear-gradient(135deg, #f8faf9 0%, #ffffff 100%);
  border: 2px dashed var(--color-soft-border);
  border-radius: var(--radius-large);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-base);
  position: relative;
  overflow: hidden;
}

.upload-zone:hover {
  border-color: var(--color-primary-blue);
  background: linear-gradient(135deg, rgba(173, 222, 239, 0.05) 0%, rgba(165, 231, 165, 0.05) 100%);
  box-shadow: var(--shadow-subtle);
}

.upload-zone--dragging {
  border-color: var(--color-primary-green);
  background: linear-gradient(135deg, rgba(165, 231, 165, 0.1) 0%, rgba(173, 222, 239, 0.1) 100%);
  box-shadow: var(--shadow-glow-green);
}

.upload-zone--has-image {
  border-style: solid;
  border-color: var(--color-primary-blue);
  cursor: default;
  padding: 0;
  min-height: 440px;
  background: var(--color-graphite-a);
}

.upload-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-12);
  padding: var(--space-32);
  text-align: center;
}

.upload-icon {
  color: var(--color-primary-blue);
  margin-bottom: var(--space-8);
  filter: drop-shadow(0 2px 4px rgba(173, 222, 239, 0.3));
}

.image-preview {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 500px;
  object-fit: contain;
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(165, 231, 165, 0.9) 0%, rgba(173, 222, 239, 0.9) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity var(--transition-base);
  backdrop-filter: blur(4px);
}

.upload-zone--has-image:hover .image-overlay {
  opacity: 1;
}

.upload-error {
  margin-top: var(--space-12);
  padding: var(--space-12) var(--space-20);
  background: linear-gradient(135deg, rgba(255, 59, 48, 0.1) 0%, rgba(255, 149, 0, 0.1) 100%);
  border-radius: var(--radius-medium);
  border-left: 3px solid #ff3b30;
}

@media (max-width: 640px) {
  .upload-zone {
    min-height: 240px;
  }
  
  .upload-zone--has-image {
    min-height: 300px;
  }
  
  .image-preview img {
    max-height: 300px;
  }
}
</style>
