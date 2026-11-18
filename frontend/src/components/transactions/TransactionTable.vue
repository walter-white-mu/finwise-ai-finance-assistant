<script setup lang="ts">
import { Pencil, Trash2 } from 'lucide-vue-next'
import type { Transaction } from '../../types/transaction'

defineProps<{ transactions: Transaction[]; page: number; pageSize: number; total: number }>()
const emit = defineEmits<{ edit: [transaction: Transaction]; delete: [id: number]; 'page-change': [page: number] }>()
const currency = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 })
const dateFormat = new Intl.DateTimeFormat('en-IN', { day: '2-digit', month: 'short', year: 'numeric', timeZone: 'UTC' })
</script>

<template>
  <div class="overflow-x-auto">
    <table class="w-full min-w-[700px] text-left text-sm">
      <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
        <tr><th class="px-4 py-3">Description</th><th class="px-4 py-3">Category</th><th class="px-4 py-3">Date</th><th class="px-4 py-3">Type</th><th class="px-4 py-3 text-right">Amount</th><th class="px-4 py-3 text-right">Actions</th></tr>
      </thead>
      <tbody class="divide-y divide-slate-100">
        <tr v-for="transaction in transactions" :key="transaction.id" class="text-slate-700">
          <td class="px-4 py-3 font-medium text-slate-900">{{ transaction.description }}</td>
          <td class="px-4 py-3">{{ transaction.category }}</td>
          <td class="px-4 py-3">{{ dateFormat.format(new Date(`${transaction.transaction_date}T00:00:00Z`)) }}</td>
          <td class="px-4 py-3"><span class="rounded-full px-2.5 py-1 text-xs font-semibold" :class="transaction.type === 'INCOME' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">{{ transaction.type === 'INCOME' ? 'Income' : 'Expense' }}</span></td>
          <td class="px-4 py-3 text-right font-semibold tabular-nums" :class="transaction.type === 'INCOME' ? 'text-green-700' : 'text-red-700'">
            {{ transaction.type === 'INCOME' ? '+' : '−' }}{{ currency.format(transaction.amount) }}
          </td>
          <td class="px-4 py-3"><div class="flex justify-end gap-2">
            <button :aria-label="`Edit ${transaction.description}`" class="rounded p-2 text-slate-500 hover:bg-slate-100 hover:text-blue-700" @click="emit('edit', transaction)"><Pencil :size="16" /></button>
            <button :aria-label="`Delete ${transaction.description}`" class="rounded p-2 text-slate-500 hover:bg-red-50 hover:text-red-700" @click="emit('delete', transaction.id)"><Trash2 :size="16" /></button>
          </div></td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class="flex items-center justify-between border-t border-slate-100 px-4 py-3 text-sm text-slate-500">
    <span>Showing {{ total ? (page - 1) * pageSize + 1 : 0 }}–{{ Math.min(page * pageSize, total) }} of {{ total }}</span>
    <div class="flex gap-2">
      <button class="rounded-md border border-slate-300 px-3 py-1.5 disabled:opacity-40" :disabled="page <= 1" @click="emit('page-change', page - 1)">Previous</button>
      <button class="rounded-md border border-slate-300 px-3 py-1.5 disabled:opacity-40" :disabled="page * pageSize >= total" @click="emit('page-change', page + 1)">Next</button>
    </div>
  </div>
</template>
