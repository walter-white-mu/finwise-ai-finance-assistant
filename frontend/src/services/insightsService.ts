import api from './api'
import type {
  Anomaly,
  Budget,
  BudgetProgress,
  MonthlySummary,
  RecommendationsResponse,
  SpendingAnalysis
} from '../types/insights'

const monthQuery = (month: string) => ({ params: { month: `${month}-01` } })

export const getMonthlyInsights = async (month: string) => {
  const [summary, spending, progress, anomalies, recommendations] = await Promise.all([
    api.get<MonthlySummary>('/api/insights/summary', monthQuery(month)),
    api.get<SpendingAnalysis>('/api/insights/spending', monthQuery(month)),
    api.get<BudgetProgress[]>('/api/budgets/progress', monthQuery(month)),
    api.get<Anomaly[]>('/api/insights/anomalies', monthQuery(month)),
    api.get<RecommendationsResponse>('/api/insights/recommendations', monthQuery(month))
  ])

  return {
    summary: summary.data,
    spending: spending.data,
    progress: progress.data,
    anomalies: anomalies.data,
    recommendations: recommendations.data
  }
}

export const getBudgets = async (): Promise<Budget[]> => (await api.get<Budget[]>('/api/budgets')).data

export const createBudget = async (category: string, amount: string): Promise<Budget> =>
  (await api.post<Budget>('/api/budgets', { category, amount })).data

export const updateBudget = async (id: number, category: string, amount: string): Promise<Budget> =>
  (await api.patch<Budget>(`/api/budgets/${id}`, { category, amount })).data

export const deleteBudget = async (id: number): Promise<void> => {
  await api.delete(`/api/budgets/${id}`)
}
