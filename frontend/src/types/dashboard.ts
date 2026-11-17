export interface DashboardSummary {
  total_income: number
  total_expenses: number
  balance: number
  savings_rate: number
}

export interface CategorySpending {
  category: string
  total: number
}

export interface MonthlyTrend {
  month: string
  total_income: number
  total_expenses: number
  balance: number
}