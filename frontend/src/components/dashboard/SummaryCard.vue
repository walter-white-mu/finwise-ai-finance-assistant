<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  title: string
  amount: string
  description: string
  icon: Component
  iconColor: string
}>()
</script>

<template>
  <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
    <div class="flex items-center justify-between">
      <p class="text-sm font-medium text-slate-500">
        {{ title }}
      </p>

      <div class="rounded-lg p-2" :class="iconColor">
        <component :is="icon" :size="20" />
      </div>
    </div>

    <h3 class="mt-4 text-2xl font-bold text-slate-900">
      {{ amount }}
    </h3>

    <p class="mt-2 text-xs text-slate-500">
      {{ description }}
    </p>
  </div>
</template>