<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import type { SavingsGoal, SavingsGoalInput } from '../../types/savingsGoal'
import { isPositiveMoney } from '../../utils/money'

const props = defineProps<{ goal: SavingsGoal | null; saving: boolean }>()
const emit = defineEmits<{ save: [input: SavingsGoalInput]; cancel: [] }>()

const form = reactive<SavingsGoalInput>({ name: '', description: '', target_amount: '', target_date: '' })
const validationError = ref('')

watch(() => props.goal, (goal) => {
  Object.assign(form, goal ? {
    name: goal.name,
    description: goal.description ?? '',
    target_amount: goal.target_amount,
    target_date: goal.target_date
  } : { name: '', description: '', target_amount: '', target_date: '' })
  validationError.value = ''
}, { immediate: true })

const submit = () => {
  if (form.name.trim().length < 2 || !isPositiveMoney(form.target_amount) || !form.target_date) {
    validationError.value = 'Enter a goal name, a positive target amount with at most 2 decimal places, and a target date.'
    return
  }
  emit('save', {
    name: form.name.trim(),
    description: form.description?.trim() || null,
    target_amount: form.target_amount.trim(),
    target_date: form.target_date
  })
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
    <div class="grid gap-4 sm:grid-cols-2">
      <label class="text-sm font-medium text-slate-700 sm:col-span-2">Goal name
        <input v-model="form.name" required minlength="2" maxlength="120" class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" placeholder="e.g. Emergency fund" />
      </label>
      <label class="text-sm font-medium text-slate-700 sm:col-span-2">Description (optional)
        <textarea v-model="form.description" maxlength="2000" rows="2" class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
      </label>
      <label class="text-sm font-medium text-slate-700">Target amount (₹)
        <input v-model="form.target_amount" required inputmode="decimal" pattern="[0-9]+(\.[0-9]{1,2})?" class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" placeholder="0.00" />
      </label>
      <label class="text-sm font-medium text-slate-700">Target date
        <input v-model="form.target_date" type="date" required class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
      </label>
    </div>
    <p v-if="validationError" role="alert" class="text-sm text-red-600">{{ validationError }}</p>
    <div class="flex justify-end gap-3">
      <button type="button" class="rounded-lg border border-slate-300 px-4 py-2 text-sm" @click="emit('cancel')">Cancel</button>
      <button type="submit" :disabled="saving" class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60">{{ saving ? 'Saving...' : goal ? 'Save changes' : 'Create goal' }}</button>
    </div>
  </form>
</template>
