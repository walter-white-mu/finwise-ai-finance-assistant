import api from './api'

export interface ChatToolResult {
  name: string
  data: Record<string, unknown> | unknown[]
}

export interface ChatResponse {
  conversation_id: string
  assistant_message: string
  tool_results: ChatToolResult[]
}

export async function sendChatMessage(message: string, conversationId: string | null) {
  const response = await api.post<ChatResponse>('/api/chat', {
    message,
    conversation_id: conversationId
  }, { timeout: 190_000 })
  return response.data
}

export async function clearChatConversation(conversationId: string) {
  await api.delete(`/api/chat/${encodeURIComponent(conversationId)}`)
}
