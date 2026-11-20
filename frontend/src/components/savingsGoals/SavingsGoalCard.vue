<script setup lang="ts">
import { CalendarDays, CheckCircle2, CircleDollarSign, Clock3, Pencil, Trash2 } from 'lucide-vue-next'
import type { SavingsGoal } from '../../types/savingsGoal'
import { formatDate, formatRupees } from '../../utils/money'

defineProps<{ goal: SavingsGoal; expanded: boolean }>()
const emit = defineEmits<{ edit: [goal: SavingsGoal]; delete: [goal: SavingsGoal]; toggle: [id: number]; contribute: [id: number] }>()
</script>

<template>
  <article class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <div class="flex items-center gap-2">
          <h3 class="truncate text-lg font-semibold text-slate-900">{{ goal.name }}</h3>
          <span class="shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold" :class="goal.status === 'COMPLETED' ? 'bg-green-50 text-green-700' : 'bg-blue-50 text-blue-700'">{{ goal.status === 'COMPLETED' ? 'Completed' : 'Active' }}</span>
        </div>
        <p v-if="goal.description" class="mt-1 text-sm text-slate-500">{{ goal.description }}</p>
      </div>
      <div class="flex shrink-0 gap-1">
        <button :aria-label="`Edit ${goal.name}`" class="rounded p-2 text-slate-500 hover:bg-slate-100 hover:text-blue-700" @click="emit('edit', goal)"><Pencil :size="16" /></button>
        <button :aria-label="`Delete ${goal.name}`" class="rounded p-2 text-slate-500 hover:bg-red-50 hover:text-red-700" @click="emit('delete', goal)"><Trash2 :size="16" /></button>
      </div>
    </div>

    <div class="mt-5 flex items-end justify-between gap-3">
      <div><p class="text-xs uppercase tracking-wide text-slate-500">Saved</p><p class="mt-1 text-xl font-bold text-slate-900">{{ formatRupees(goal.current_saved_amount) }}</p></div>
      <p class="text-sm text-slate-500">of {{ formatRupees(goal.target_amount) }}</p>
    </div>
    <div class="mt-3 h-2.5 overflow-hidden rounded-full bg-slate-100" role="progressbar" :aria-valuenow="Number(goal.progress_percent)" aria-valuemin="0" aria-valuemax="100" :aria-label="`${goal.name} progress`">
      <div class="h-full rounded-full bg-blue-600 transition-all" :style="{ width: `${Math.min(100, Number(goal.progress_percent))}%` }" />
    </div>
    <div class="mt-2 flex justify-between text-xs text-slate-500"><span>{{ goal.progress_percent }}% saved</span><span>{{ formatRupees(goal.remaining_amount) }} remaining</span></div>

    <div class="mt-5 grid grid-cols-2 gap-3 border-t border-slate-100 pt-4 text-sm">
      <p class="flex items-center gap-2 text-slate-600"><CalendarDays :size="16" class="text-slate-400" />{{ formatDate(goal.target_date) }}</p>
      <p class="flex items-center justify-end gap-2 text-slate-600"><component :is="goal.status === 'COMPLETED' ? CheckCircle2 : Clock3" :size="16" class="text-slate-400" />{{ goal.status === 'COMPLETED' ? 'Target reached' : 'Target date' }}</p>
    </div>
    <div class="mt-4 flex flex-wrap gap-2">
      <button class="inline-flex items-center gap-2 rounded-lg bg-blue-50 px-3 py-2 text-sm font-semibold text-blue-700 hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-50" :disabled="goal.status === 'COMPLETED'" @click="emit('contribute', goal.id)"><CircleDollarSign :size="16" />Add contribution</button>
      <button class="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50" @click="emit('toggle', goal.id)">{{ expanded ? 'Hide history' : 'Contribution history' }}</button>
    </div>
  </article>
</template>
