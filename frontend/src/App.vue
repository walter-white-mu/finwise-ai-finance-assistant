<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import {
  Wallet,
  TrendingUp,
  TrendingDown,
  PiggyBank
} from 'lucide-vue-next'

import SummaryCard from './components/dashboard/SummaryCard.vue'
import MonthlyTrendsChart from './components/dashboard/MonthlyTrendsChart.vue'
import CategorySpendingChart from './components/dashboard/CategorySpendingChart.vue'
import {
  getDashboardSummary,
  getCategorySpending,
  getMonthlyTrends
} from './services/dashboardService'

import type { CategorySpending, DashboardSummary, MonthlyTrend } from './types/dashboard'

const summary = ref<DashboardSummary | null>(null)

const loading = ref(true)
const error = ref('')
const categories = ref<CategorySpending[]>([])
const monthlyTrends = ref<MonthlyTrend[]>([])
const categoriesLoading = ref(true)
const trendsLoading = ref(true)
const categoriesError = ref('')
const trendsError = ref('')

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

const loadCategories = async () => {
  categoriesLoading.value = true
  categoriesError.value = ''
  try {
    categories.value = await getCategorySpending()
  } catch (err) {
    console.error('Category spending API error:', err)
    categoriesError.value = 'Unable to load category spending.'
  } finally {
    categoriesLoading.value = false
  }
}

const loadMonthlyTrends = async () => {
  trendsLoading.value = true
  trendsError.value = ''
  try {
    monthlyTrends.value = await getMonthlyTrends()
  } catch (err) {
    console.error('Monthly trends API error:', err)
    trendsError.value = 'Unable to load monthly trends.'
  } finally {
    trendsLoading.value = false
  }
}

onMounted(() => {
  loadDashboard()
  loadCategories()
  loadMonthlyTrends()
})
</script>

<template>
<main class="min-h-screen space-y-8 p-5 sm:p-8">
<header>
  <h1 class="m-0 text-3xl font-bold text-slate-900">Dashboard</h1>
  <p class="mt-2 text-sm text-slate-500">Here's an overview of your finances.</p>
</header>
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
<section class="grid grid-cols-1 gap-5 xl:grid-cols-2">
  <MonthlyTrendsChart
    :data="monthlyTrends"
    :loading="trendsLoading"
    :error="trendsError"
    @retry="loadMonthlyTrends"
  />
  <CategorySpendingChart
    :data="categories"
    :loading="categoriesLoading"
    :error="categoriesError"
    @retry="loadCategories"
  />
</section>
</main>
</template>
