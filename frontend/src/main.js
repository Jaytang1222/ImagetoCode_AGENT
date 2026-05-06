import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'

// Import design system styles in order
import './styles/reset.css'
import './styles/variables.css'
import './styles/typography.css'
import './styles/utilities.css'

import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')
