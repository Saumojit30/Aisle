"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/utils"
import { Bot, User } from "lucide-react"
import type { Message } from "@/types"

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user"

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, x: isUser ? 20 : -20 }}
      animate={{ opacity: 1, y: 0, x: 0 }}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
      className={cn("flex gap-3 w-full", isUser ? "justify-end" : "justify-start")}
    >
      {!isUser && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 400, damping: 20, delay: 0.1 }}
          className="flex-shrink-0 h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center mt-1"
        >
          <Bot className="h-4 w-4 text-primary" />
        </motion.div>
      )}

      <div className={cn("max-w-[75%]", isUser && "order-1")}>
        <motion.div
          layout
          className={cn(
            "rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
            isUser
              ? "bg-primary text-primary-foreground rounded-br-md"
              : "bg-muted/50 border rounded-bl-md"
          )}
        >
          {message.content}
        </motion.div>

        {/* Budget info if present */}
        {message.budgetAfter && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            className="mt-1 flex gap-2 text-[10px] text-muted-foreground"
          >
            <span>Tokens: {message.budgetAfter.session_tokens}</span>
            <span>Session: ${message.budgetAfter.session_cost.toFixed(4)}</span>
            <span>
              Daily: {message.budgetAfter.daily_usage_pct.toFixed(0)}%
            </span>
          </motion.div>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0 h-8 w-8 rounded-full bg-primary flex items-center justify-center mt-1">
          <User className="h-4 w-4 text-primary-foreground" />
        </div>
      )}
    </motion.div>
  )
}
