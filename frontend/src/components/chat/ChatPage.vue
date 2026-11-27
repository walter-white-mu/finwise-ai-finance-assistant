<script setup lang="ts">
import { nextTick, ref } from 'vue'
import { Bot, MessageCircle, RotateCcw, Send, UserRound } from 'lucide-vue-next'
import { clearChatConversation, sendChatMessage } from '../../services/chatService'

type Message = { role: 'user' | 'assistant'; content: string }
const messages = ref<Message[]>([])
const draft = ref('')
const conversationId = ref<string | null>(null)
const loading = ref(false)
const error = ref('')
const transcript = ref<HTMLElement | null>(null)

async function submit() {
  const text = draft.value.trim()
  if (!text || loading.value) return
  messages.value.push({ role: 'user', content: text })
  draft.value = ''
  error.value = ''
  loading.value = true
  await nextTick()
  transcript.value?.scrollTo({ top: transcript.value.scrollHeight, behavior: 'smooth' })
  try {
    const response = await sendChatMessage(text, conversationId.value)
    conversationId.value = response.conversation_id
    messages.value.push({ role: 'assistant', content: response.assistant_message })
  } catch (reason) {
    const detail = (reason as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    error.value = detail || 'I could not reach the finance assistant. Check that the backend and local Ollama are running, then try again.'
  } finally {
    loading.value = false
    await nextTick()
    transcript.value?.scrollTo({ top: transcript.value.scrollHeight, behavior: 'smooth' })
  }
}

async function clearConversation() {
  if (conversationId.value) {
    try { await clearChatConversation(conversationId.value) } catch { /* UI clear still works if the backend has restarted. */ }
  }
  messages.value = []
  conversationId.value = null
  draft.value = ''
  error.value = ''
}
</script>

<template>
  <section class="mx-auto flex h-[min(72vh,760px)] min-h-[480px] max-w-4xl flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white text-left shadow-sm">
    <header class="flex items-center justify-between border-b border-slate-100 px-5 py-4 sm:px-6">
      <div class="flex items-center gap-3">
        <div class="rounded-xl bg-blue-50 p-2.5 text-blue-700"><Bot :size="21" /></div>
        <div><h2 class="text-lg font-semibold text-slate-900">FinWise assistant</h2><p class="text-xs text-slate-500">Private, local financial insights</p></div>
      </div>
      <button class="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-slate-100" @click="clearConversation" aria-label="Clear conversation"><RotateCcw :size="16" /> <span class="hidden sm:inline">Clear conversation</span></button>
    </header>

    <div ref="transcript" class="flex-1 space-y-5 overflow-y-auto bg-slate-50/60 p-4 sm:p-6" aria-live="polite">
      <div v-if="messages.length === 0" class="mx-auto mt-12 max-w-md text-center">
        <div class="mx-auto mb-4 grid size-12 place-items-center rounded-2xl bg-blue-100 text-blue-700"><MessageCircle :size="23" /></div>
        <h3 class="text-base font-semibold text-slate-900">Ask about your finances</h3>
        <p class="mt-2 text-sm leading-6 text-slate-500">I can look up your monthly spending, budgets, savings goals, and trends using your recorded data.</p>
        <button class="mt-5 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm text-slate-700 hover:border-blue-300" @click="draft = 'How much did I spend this month?'">How much did I spend this month?</button>
      </div>
      <div v-for="(message, index) in messages" :key="index" class="flex items-start gap-3" :class="message.role === 'user' ? 'flex-row-reverse' : ''">
        <div class="mt-1 grid size-8 shrink-0 place-items-center rounded-full" :class="message.role === 'user' ? 'bg-blue-600 text-white' : 'bg-blue-100 text-blue-700'"><UserRound v-if="message.role === 'user'" :size="16" /><Bot v-else :size="17" /></div>
        <div class="max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-6 sm:max-w-[75%]" :class="message.role === 'user' ? 'rounded-tr-sm bg-blue-600 text-white' : 'rounded-tl-sm border border-slate-200 bg-white text-slate-800'">{{ message.content }}</div>
      </div>
      <div v-if="loading" class="flex items-center gap-3 text-sm text-slate-500"><div class="grid size-8 place-items-center rounded-full bg-blue-100 text-blue-700"><Bot :size="17" /></div><span class="flex items-center gap-1 rounded-2xl border border-slate-200 bg-white px-4 py-3"><span class="animate-pulse">Thinking</span><span class="animate-bounce">…</span></span></div>
    </div>

    <div class="border-t border-slate-100 bg-white p-4 sm:px-6 sm:py-5">
      <p v-if="error" role="alert" class="mb-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>
      <form class="flex items-end gap-3" @submit.prevent="submit">
        <label class="sr-only" for="chat-message">Your message</label>
        <textarea id="chat-message" v-model="draft" rows="1" maxlength="4000" placeholder="Ask a question about your finances…" class="max-h-32 min-h-12 flex-1 resize-y rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-800 outline-none placeholder:text-slate-400 focus:border-blue-400 focus:ring-2 focus:ring-blue-100" @keydown.enter.exact.prevent="submit" />
        <button type="submit" :disabled="loading || !draft.trim()" class="grid size-12 shrink-0 place-items-center rounded-xl bg-blue-600 text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300" aria-label="Send message"><Send :size="18" /></button>
      </form>
      <p class="mt-2 text-center text-[11px] text-slate-400">Financial data is calculated by FinWise. AI can make mistakes.</p>
    </div>
  </section>
</template>
