import api from './api'

export interface DocumentRecord {
  id: string
  filename: string
  size_bytes: number
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
  error_message: string | null
  page_count: number | null
  chunk_count: number
  created_at: string
}

export interface DocumentSource {
  document_id: string
  document_name: string
  page_number: number
  excerpt: string
  similarity: number
}

export async function listDocuments() {
  return (await api.get<DocumentRecord[]>('/api/documents')).data
}

export async function uploadDocument(file: File) {
  const form = new FormData()
  form.append('file', file)
  return (await api.post<DocumentRecord>('/api/documents/upload', form, { timeout: 60_000, headers: { 'Content-Type': 'multipart/form-data' } })).data
}

export async function processDocument(id: string) {
  return (await api.post<DocumentRecord>(`/api/documents/${encodeURIComponent(id)}/process`, {}, { timeout: 600_000 })).data
}

export async function deleteDocument(id: string) {
  await api.delete(`/api/documents/${encodeURIComponent(id)}`)
}

export async function askDocuments(question: string) {
  return (await api.post<{ answer: string; sources: DocumentSource[] }>('/api/documents/ask', { question }, { timeout: 190_000 })).data
}
