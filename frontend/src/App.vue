<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import {
  Wallet,
  TrendingUp,
  TrendingDown,
  PiggyBank
} from 'lucide-vue-next'

import { getDashboardSummary } from './services/dashboardService'

import type { DashboardSummary } from './types/dashboard'

const summary = ref<DashboardSummary | null>(null)

const loading = ref(true)
const error = ref('')

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2
  }).format(amount)
}

const summaryCards = computed(() => {
  if (!summary.value) return []

  return [
    {
      title: 'Total Balance',
      amount: formatCurrency(summary.value.balance),
      description: 'Your current net balance',
      icon: Wallet,
      iconColor: 'bg-blue-50 text-blue-600'
    },
    {
      title: 'Total Income',
      amount: formatCurrency(summary.value.total_income),
      description: 'Income received',
      icon: TrendingUp,
      iconColor: 'bg-green-50 text-green-600'
    },
    {
      title: 'Total Expenses',
      amount: formatCurrency(summary.value.total_expenses),
      description: 'Total expenses',
      icon: TrendingDown,
      iconColor: 'bg-red-50 text-red-600'
    },
    {
      title: 'Savings Rate',
      amount: `${summary.value.savings_rate}%`,
      description: 'Percentage of income saved',
      icon: PiggyBank,
      iconColor: 'bg-purple-50 text-purple-600'
    }
  ]
})

const loadDashboard = async () => {
  loading.value = true
  error.value = ''

  try {
    summary.value = await getDashboardSummary()
  } catch (err) {
    console.error('Dashboard API error:', err)
    error.value = 'Unable to load dashboard data. Please check the backend.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<template>
<section>
  <div v-if="loading" class="py-10 text-center text-slate-500">
    Loading financial data...
  </div>

  <div v-else-if="error" class="rounded-xl bg-red-50 p-5 text-red-600">
    {{ error }}

    <button
      @click="loadDashboard"
      class="ml-3 font-semibold underline"
    >
      Retry
    </button>
  </div>

  <div
    v-else
    class="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4"
  >
    <SummaryCard
      v-for="card in summaryCards"
      :key="card.title"
      v-bind="card"
    />
  </div>
</section>
</template>