export interface MonthTotals {
  month: string
  total_income: string
  total_expenses: string
  net_savings: string
  savings_rate: string
}

export interface MonthlySummary {
  current: MonthTotals
  previous: MonthTotals
  income_change: string
  expense_change: string
  savings_change: string
}

export interface SpendingCategory {
  category: string
  amount: string
  percentage: string
  previous_amount: string
  change: string
  change_percentage: string | null
}

export interface SpendingAnalysis {
  month: string
  total_expenses: string
  categories: SpendingCategory[]
}

export interface Budget {
  id: number
  category: string
  amount: string
  created_at: string
  updated_at: string
}

export interface BudgetProgress {
  category: string
  budget: string
  spent: string
  remaining: string
  percentage_used: string
  exceeded: boolean
}

export interface Anomaly {
  transaction_id: number
  description: string
  category: string
  amount: string
  transaction_date: string
  baseline_median: string
  reason: string
}

export interface SavingsRecommendation {
  category: string
  recent_month_spending: string
  comparison_monthly_average: string
  estimated_monthly_savings: string
  reason: string
}

export interface RecommendationsResponse {
  available: boolean
  months_of_history: number
  recommendations: SavingsRecommendation[]
  message: string | null
}
