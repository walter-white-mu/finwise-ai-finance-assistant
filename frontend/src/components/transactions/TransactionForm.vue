<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import type { Transaction, TransactionInput } from '../../types/transaction'

const props = defineProps<{ transaction: Transaction | null; saving: boolean }>()
const emit = defineEmits<{ save: [input: TransactionInput]; cancel: [] }>()

const now = new Date()
const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
const form = reactive<TransactionInput>({
  type: 'EXPENSE', description: '', amount: 0, category: '', transaction_date: today
})
const validationError = ref('')

watch(() => props.transaction, (transaction) => {
  Object.assign(form, transaction ? {
    type: transaction.type,
    description: transaction.description,
    amount: transaction.amount,
    category: transaction.category,
    transaction_date: transaction.transaction_date
  } : {
    type: 'EXPENSE', description: '', amount: 0, category: '', transaction_date: today
  })
  validationError.value = ''
}, { immediate: true })

const submit = () => {
  const description = form.description.trim()
  const category = form.category.trim()
  if (description.length < 2 || category.length < 2 || !form.transaction_date || !Number.isFinite(form.amount) || form.amount <= 0) {
    validationError.value = 'Enter a description and category (at least 2 characters), a date, and a positive amount.'
    return
  }
  validationError.value = ''
  emit('save', { ...form, description, category, amount: Number(form.amount) })
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
    <div class="grid gap-4 sm:grid-cols-2">
      <label class="text-sm font-medium text-slate-700">Type
        <select v-model="form.type" class="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2">
          <option value="INCOME">Income</option><option value="EXPENSE">Expense</option>
        </select>
      </label>
      <label class="text-sm font-medium text-slate-700">Amount (₹)
        <input v-model.number="form.amount" type="number" min="0.01" step="0.01" required class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
      </label>
      <label class="text-sm font-medium text-slate-700 sm:col-span-2">Description
        <input v-model="form.description" maxlength="255" minlength="2" required class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
      </label>
      <label class="text-sm font-medium text-slate-700">Category
        <input v-model="form.category" maxlength="100" minlength="2" required class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
      </label>
      <label class="text-sm font-medium text-slate-700">Transaction date
        <input v-model="form.transaction_date" type="date" required class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
      </label>
    </div>
    <p v-if="validationError" role="alert" class="text-sm text-red-600">{{ validationError }}</p>
    <div class="flex justify-end gap-3">
      <button type="button" class="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700" @click="emit('cancel')">Cancel</button>
      <button type="submit" :disabled="saving" class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60">
        {{ saving ? 'Saving...' : transaction ? 'Save changes' : 'Add transaction' }}
      </button>
    </div>
  </form>
</template>
