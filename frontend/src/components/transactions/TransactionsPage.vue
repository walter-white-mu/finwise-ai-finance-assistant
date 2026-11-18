<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { Plus } from 'lucide-vue-next'

import TransactionForm from './TransactionForm.vue'
import TransactionTable from './TransactionTable.vue'
import {
  createTransaction,
  deleteTransaction,
  getTransactionErrorMessage,
  getTransactions,
  updateTransaction
} from '../../services/transactionService'
import type { Transaction, TransactionInput, TransactionType } from '../../types/transaction'

const emit = defineEmits<{ changed: [] }>()
const transactions = ref<Transaction[]>([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const feedback = ref('')
const feedbackIsError = ref(false)
const formOpen = ref(false)
const editing = ref<Transaction | null>(null)
const typeFilter = ref<'ALL' | TransactionType>('ALL')
const categoryFilter = ref('ALL')
const page = ref(1)
const pageSize = 10

const categories = computed(() => [...new Set(transactions.value.map((item) => item.category))].sort((a, b) => a.localeCompare(b)))
const filteredTransactions = computed(() => transactions.value
  .filter((item) => typeFilter.value === 'ALL' || item.type === typeFilter.value)
  .filter((item) => categoryFilter.value === 'ALL' || item.category === categoryFilter.value)
  .sort((a, b) => b.transaction_date.localeCompare(a.transaction_date) || b.id - a.id))
const visibleTransactions = computed(() => filteredTransactions.value.slice((page.value - 1) * pageSize, page.value * pageSize))

watch([typeFilter, categoryFilter], () => { page.value = 1 })
watch(() => filteredTransactions.value.length, (count) => {
  page.value = Math.min(page.value, Math.max(1, Math.ceil(count / pageSize)))
})

const loadTransactions = async () => {
  loading.value = true
  error.value = ''
  try {
    transactions.value = await getTransactions()
  } catch (err) {
    error.value = getTransactionErrorMessage(err)
  } finally {
    loading.value = false
  }
}

const beginCreate = () => {
  editing.value = null
  formOpen.value = true
  feedback.value = ''
  feedbackIsError.value = false
}

const beginEdit = (transaction: Transaction) => {
  editing.value = transaction
  formOpen.value = true
  feedback.value = ''
  feedbackIsError.value = false
}

const saveTransaction = async (input: TransactionInput) => {
  saving.value = true
  feedback.value = ''
  try {
    if (editing.value) {
      await updateTransaction(editing.value.id, input)
      feedback.value = 'Transaction updated.'
    } else {
      await createTransaction(input)
      feedback.value = 'Transaction added.'
    }
    formOpen.value = false
    editing.value = null
    feedbackIsError.value = false
    await loadTransactions()
    emit('changed')
  } catch (err) {
    feedback.value = getTransactionErrorMessage(err)
    feedbackIsError.value = true
  } finally {
    saving.value = false
  }
}

const removeTransaction = async (id: number) => {
  const transaction = transactions.value.find((item) => item.id === id)
  if (!transaction || !window.confirm(`Delete “${transaction.description}”? This cannot be undone.`)) return
  feedback.value = ''
  feedbackIsError.value = false
  try {
    await deleteTransaction(id)
    feedback.value = 'Transaction deleted.'
    await loadTransactions()
    emit('changed')
  } catch (err) {
    feedback.value = getTransactionErrorMessage(err)
    feedbackIsError.value = true
  }
}

onMounted(loadTransactions)
</script>

<template>
  <section class="space-y-5">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div><h2 class="text-2xl font-bold text-slate-900">Transactions</h2><p class="mt-1 text-sm text-slate-500">Review and manage your income and expenses.</p></div>
      <button class="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700" @click="beginCreate"><Plus :size="18" />Add transaction</button>
    </div>

    <p v-if="feedback" :role="feedbackIsError ? 'alert' : 'status'" class="rounded-lg px-4 py-3 text-sm" :class="feedbackIsError ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-800'">{{ feedback }}</p>

    <section v-if="formOpen" class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 class="mb-4 text-lg font-semibold text-slate-900">{{ editing ? 'Edit transaction' : 'Add transaction' }}</h3>
      <TransactionForm :transaction="editing" :saving="saving" @save="saveTransaction" @cancel="formOpen = false" />
    </section>

    <section class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div class="flex flex-wrap gap-3 border-b border-slate-100 p-4">
        <label class="text-sm text-slate-600">Type
          <select v-model="typeFilter" class="ml-2 rounded-lg border border-slate-300 bg-white px-3 py-2"><option value="ALL">All types</option><option value="INCOME">Income</option><option value="EXPENSE">Expense</option></select>
        </label>
        <label class="text-sm text-slate-600">Category
          <select v-model="categoryFilter" class="ml-2 rounded-lg border border-slate-300 bg-white px-3 py-2"><option value="ALL">All categories</option><option v-for="category in categories" :key="category" :value="category">{{ category }}</option></select>
        </label>
      </div>

      <div v-if="loading" class="p-10 text-center text-sm text-slate-500">Loading transactions...</div>
      <div v-else-if="error" class="p-8 text-center text-sm text-red-600">{{ error }} <button class="ml-2 font-semibold underline" @click="loadTransactions">Retry</button></div>
      <div v-else-if="filteredTransactions.length === 0" class="p-10 text-center text-sm text-slate-500">No transactions match these filters.</div>
      <TransactionTable v-else :transactions="visibleTransactions" :page="page" :page-size="pageSize" :total="filteredTransactions.length" @edit="beginEdit" @delete="removeTransaction" @page-change="page = $event" />
    </section>
  </section>
</template>
