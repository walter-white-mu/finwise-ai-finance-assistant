<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { ContributionInput } from '../../types/savingsGoal'
import { isPositiveMoney } from '../../utils/money'

defineProps<{ saving: boolean }>()
const emit = defineEmits<{ save: [input: ContributionInput]; cancel: [] }>()
const now = new Date()
const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
const form = reactive<ContributionInput>({ amount: '', contribution_date: today, note: '' })
const validationError = ref('')

const submit = () => {
  if (!isPositiveMoney(form.amount) || !form.contribution_date) {
    validationError.value = 'Enter a positive contribution with at most 2 decimal places and choose a date.'
    return
  }
  emit('save', { ...form, amount: form.amount.trim(), note: form.note?.trim() || null })
}
</script>

<template>
  <form class="rounded-lg bg-slate-50 p-4" @submit.prevent="submit">
    <h4 class="mb-3 font-semibold text-slate-800">Add a contribution</h4>
    <div class="grid gap-3 sm:grid-cols-3">
      <label class="text-sm text-slate-700">Amount (₹)<input v-model="form.amount" required inputmode="decimal" pattern="[0-9]+(\.[0-9]{1,2})?" class="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2" placeholder="0.00" /></label>
      <label class="text-sm text-slate-700">Date<input v-model="form.contribution_date" type="date" required class="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2" /></label>
      <label class="text-sm text-slate-700">Note (optional)<input v-model="form.note" maxlength="255" class="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2" /></label>
    </div>
    <p v-if="validationError" role="alert" class="mt-2 text-sm text-red-600">{{ validationError }}</p>
    <div class="mt-3 flex justify-end gap-2">
      <button type="button" class="rounded-md border border-slate-300 px-3 py-1.5 text-sm" @click="emit('cancel')">Cancel</button>
      <button type="submit" :disabled="saving" class="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-semibold text-white disabled:opacity-60">{{ saving ? 'Saving...' : 'Add contribution' }}</button>
    </div>
  </form>
</template>
