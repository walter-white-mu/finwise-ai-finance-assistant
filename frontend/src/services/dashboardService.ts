import api from './api'

import type {
  DashboardSummary,
  CategorySpending,
  MonthlyTrend
} from '../types/dashboard'

export const getDashboardSummary = async (): Promise<DashboardSummary> => {
  const response = await api.get('/api/dashboard/summary')

  return {
    total_income: Number(response.data.total_income),
    total_expenses: Number(response.data.total_expenses),
    balance: Number(response.data.balance),
    savings_rate: Number(response.data.savings_rate)
  }
}

export const getCategorySpending = async (): Promise<CategorySpending[]> => {
  const response = await api.get('/api/dashboard/category-spending')

  return response.data.map((item: CategorySpending) => ({
    category: item.category,
    total: Number(item.total)
  }))
}

export const getMonthlyTrends = async (): Promise<MonthlyTrend[]> => {
  const response = await api.get('/api/dashboard/monthly-trends')

  return response.data.map((item: MonthlyTrend) => ({
    month: item.month,
    total_income: Number(item.total_income),
    total_expenses: Number(item.total_expenses),
    balance: Number(item.balance)
  }))
}