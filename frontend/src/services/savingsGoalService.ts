import api from './api'
import type { SavingsGoal, SavingsGoalInput } from '../types/savingsGoal'

const endpoint = '/api/savings-goals'

export const getSavingsGoals = async (): Promise<SavingsGoal[]> =>
  (await api.get<SavingsGoal[]>(endpoint)).data

export const getSavingsGoal = async (id: number): Promise<SavingsGoal> =>
  (await api.get<SavingsGoal>(`${endpoint}/${id}`)).data

export const createSavingsGoal = async (input: SavingsGoalInput): Promise<SavingsGoal> =>
  (await api.post<SavingsGoal>(endpoint, input)).data

export const updateSavingsGoal = async (id: number, input: Partial<SavingsGoalInput>): Promise<SavingsGoal> =>
  (await api.patch<SavingsGoal>(`${endpoint}/${id}`, input)).data

export const deleteSavingsGoal = async (id: number): Promise<void> => {
  await api.delete(`${endpoint}/${id}`)
}
