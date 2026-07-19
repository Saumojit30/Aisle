"use client"

import { useEffect, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ScrollArea } from "@/components/ui/scroll-area"
import { MessageBubble } from "./message-bubble"
import { ChatInput } from "./chat-input"
import { TypingIndicator } from "./typing-indicator"
import { useChatStore } from "@/stores/chat-store"
import { useChatStream } from "@/hooks/use-chat-stream"

export function ChatInterface() {
  const { messages, isProcessing, agentTyping, sessionId } = useChatStore()
  const { sendMessage } = useChatStream()
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, agentTyping])

  return (
    <div className="flex flex-col h-full">
      <ScrollArea className="flex-1 px-4 py-4" ref={scrollRef}>
        <div className="max-w-3xl mx-auto space-y-4">
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center py-16 text-center"
            >
              <motion.div
                animate={{ y: [0, -8, 0] }}
                transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                className="mb-6"
              >
                <div className="h-16 w-16 rounded-2xl bg-primary/10 flex items-center justify-center">
                  <svg
                    className="h-8 w-8 text-primary"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={1.5}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z"
                    />
                  </svg>
                </div>
              </motion.div>
              <h2 className="text-xl font-semibold mb-2">
                E-Commerce Agent
              </h2>
              <p className="text-sm text-muted-foreground max-w-sm">
                Ask me about products, track orders, get recommendations, or
                request support. I route your request to the right specialist.
              </p>
              {sessionId && (
                <p className="text-xs text-muted-foreground/60 mt-4 font-mono">
                  Session: {sessionId}
                </p>
              )}
            </motion.div>
          )}

          <AnimatePresence mode="popLayout">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
          </AnimatePresence>

          <AnimatePresence>
            {agentTyping && <TypingIndicator />}
          </AnimatePresence>
        </div>
      </ScrollArea>

      <ChatInput onSend={sendMessage} isProcessing={isProcessing} />
    </div>
  )
}
