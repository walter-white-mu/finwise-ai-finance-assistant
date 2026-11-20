export type GoalStatus = 'ACTIVE' | 'COMPLETED'

export interface SavingsGoal {
  id: number
  name: string
  description: string | null
  target_amount: string
  current_saved_amount: string
  remaining_amount: string
  progress_percent: string
  target_date: string
  created_at: string
  status: GoalStatus
}

export interface SavingsGoalInput {
  name: string
  description: string | null
  target_amount: string
  target_date: string
}

export interface GoalContribution {
  id: number
  goal_id: number
  amount: string
  contribution_date: string
  note: string | null
  created_at: string
}

export interface ContributionInput {
  amount: string
  contribution_date: string
  note: string | null
}
