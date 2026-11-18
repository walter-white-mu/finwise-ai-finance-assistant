<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { init } from './echarts'

import type { ECharts, EChartsOption } from 'echarts'
import type { MonthlyTrend } from '../../types/dashboard'

const props = defineProps<{
  data: MonthlyTrend[]
  loading: boolean
  error: string
}>()
const emit = defineEmits<{ retry: [] }>()

const chartElement = ref<HTMLElement | null>(null)
let chart: ECharts | null = null
let resizeObserver: ResizeObserver | null = null

const currency = new Intl.NumberFormat('en-IN', {
  style: 'currency', currency: 'INR', maximumFractionDigits: 0
})

const monthLabels = computed(() => props.data.map(({ month }) => {
  const [year, monthNumber] = month.split('-').map(Number)
  if (!year || !monthNumber) return month
  return new Date(year, monthNumber - 1, 1).toLocaleDateString('en-IN', {
    month: 'short', year: 'numeric'
  })
}))

const option = computed<EChartsOption>(() => ({
  color: ['#16a34a', '#ef4444'],
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    valueFormatter: (value) => currency.format(Number(value))
  },
  legend: { top: 0, right: 0, data: ['Income', 'Expenses'] },
  grid: { top: 45, left: 12, right: 12, bottom: 12, containLabel: true },
  xAxis: {
    type: 'category',
    data: monthLabels.value,
    axisTick: { show: false },
    axisLine: { lineStyle: { color: '#cbd5e1' } },
    axisLabel: { color: '#64748b', hideOverlap: true }
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: '#64748b', formatter: (value: number) => currency.format(value) },
    splitLine: { lineStyle: { color: '#e2e8f0', type: 'dashed' } }
  },
  series: [
    { name: 'Income', type: 'bar', data: props.data.map((row) => row.total_income), barMaxWidth: 36, itemStyle: { borderRadius: [4, 4, 0, 0] } },
    { name: 'Expenses', type: 'bar', data: props.data.map((row) => row.total_expenses), barMaxWidth: 36, itemStyle: { borderRadius: [4, 4, 0, 0] } }
  ]
}))

const updateChart = async () => {
  await nextTick()
  if (!chartElement.value) return
  if (!chart) chart = init(chartElement.value)
  chart.setOption(option.value, true)
  chart.resize()
}

watch([option, () => props.loading], updateChart)

onMounted(() => {
  updateChart()
  if (chartElement.value) {
    resizeObserver = new ResizeObserver(() => chart?.resize())
    resizeObserver.observe(chartElement.value)
  }
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  chart?.dispose()
  chart = null
})
</script>

<template>
  <article class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
    <h2 class="text-lg font-semibold text-slate-900">Monthly Income vs Expenses</h2>
    <div class="relative mt-4 min-h-[300px]">
      <div ref="chartElement" class="h-[300px] w-full" :class="{ 'invisible': loading || !!error || !data.length }" />
      <div v-if="loading" class="absolute inset-0 grid place-items-center text-sm text-slate-500">Loading monthly trends...</div>
      <div v-else-if="error" class="absolute inset-0 grid place-items-center text-center text-sm text-red-600">
        <div>{{ error }} <button class="ml-2 font-semibold underline" @click="emit('retry')">Retry</button></div>
      </div>
      <div v-else-if="!data.length" class="absolute inset-0 grid place-items-center text-sm text-slate-500">No monthly transaction data yet.</div>
    </div>
  </article>
</template>
