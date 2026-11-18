export type TransactionType = 'INCOME' | 'EXPENSE'

export interface Transaction {
  id: number
  type: TransactionType
  description: string
  amount: number
  category: string
  transaction_date: string
  created_at: string
}

export interface TransactionInput {
  type: TransactionType
  description: string
  amount: number
  category: string
  transaction_date: string
}

export type TransactionUpdate = Partial<TransactionInput>
