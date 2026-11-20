import { AxiosError } from 'axios'

export const getApiErrorMessage = (error: unknown): string => {
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
