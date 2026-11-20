import api from './api'
import type { ContributionInput, GoalContribution } from '../types/savingsGoal'

const endpoint = (goalId: number) => `/api/savings-goals/${goalId}/contributions`

export const getContributions = async (goalId: number): Promise<GoalContribution[]> =>
  (await api.get<GoalContribution[]>(endpoint(goalId))).data

export const addContribution = async (goalId: number, input: ContributionInput): Promise<GoalContribution> =>
  (await api.post<GoalContribution>(endpoint(goalId), input)).data

export const deleteContribution = async (goalId: number, contributionId: number): Promise<void> => {
  await api.delete(`${endpoint(goalId)}/${contributionId}`)
}
