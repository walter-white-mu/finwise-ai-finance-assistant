<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { init } from './echarts'

import type { ECharts, EChartsOption } from 'echarts'
import type { CategorySpending } from '../../types/dashboard'

const props = defineProps<{
  data: CategorySpending[]
  loading: boolean
  error: string
}>()
const emit = defineEmits<{ retry: [] }>()

const chartElement = ref<HTMLElement | null>(null)
let chart: ECharts | null = null
let resizeObserver: ResizeObserver | null = null

const currency = new Intl.NumberFormat('en-IN', {
  style: 'currency', currency: 'INR', maximumFractionDigits: 2
})

const option = computed<EChartsOption>(() => ({
  color: ['#2563eb', '#7c3aed', '#0891b2', '#ea580c', '#16a34a', '#db2777', '#ca8a04'],
  tooltip: {
    trigger: 'item',
    formatter: (params) => {
      if (Array.isArray(params)) return ''
      return `${params.name}<br/>${currency.format(Number(params.value))} (${params.percent}%)`
    }
  },
  legend: { bottom: 0, left: 'center', type: 'scroll' },
  series: [{
    name: 'Spending by category',
    type: 'pie',
    radius: ['48%', '72%'],
    center: ['50%', '45%'],
    avoidLabelOverlap: true,
    itemStyle: { borderRadius: 5, borderColor: '#fff', borderWidth: 2 },
    label: { show: true, formatter: '{b}: {d}%', color: '#475569' },
    labelLine: { length: 12, length2: 8 },
    data: props.data.map((row) => ({ name: row.category, value: row.total }))
  }]
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
    <h2 class="text-lg font-semibold text-slate-900">Category Spending</h2>
    <div class="relative mt-4 min-h-[300px]">
      <div ref="chartElement" class="h-[300px] w-full" :class="{ 'invisible': loading || !!error || !data.length }" />
      <div v-if="loading" class="absolute inset-0 grid place-items-center text-sm text-slate-500">Loading category spending...</div>
      <div v-else-if="error" class="absolute inset-0 grid place-items-center text-center text-sm text-red-600">
        <div>{{ error }} <button class="ml-2 font-semibold underline" @click="emit('retry')">Retry</button></div>
      </div>
      <div v-else-if="!data.length" class="absolute inset-0 grid place-items-center text-sm text-slate-500">No expense categories yet.</div>
    </div>
  </article>
</template>
