<script setup lang="ts">
import { onMounted, ref } from 'vue'
import HelloWorld from './components/HelloWorld.vue'
import api from './services/api'

const connection = ref<'loading' | 'connected' | 'error'>('loading')
const errorMessage = ref('')

async function checkConnection() {
  connection.value = 'loading'
  errorMessage.value = ''

  try {
    await api.getHealth()
    connection.value = 'connected'
  } catch (error) {
    connection.value = 'error'
    errorMessage.value = error instanceof Error ? error.message : 'Unable to reach backend'
  }
}

onMounted(checkConnection)
</script>

<template>
  <div class="connection-status" role="status" aria-live="polite">
    <span v-if="connection === 'loading'">Connecting to backend...</span>
    <span v-else-if="connection === 'connected'">Backend connected</span>
    <template v-else>
      <span>Backend unavailable: {{ errorMessage }}</span>
      <button type="button" @click="checkConnection">Retry</button>
    </template>
  </div>
  <HelloWorld />
</template>

<style scoped>
.connection-status {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem;
  overflow-wrap: anywhere;
}
</style>
