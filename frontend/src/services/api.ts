import axios from 'axios'

const baseURL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '')

const client = axios.create({
  baseURL,
  timeout: 5000,
  headers: { Accept: 'application/json' },
})

export interface HealthResponse {
  status: 'healthy'
}

async function getHealth(): Promise<HealthResponse> {
  const { data } = await client.get<unknown>('/health')
  if (typeof data !== 'object' || data === null || !('status' in data) || data.status !== 'healthy') {
    throw new Error('Unexpected backend health response')
  }

  return { status: data.status }
}

export default { getHealth }