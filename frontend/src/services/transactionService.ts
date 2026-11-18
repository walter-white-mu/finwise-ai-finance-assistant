import { AxiosError } from 'axios'

import api from './api'
import type { Transaction, TransactionInput, TransactionUpdate } from '../types/transaction'

const toTransaction = (item: Transaction): Transaction => ({
  ...item,
  amount: Number(item.amount)
})

export const getTransactions = async (): Promise<Transaction[]> => {
  const response = await api.get<Transaction[]>('/api/transactions')
  return response.data.map(toTransaction)
}

export const getTransaction = async (id: number): Promise<Transaction> => {
  const response = await api.get<Transaction>(`/api/transactions/${id}`)
  return toTransaction(response.data)
}

export const createTransaction = async (input: TransactionInput): Promise<Transaction> => {
  const response = await api.post<Transaction>('/api/transactions', input)
  return toTransaction(response.data)
}

export const updateTransaction = async (id: number, input: TransactionUpdate): Promise<Transaction> => {
  const response = await api.patch<Transaction>(`/api/transactions/${id}`, input)
  return toTransaction(response.data)
}

export const deleteTransaction = async (id: number): Promise<void> => {
  await api.delete(`/api/transactions/${id}`)
}

export const getTransactionErrorMessage = (error: unknown): string => {
  if (!(error instanceof AxiosError)) return 'Something went wrong. Please try again.'

  const detail: unknown = error.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((item: { msg?: string; loc?: (string | number)[] }) => {
      const field = item.loc?.at(-1)
      return `${field ? `${String(field)}: ` : ''}${item.msg ?? 'Invalid value'}`
    }).join(' ')
  }
  return error.message || 'Unable to complete the request. Please try again.'
}
