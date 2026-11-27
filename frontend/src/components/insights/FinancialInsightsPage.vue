<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { init } from '../dashboard/echarts'
import { formatDate, formatRupees } from '../../utils/money'
import { createBudget, deleteBudget, getBudgets, getMonthlyInsights } from '../../services/insightsService'
import type { ECharts, EChartsOption } from 'echarts'
import type { Anomaly, Budget, BudgetProgress, MonthlySummary, RecommendationsResponse, SpendingAnalysis } from '../../types/insights'

const selectedMonth = ref(new Date().toISOString().slice(0, 7))
const summary = ref<MonthlySummary | null>(null)
const spending = ref<SpendingAnalysis | null>(null)
const progress = ref<BudgetProgress[]>([])
const anomalies = ref<Anomaly[]>([])
const recommendations = ref<RecommendationsResponse | null>(null)
const budgets = ref<Budget[]>([])
const loading = ref(true)
const error = ref('')
const category = ref('')
const amount = ref('')
const savingBudget = ref(false)
const chartElement = ref<HTMLElement | null>(null)
let chart: ECharts | null = null
let resizeObserver: ResizeObserver | null = null

const chartColors = ['#2563eb', '#7c3aed', '#0891b2', '#ea580c', '#16a34a', '#db2777', '#ca8a04']
const monthName = computed(() => new Intl.DateTimeFormat('en-IN', { month: 'long', year: 'numeric' }).format(new Date(`${selectedMonth.value}-02`)))
const savingsRate = computed(() => Number(summary.value?.current.savings_rate ?? 0))
const chartOption = computed<EChartsOption>(() => ({
  color: chartColors,
  tooltip: { trigger: 'item', formatter: (item) => Array.isArray(item) ? '' : `${item.name}<br/>${formatRupees(String(item.value))} (${item.percent}%)` },
  series: [{
    type: 'pie', radius: ['60%', '82%'], center: ['50%', '50%'],
    itemStyle: { borderColor: '#fff', borderWidth: 3, borderRadius: 5 },
    label: { show: false },
    data: (spending.value?.categories ?? []).map((item) => ({ name: item.category, value: Number(item.amount) }))
  }]
}))

async function updateChart() {
  await nextTick()
  if (!chartElement.value || !spending.value?.categories.length) return
  chart ??= init(chartElement.value)
  if (!resizeObserver) {
    resizeObserver = new ResizeObserver(() => chart?.resize())
    resizeObserver.observe(chartElement.value)
  }
  chart.setOption(chartOption.value, true)
  chart.resize()
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [data, savedBudgets] = await Promise.all([getMonthlyInsights(selectedMonth.value), getBudgets()])
    summary.value = data.summary
    spending.value = data.spending
    progress.value = data.progress
    anomalies.value = data.anomalies
    recommendations.value = data.recommendations
    budgets.value = savedBudgets
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : 'Could not load financial insights.'
  } finally {
    loading.value = false
  }
}

async function addBudget() {
  if (!category.value.trim() || !amount.value) return
  savingBudget.value = true
  error.value = ''
  try {
    await createBudget(category.value.trim(), amount.value)
    category.value = ''
    amount.value = ''
    await load()
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : 'Could not save this budget.'
  } finally {
    savingBudget.value = false
  }
}

async function removeBudget(id: number) {
  try {
    await deleteBudget(id)
    await load()
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : 'Could not remove this budget.'
  }
}

function budgetId(name: string) {
  return budgets.value.find((item) => item.category === name)?.id
}

watch([chartOption, loading], updateChart)
watch(selectedMonth, load)
onMounted(() => {
  load()
})
onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  chart?.dispose()
  chart = null
})
</script>

<template>
  <section class="space-y-6" aria-labelledby="insights-title">
    <header class="flex flex-wrap items-end justify-between gap-4">
      <div><p class="text-xs font-semibold uppercase tracking-widest text-blue-600">Your money, in focus</p><h2 id="insights-title" class="mt-2 text-2xl font-bold text-slate-900">Financial insights</h2><p class="mt-1 text-sm text-slate-500">A clear view of your monthly financial health and spending habits.</p></div>
      <label class="text-sm font-medium text-slate-600">Month <input v-model="selectedMonth" type="month" class="ml-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-slate-800"></label>
    </header>

    <div v-if="error" role="alert" class="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"><span>{{ error }}</span><button class="font-semibold underline" @click="load">Retry</button></div>
    <div v-if="loading" class="rounded-xl border border-slate-200 bg-white p-10 text-center text-sm text-slate-500">Loading financial insights…</div>
    <template v-else-if="summary">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <article v-for="card in [
          { title: 'Income', value: summary.current.total_income, change: summary.income_change },
          { title: 'Expenses', value: summary.current.total_expenses, change: summary.expense_change },
          { title: 'Net savings', value: summary.current.net_savings, change: summary.savings_change }
        ]" :key="card.title" class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-sm font-medium text-slate-500">{{ card.title }} · {{ monthName }}</p><p class="mt-3 text-2xl font-bold text-slate-900">{{ formatRupees(card.value) }}</p>
          <p class="mt-2 text-xs" :class="(card.title === 'Expenses' ? Number(card.change) <= 0 : Number(card.change) >= 0) ? 'text-emerald-600' : 'text-rose-600'">{{ Number(card.change) > 0 ? '↑' : '↓' }} {{ formatRupees(String(Math.abs(Number(card.change)))) }} from last month</p>
        </article>
        <article class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><p class="text-sm font-medium text-slate-500">Savings rate</p><p class="mt-3 text-2xl font-bold text-slate-900">{{ savingsRate.toFixed(1) }}%</p><div class="mt-4 h-2 overflow-hidden rounded-full bg-slate-100"><div class="h-full rounded-full bg-violet-600 transition-all" :style="{ width: `${Math.max(0, Math.min(100, savingsRate))}%` }"></div></div><p class="mt-2 text-xs text-slate-500">{{ Number(summary.previous.savings_rate).toFixed(1) }}% last month</p></article>
      </div>

      <div class="grid grid-cols-1 gap-5 xl:grid-cols-2">
        <article class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><h3 class="font-semibold text-slate-900">Spending breakdown</h3><p class="mt-1 text-xs text-slate-500">Category share and change from the prior month</p>
          <div v-if="!spending?.categories.length" class="grid min-h-64 place-items-center text-sm text-slate-500">No expenses recorded for this month.</div>
          <div v-else class="grid grid-cols-1 items-center gap-3 sm:grid-cols-[minmax(190px,0.85fr)_1fr]"><div class="relative mx-auto h-64 w-full max-w-72"><div ref="chartElement" class="h-full w-full"></div><div class="pointer-events-none absolute inset-0 grid place-content-center text-center"><span class="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Total spent</span><strong class="mt-1 text-lg text-slate-900">{{ formatRupees(spending.total_expenses) }}</strong></div></div><div class="space-y-3"><div v-for="(item, index) in spending.categories" :key="item.category" class="flex items-center gap-2 text-xs"><span class="h-2.5 w-2.5 rounded-full" :style="{ backgroundColor: chartColors[index % chartColors.length] }"></span><span class="min-w-0 flex-1 truncate text-slate-600">{{ item.category }} · {{ Number(item.percentage).toFixed(1) }}%</span><span :class="Number(item.change) > 0 ? 'text-rose-600' : 'text-emerald-600'">{{ Number(item.change) > 0 ? '↑' : '↓' }} {{ formatRupees(String(Math.abs(Number(item.change)))) }}</span></div></div></div>
        </article>

        <article class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><div class="flex items-start justify-between"><div><h3 class="font-semibold text-slate-900">Budget progress</h3><p class="mt-1 text-xs text-slate-500">Monthly category limits</p></div><span class="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700">{{ progress.length }} categories</span></div>
          <div v-if="!progress.length" class="py-7 text-center text-sm text-slate-500">Set a category budget to start tracking.</div>
          <div v-else class="mt-5 space-y-5"><div v-for="item in progress" :key="item.category"><div class="flex justify-between text-xs"><span class="font-medium text-slate-700">{{ item.category }}<button v-if="budgetId(item.category)" class="ml-2 text-slate-400 hover:text-rose-600" :aria-label="`Remove ${item.category} budget`" @click="removeBudget(budgetId(item.category)!)">×</button></span><span :class="item.exceeded ? 'font-semibold text-rose-600' : 'text-slate-600'">{{ formatRupees(item.spent) }} / {{ formatRupees(item.budget) }}</span></div><div class="mt-2 h-2 overflow-hidden rounded-full bg-slate-100"><div class="h-full rounded-full" :class="item.exceeded ? 'bg-rose-500' : 'bg-blue-600'" :style="{ width: `${Math.min(100, Number(item.percentage_used))}%` }"></div></div><div class="mt-1 flex justify-between text-[11px] text-slate-500"><span>{{ item.exceeded ? 'Over budget' : `${formatRupees(item.remaining)} remaining` }}</span><span>{{ Number(item.percentage_used).toFixed(0) }}%</span></div></div></div>
          <form class="mt-5 flex gap-2 border-t border-slate-100 pt-4" @submit.prevent="addBudget"><input v-model="category" class="min-w-0 flex-1 rounded-lg border border-slate-200 px-3 py-2 text-xs" placeholder="Category" aria-label="Budget category" maxlength="100" required><input v-model="amount" class="w-32 rounded-lg border border-slate-200 px-3 py-2 text-xs" type="number" min="0.01" step="0.01" placeholder="Monthly limit" aria-label="Monthly budget amount" required><button class="rounded-lg bg-blue-600 px-3 py-2 text-sm font-semibold text-white disabled:opacity-60" :disabled="savingBudget">{{ savingBudget ? '…' : '+' }}</button></form>
        </article>
      </div>

      <div class="grid grid-cols-1 gap-5 xl:grid-cols-2">
        <article class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><div class="flex items-start justify-between"><div><h3 class="font-semibold text-slate-900">Unusual activity</h3><p class="mt-1 text-xs text-slate-500">Large transactions compared with category history</p></div><span v-if="anomalies.length" class="rounded-full bg-rose-50 px-2.5 py-1 text-xs font-semibold text-rose-700">{{ anomalies.length }}</span></div><p v-if="!anomalies.length" class="mt-6 rounded-lg bg-emerald-50 p-4 text-sm text-emerald-800">No unusually large expenses detected this month.</p><div v-for="item in anomalies" :key="item.transaction_id" class="mt-4 flex items-start gap-3 border-t border-slate-100 pt-4"><span class="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-amber-50 font-bold text-amber-700">!</span><div class="min-w-0 flex-1"><div class="flex justify-between gap-3 text-sm"><strong class="truncate text-slate-800">{{ item.description }} · {{ item.category }}</strong><strong class="shrink-0">{{ formatRupees(item.amount) }}</strong></div><p class="mt-1 text-xs text-slate-500">{{ item.reason }}</p><p class="mt-1 text-[11px] text-slate-400">{{ formatDate(item.transaction_date) }}</p></div></div></article>

        <article class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><h3 class="font-semibold text-slate-900">Ways to save</h3><p class="mt-1 text-xs text-slate-500">Suggestions based on actual spending patterns</p><div v-if="!recommendations?.available" class="mt-5 rounded-lg bg-violet-50 p-4"><p class="text-sm font-semibold text-violet-900">Building your spending picture</p><p class="mt-1 text-xs leading-5 text-violet-800">{{ recommendations?.message ?? 'Record transactions across three months to see personalized savings ideas.' }}</p></div><p v-else-if="!recommendations.recommendations.length" class="mt-5 rounded-lg bg-emerald-50 p-4 text-sm text-emerald-800">Your category spending is at or below its recent baseline.</p><div v-for="item in recommendations?.recommendations" :key="item.category" class="mt-4 flex items-start gap-3 border-t border-slate-100 pt-4"><span class="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-emerald-50 text-emerald-700">↘</span><div class="min-w-0 flex-1"><p class="text-sm font-semibold text-slate-800">Try trimming {{ item.category }}</p><p class="mt-1 text-xs leading-5 text-slate-500">{{ item.reason }}</p></div><strong class="shrink-0 text-sm text-emerald-700">{{ formatRupees(item.estimated_monthly_savings) }}<span class="font-normal">/mo</span></strong></div></article>
      </div>
    </template>
  </section>
</template>
