<script setup lang="ts">
import {
  Wallet,
  TrendingUp,
  TrendingDown,
  PiggyBank
} from 'lucide-vue-next'

import AppSidebar from './components/layout/AppSidebar.vue'
import AppHeader from './components/layout/AppHeader.vue'
import SummaryCard from './components/dashboard/SummaryCard.vue'

const summaryCards = [
  {
    title: 'Total Balance',
    amount: '₹95,000',
    description: 'Your current net balance',
    icon: Wallet,
    iconColor: 'bg-blue-50 text-blue-600'
  },
  {
    title: 'Total Income',
    amount: '₹1,20,000',
    description: 'Income received this month',
    icon: TrendingUp,
    iconColor: 'bg-green-50 text-green-600'
  },
  {
    title: 'Total Expenses',
    amount: '₹25,000',
    description: 'Expenses this month',
    icon: TrendingDown,
    iconColor: 'bg-red-50 text-red-600'
  },
  {
    title: 'Savings Rate',
    amount: '79.17%',
    description: 'Percentage of income saved',
    icon: PiggyBank,
    iconColor: 'bg-purple-50 text-purple-600'
  }
]
</script>

<template>
  <div class="min-h-screen bg-slate-50 lg:flex">

    <AppSidebar class="hidden lg:flex" />

    <main class="min-w-0 flex-1">
      <AppHeader />

      <div class="space-y-8 p-6 lg:p-8">

        <!-- Welcome section -->
        <section>
          <h2 class="text-xl font-bold text-slate-900">
            Welcome back!
          </h2>

          <p class="mt-1 text-sm text-slate-500">
            Here's what's happening with your money.
          </p>
        </section>

        <!-- Summary cards -->
        <section>
          <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
            <SummaryCard
              v-for="card in summaryCards"
              :key="card.title"
              v-bind="card"
            />
          </div>
        </section>

        <!-- Charts section -->
        <section class="grid grid-cols-1 gap-6 xl:grid-cols-2">

          <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 class="font-semibold text-slate-900">
              Income vs Expenses
            </h3>

            <p class="mt-1 text-sm text-slate-500">
              Your monthly financial performance
            </p>

            <div class="mt-6 flex h-64 items-center justify-center rounded-lg bg-slate-50">
              <p class="text-sm text-slate-400">
                Monthly chart coming soon
              </p>
            </div>
          </div>

          <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 class="font-semibold text-slate-900">
              Spending Breakdown
            </h3>

            <p class="mt-1 text-sm text-slate-500">
              Where your money goes
            </p>

            <div class="mt-6 flex h-64 items-center justify-center rounded-lg bg-slate-50">
              <p class="text-sm text-slate-400">
                Category chart coming soon
              </p>
            </div>
          </div>

        </section>

        <!-- Recent transactions placeholder -->
        <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 class="font-semibold text-slate-900">
            Recent Transactions
          </h3>

          <p class="mt-1 text-sm text-slate-500">
            Your latest income and expenses will appear here.
          </p>

          <div class="mt-6 flex h-24 items-center justify-center rounded-lg bg-slate-50">
            <p class="text-sm text-slate-400">
              Transactions table coming soon
            </p>
          </div>
        </section>

      </div>
    </main>
  </div>
</template>