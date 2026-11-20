<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Plus, PiggyBank, Target, CircleCheckBig } from 'lucide-vue-next'

import ContributionForm from './ContributionForm.vue'
import SavingsGoalCard from './SavingsGoalCard.vue'
import SavingsGoalForm from './SavingsGoalForm.vue'
import { addContribution, deleteContribution, getContributions } from '../../services/contributionService'
import { getApiErrorMessage } from '../../services/apiError'
import { createSavingsGoal, deleteSavingsGoal, getSavingsGoals, updateSavingsGoal } from '../../services/savingsGoalService'
import type { ContributionInput, GoalContribution, SavingsGoal, SavingsGoalInput } from '../../types/savingsGoal'
import { formatDate, formatMinorUnits, formatRupees, toMinorUnits } from '../../utils/money'

const goals = ref<SavingsGoal[]>([])
const loading = ref(true)
const saving = ref(false)
const contributionSaving = ref(false)
const error = ref('')
const feedback = ref('')
const feedbackIsError = ref(false)
const formOpen = ref(false)
const editingGoal = ref<SavingsGoal | null>(null)
const expandedGoalId = ref<number | null>(null)
const contributionFormGoalId = ref<number | null>(null)
const contributions = ref<GoalContribution[]>([])
const contributionsLoading = ref(false)
const contributionsError = ref('')

const totalSaved = computed(() => goals.value.reduce((sum, goal) => sum + toMinorUnits(goal.current_saved_amount), 0n))
const totalTarget = computed(() => goals.value.reduce((sum, goal) => sum + toMinorUnits(goal.target_amount), 0n))
const activeCount = computed(() => goals.value.filter((goal) => goal.status === 'ACTIVE').length)
const completedCount = computed(() => goals.value.filter((goal) => goal.status === 'COMPLETED').length)

const loadGoals = async () => {
  loading.value = true
  error.value = ''
  try {
    goals.value = await getSavingsGoals()
  } catch (err) {
    error.value = getApiErrorMessage(err)
  } finally {
    loading.value = false
  }
}

const beginCreate = () => {
  editingGoal.value = null
  feedback.value = ''
  feedbackIsError.value = false
  formOpen.value = true
}

const beginEdit = (goal: SavingsGoal) => {
  editingGoal.value = goal
  feedback.value = ''
  feedbackIsError.value = false
  formOpen.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const saveGoal = async (input: SavingsGoalInput) => {
  saving.value = true
  feedback.value = ''
  try {
    if (editingGoal.value) {
      await updateSavingsGoal(editingGoal.value.id, input)
      feedback.value = 'Savings goal updated.'
    } else {
      await createSavingsGoal(input)
      feedback.value = 'Savings goal created.'
    }
    feedbackIsError.value = false
    formOpen.value = false
    editingGoal.value = null
    await loadGoals()
  } catch (err) {
    feedback.value = getApiErrorMessage(err)
    feedbackIsError.value = true
  } finally {
    saving.value = false
  }
}

const removeGoal = async (goal: SavingsGoal) => {
  if (!window.confirm(`Delete “${goal.name}” and its contribution history? This cannot be undone.`)) return
  feedback.value = ''
  try {
    await deleteSavingsGoal(goal.id)
    feedback.value = 'Savings goal deleted.'
    feedbackIsError.value = false
    if (expandedGoalId.value === goal.id) {
      expandedGoalId.value = null
      contributions.value = []
    }
    await loadGoals()
  } catch (err) {
    feedback.value = getApiErrorMessage(err)
    feedbackIsError.value = true
  }
}

const showHistory = async (goalId: number) => {
  if (expandedGoalId.value === goalId) {
    expandedGoalId.value = null
    contributionFormGoalId.value = null
    return
  }
  expandedGoalId.value = goalId
  contributionFormGoalId.value = null
  contributionsLoading.value = true
  contributionsError.value = ''
  try {
    contributions.value = await getContributions(goalId)
  } catch (err) {
    contributionsError.value = getApiErrorMessage(err)
  } finally {
    contributionsLoading.value = false
  }
}

const showContributionForm = async (goalId: number) => {
  if (expandedGoalId.value !== goalId) await showHistory(goalId)
  contributionFormGoalId.value = goalId
}

const saveContribution = async (goalId: number, input: ContributionInput) => {
  contributionSaving.value = true
  feedback.value = ''
  try {
    await addContribution(goalId, input)
    feedback.value = 'Contribution recorded.'
    feedbackIsError.value = false
    contributionFormGoalId.value = null
    await Promise.all([loadGoals(), reloadContributions(goalId)])
  } catch (err) {
    feedback.value = getApiErrorMessage(err)
    feedbackIsError.value = true
  } finally {
    contributionSaving.value = false
  }
}

const reloadContributions = async (goalId: number) => {
  contributions.value = await getContributions(goalId)
}

const removeContribution = async (contribution: GoalContribution) => {
  const goalId = contribution.goal_id
  if (!window.confirm(`Remove this ${formatRupees(contribution.amount)} contribution? The goal total will be reduced.`)) return
  feedback.value = ''
  try {
    await deleteContribution(goalId, contribution.id)
    feedback.value = 'Contribution removed.'
    feedbackIsError.value = false
    await Promise.all([loadGoals(), reloadContributions(goalId)])
  } catch (err) {
    feedback.value = getApiErrorMessage(err)
    feedbackIsError.value = true
  }
}

onMounted(loadGoals)
</script>

<template>
  <main class="space-y-6">
    <header class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-slate-900">Savings Goals</h2>
        <p class="mt-1 text-sm text-slate-500">Set a target and track each contribution along the way.</p>
      </div>
      <button class="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700" @click="beginCreate"><Plus :size="18" />Create goal</button>
    </header>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <article class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><p class="flex items-center gap-2 text-sm text-slate-500"><PiggyBank :size="17" class="text-blue-600" />Total saved</p><p class="mt-2 text-xl font-bold text-slate-900">{{ formatMinorUnits(totalSaved) }}</p></article>
      <article class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><p class="flex items-center gap-2 text-sm text-slate-500"><Target :size="17" class="text-blue-600" />Total target</p><p class="mt-2 text-xl font-bold text-slate-900">{{ formatMinorUnits(totalTarget) }}</p></article>
      <article class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><p class="text-sm text-slate-500">Active goals</p><p class="mt-2 text-xl font-bold text-blue-700">{{ activeCount }}</p></article>
      <article class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><p class="flex items-center gap-2 text-sm text-slate-500"><CircleCheckBig :size="17" class="text-green-600" />Completed goals</p><p class="mt-2 text-xl font-bold text-green-700">{{ completedCount }}</p></article>
    </div>

    <p v-if="feedback" :role="feedbackIsError ? 'alert' : 'status'" class="rounded-lg px-4 py-3 text-sm" :class="feedbackIsError ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-800'">{{ feedback }}</p>

    <section v-if="formOpen" class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 class="mb-4 text-lg font-semibold text-slate-900">{{ editingGoal ? 'Edit savings goal' : 'Create savings goal' }}</h3>
      <SavingsGoalForm :goal="editingGoal" :saving="saving" @save="saveGoal" @cancel="formOpen = false" />
    </section>

    <div v-if="loading" class="rounded-xl border border-slate-200 bg-white p-12 text-center text-sm text-slate-500">Loading savings goals...</div>
    <div v-else-if="error" class="rounded-xl bg-red-50 p-6 text-center text-sm text-red-700">{{ error }} <button class="ml-2 font-semibold underline" @click="loadGoals">Retry</button></div>
    <div v-else-if="goals.length === 0" class="rounded-xl border border-dashed border-slate-300 bg-white px-6 py-14 text-center">
      <PiggyBank :size="36" class="mx-auto text-blue-500" />
      <h3 class="mt-3 text-lg font-semibold text-slate-900">No savings goals yet</h3>
      <p class="mt-1 text-sm text-slate-500">Create your first goal to start tracking your progress.</p>
      <button class="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white" @click="beginCreate">Create goal</button>
    </div>

    <div v-else class="grid grid-cols-1 gap-5 xl:grid-cols-2">
      <div v-for="goal in goals" :key="goal.id" class="space-y-3">
        <SavingsGoalCard :goal="goal" :expanded="expandedGoalId === goal.id" @edit="beginEdit" @delete="removeGoal" @toggle="showHistory" @contribute="showContributionForm" />
        <section v-if="expandedGoalId === goal.id" class="space-y-4 rounded-xl border border-slate-200 bg-white p-4">
          <p v-if="contributionsError" role="alert" class="text-sm text-red-600">{{ contributionsError }}</p>
          <div v-else-if="contributionsLoading" class="text-sm text-slate-500">Loading contribution history...</div>
          <div v-else-if="contributions.length === 0" class="text-sm text-slate-500">No contributions recorded for this goal yet.</div>
          <ul v-else class="divide-y divide-slate-100">
            <li v-for="item in contributions" :key="item.id" class="flex flex-wrap items-center justify-between gap-2 py-3 first:pt-0 last:pb-0">
              <div><p class="font-medium text-slate-800">{{ formatRupees(item.amount) }}</p><p class="text-xs text-slate-500">{{ formatDate(item.contribution_date) }}<span v-if="item.note"> · {{ item.note }}</span></p></div>
              <button class="rounded px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50" @click="removeContribution(item)">Remove</button>
            </li>
          </ul>
          <ContributionForm v-if="contributionFormGoalId === goal.id" :saving="contributionSaving" @save="saveContribution(goal.id, $event)" @cancel="contributionFormGoalId = null" />
        </section>
      </div>
    </div>
  </main>
</template>
