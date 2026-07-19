"use client"

import { useCallback, useRef, useEffect } from "react"
import { useChatStore } from "@/stores/chat-store"
import type { PipelineNode, Message } from "@/types"
import type { ChatCompleteData } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"

export function useChatStream() {
  const store = useChatStore()
  const esRef = useRef<EventSource | null>(null)

  useEffect(() => {
    return () => {
      esRef.current?.close()
    }
  }, [])

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || store.isProcessing) return

      const userMsg: Message = {
        id: `user-${Date.now()}`,
        role: "user",
        content: content.trim(),
        timestamp: new Date(),
      }

      store.addMessage(userMsg)
      store.setIsProcessing(true)
      store.setAgentTyping(true)
      store.resetPipeline()

      const sessionId = store.sessionId || `sess_${Math.random().toString(36).slice(2, 14)}`
      if (!store.sessionId) store.setSessionId(sessionId)
      if (!store.customerId) store.setCustomerId("CUST-001")

      const params = new URLSearchParams({
        message: content.trim(),
        session_id: sessionId,
        customer_id: store.customerId || "CUST-001",
      })

      // Close any previous connection
      esRef.current?.close()

      const es = new EventSource(`${API_BASE}/chat/stream?${params}`)
      esRef.current = es

      let assistantId = `ai-${Date.now()}`

      return new Promise<void>((resolve) => {
        // Guard against stale connection
        const timeout = setTimeout(() => {
          es.close()
          esRef.current = null
          finishWithError("Request timed out. The backend may be unavailable.")
          resolve()
        }, 30000)

        function finishWithError(msg: string) {
          store.setAgentTyping(false)
          store.setIsProcessing(false)
          store.addMessage({
            id: assistantId,
            role: "assistant",
            content: msg,
            timestamp: new Date(),
          })
        }

        es.addEventListener("node_start", (e: MessageEvent) => {
          const data = JSON.parse(e.data)
          store.setPipelineNode(data.node as PipelineNode, "active")
        })

        es.addEventListener("node_end", (e: MessageEvent) => {
          const data = JSON.parse(e.data)
          store.setPipelineNode(
            data.node as PipelineNode,
            data.result === "blocked" ? "failed" : "completed",
            data.result
          )
        })

        es.addEventListener("tool_start", (e: MessageEvent) => {
          const data = JSON.parse(e.data)
          store.addToolEvent({
            node: data.node as PipelineNode,
            tool: data.tool,
            status: "start",
            args: data.args,
          })
        })

        es.addEventListener("tool_end", (e: MessageEvent) => {
          const data = JSON.parse(e.data)
          store.addToolEvent({
            node: data.node as PipelineNode,
            tool: data.tool,
            status: "end",
            result: data.result,
            duration_ms: data.duration_ms,
          })
        })

        es.addEventListener("thinking", () => {
          store.setAgentTyping(true)
        })

        es.addEventListener("complete", (e: MessageEvent) => {
          clearTimeout(timeout)
          es.close()
          esRef.current = null

          const data: ChatCompleteData & { session_id: string } = JSON.parse(e.data)

          store.setAgentTyping(false)
          store.setIsProcessing(false)

          if (data.session_id) {
            store.setSessionId(data.session_id)
          }

          store.addMessage({
            id: assistantId,
            role: "assistant",
            content: data.reply,
            timestamp: new Date(),
            budgetAfter: data.budget,
            pipelineEvents: [],
          })

          resolve()
        })

        es.addEventListener("error", (_e: Event) => {
          clearTimeout(timeout)

          // EventSource fires "error" when connection fails or stream ends
          // If we already got a "complete" event, this is just stream closure
          if (es.readyState === EventSource.CLOSED) {
            store.setAgentTyping(false)
            store.setIsProcessing(false)
            finishWithError(
              "Connection lost. Please check that the backend is running on port 8080."
            )
            resolve()
          }
        })

        // Also handle the generic onerror for initial connection failure
        es.onerror = () => {
          clearTimeout(timeout)
          if (es.readyState === EventSource.CLOSED) {
            es.close()
            esRef.current = null
            store.setAgentTyping(false)
            store.setIsProcessing(false)
            finishWithError(
              "Could not connect to the agent backend. Make sure the server is running."
            )
            resolve()
          }
        }
      })
    },
    [store]
  )

  return { sendMessage }
}
