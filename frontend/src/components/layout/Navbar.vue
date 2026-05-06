<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const theme = ref('light')

const navItems = [
  { name: 'Dashboard', path: '/', icon: 'dashboard' },
  { name: 'Experiments', path: '/experiments', icon: 'experiment' },
  { name: 'Visualization', path: '/visualization', icon: 'chart' },
  { name: 'Reports', path: '/reports', icon: 'report' }
]

const isActive = (path) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}

const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', theme.value)
  localStorage.setItem('theme', theme.value)
}

// Initialize theme on mount
onMounted(() => {
  // Check for saved theme preference or default to 'light'
  const savedTheme = localStorage.getItem('theme') || 'light'
  theme.value = savedTheme
  document.documentElement.setAttribute('data-theme', savedTheme)
})
</script>

<template>
  <nav class="navbar">
    <div class="navbar-container">
      <!-- Logo & Brand -->
      <router-link to="/" class="navbar-brand">
        <div class="logo">
          <img src="../../assets/ChartMind.png" alt="ChartMind Logo" />
        </div>
        <div class="brand-text">
          <span class="brand-name">ChartMind</span>
        </div>
      </router-link>

      <!-- Navigation Links -->
      <div class="navbar-links">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          :class="{ active: isActive(item.path) }"
        >
          <span class="nav-icon" :data-icon="item.icon"></span>
          <span class="nav-text">{{ item.name }}</span>
        </router-link>
      </div>

      <!-- Right Actions -->
      <div class="navbar-actions">
        <button class="theme-toggle" @click="toggleTheme" aria-label="Toggle theme">
          <svg v-if="theme === 'light'" width="20" height="20" viewBox="0 0 20 20" fill="none">
            <circle cx="10" cy="10" r="4" stroke="currentColor" stroke-width="1.5"/>
            <path d="M10 2V4M10 16V18M18 10H16M4 10H2M15.66 4.34L14.24 5.76M5.76 14.24L4.34 15.66M15.66 15.66L14.24 14.24M5.76 5.76L4.34 4.34" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <svg v-else width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M17 10.5C16.1 13.5 13.4 15.7 10.2 15.7C6.3 15.7 3.1 12.5 3.1 8.6C3.1 5.4 5.3 2.7 8.3 1.8C5.1 2.5 2.7 5.3 2.7 8.7C2.7 12.7 5.9 16 9.9 16C13.3 16 16.1 13.6 16.8 10.4L17 10.5Z" fill="currentColor"/>
          </svg>
        </button>
        
        <div class="status-indicator">
          <div class="status-dot"></div>
          <span class="status-text">Ready</span>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--color-soft-border);
  transition: all var(--transition-base);
}

[data-theme="dark"] .navbar {
  background: rgba(26, 40, 40, 0.8);
}

.navbar-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 var(--space-32);
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-48);
}

/* Brand */
.navbar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-12);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.navbar-brand:hover {
  opacity: 0.8;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo img {
  height: 36px;
  width: auto;
  object-fit: contain;
}

.brand-text {
  display: flex;
  align-items: baseline;
  gap: var(--space-4);
}

.brand-name {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.5px;
}

/* Navigation Links */
.navbar-links {
  display: flex;
  align-items: center;
  gap: var(--space-8);
  flex: 1;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-8);
  padding: var(--space-8) var(--space-20);
  border-radius: var(--radius-medium);
  font-size: var(--text-control-size);
  font-weight: 500;
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
  position: relative;
}

.nav-link:hover {
  color: var(--color-text-primary);
  background: var(--color-surface-accent);
}

.nav-link.active {
  color: var(--color-text-primary);
  font-weight: 600;
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: var(--space-20);
  right: var(--space-20);
  height: 2px;
  background: var(--color-accent-gradient);
  border-radius: 2px;
}

.nav-icon::before {
  content: '';
  display: inline-block;
  width: 18px;
  height: 18px;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}

.nav-icon[data-icon="dashboard"]::before {
  background-image: url("data:image/svg+xml,%3Csvg width='18' height='18' viewBox='0 0 18 18' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Crect x='2' y='2' width='6' height='6' rx='1' stroke='currentColor' stroke-width='1.5'/%3E%3Crect x='10' y='2' width='6' height='6' rx='1' stroke='currentColor' stroke-width='1.5'/%3E%3Crect x='2' y='10' width='6' height='6' rx='1' stroke='currentColor' stroke-width='1.5'/%3E%3Crect x='10' y='10' width='6' height='6' rx='1' stroke='currentColor' stroke-width='1.5'/%3E%3C/svg%3E");
}

.nav-icon[data-icon="experiment"]::before {
  background-image: url("data:image/svg+xml,%3Csvg width='18' height='18' viewBox='0 0 18 18' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M6 2H12V7L15 14C15.5 15 15 16 14 16H4C3 16 2.5 15 3 14L6 7V2Z' stroke='currentColor' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
}

.nav-icon[data-icon="chart"]::before {
  background-image: url("data:image/svg+xml,%3Csvg width='18' height='18' viewBox='0 0 18 18' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M2 14L6 10L10 12L16 6' stroke='currentColor' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3Cpath d='M12 6H16V10' stroke='currentColor' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
}

.nav-icon[data-icon="report"]::before {
  background-image: url("data:image/svg+xml,%3Csvg width='18' height='18' viewBox='0 0 18 18' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M4 2H10L14 6V14C14 15.1 13.1 16 12 16H4C2.9 16 2 15.1 2 14V4C2 2.9 2.9 2 4 2Z' stroke='currentColor' stroke-width='1.5'/%3E%3Cpath d='M10 2V6H14' stroke='currentColor' stroke-width='1.5' stroke-linecap='round'/%3E%3C/svg%3E");
}

/* Actions */
.navbar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-20);
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  border-radius: var(--radius-small);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.theme-toggle:hover {
  background: var(--color-surface-accent);
  color: var(--color-text-primary);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: var(--space-8);
  padding: var(--space-6) var(--space-14);
  background: var(--color-surface-accent);
  border-radius: var(--radius-pill);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-success-green);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.status-text {
  font-size: var(--text-micro-size);
  font-weight: 600;
  color: var(--color-text-secondary);
  letter-spacing: 0.3px;
}

/* Responsive */
@media (max-width: 1023px) {
  .navbar-container {
    padding: 0 var(--space-24);
    gap: var(--space-24);
  }

  .logo img {
    height: 32px;
  }

  .navbar-links {
    gap: var(--space-4);
  }

  .nav-text {
    display: none;
  }

  .nav-link {
    padding: var(--space-10);
  }

  .nav-link.active::after {
    display: none;
  }
}

@media (max-width: 640px) {
  .navbar-container {
    padding: 0 var(--space-20);
    height: 56px;
  }

  .logo img {
    height: 28px;
  }

  .brand-text {
    display: none;
  }

  .status-text {
    display: none;
  }

  .navbar-actions {
    gap: var(--space-12);
  }
}
</style>
