<script setup lang="ts">
import {
  LayoutDashboard,
  ArrowLeftRight,
  Target,
  Settings,
  Wallet
} from 'lucide-vue-next'

const navigationItems = [
  { label: 'Dashboard', icon: LayoutDashboard, active: true },
  { label: 'Transactions', icon: ArrowLeftRight, active: false },
  { label: 'Savings Goals', icon: Target, active: false },
  { label: 'Settings', icon: Settings, active: false }
]
</script>

<template>
  <aside class="flex h-screen w-64 flex-col border-r border-slate-200 bg-white p-5">
    <div class="mb-10 flex items-center gap-3">
      <div class="rounded-xl bg-blue-600 p-2 text-white">
        <Wallet :size="24" />
      </div>

      <div>
        <h1 class="text-xl font-bold text-slate-900">FinWise</h1>
        <p class="text-xs text-slate-500">AI Finance Assistant</p>
      </div>
    </div>

    <p class="mb-3 px-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
      Menu
    </p>

    <nav class="space-y-2">
      <a
        v-for="item in navigationItems"
        :key="item.label"
        href="#"
        class="flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium transition"
        :class="
          item.active
            ? 'bg-blue-50 text-blue-700'
            : 'text-slate-600 hover:bg-slate-50'
        "
      >
        <component :is="item.icon" :size="20" />
        {{ item.label }}
      </a>
    </nav>

    <div class="mt-auto rounded-xl bg-slate-50 p-4">
      <p class="text-sm font-semibold text-slate-800">FinWise AI</p>
      <p class="mt-1 text-xs leading-5 text-slate-500">
        Smarter insights for better financial decisions.
      </p>
    </div>
  </aside>
</template>