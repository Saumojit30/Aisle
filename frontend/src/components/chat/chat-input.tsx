"use client"

import { useState, useRef, useEffect } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Send, Sparkles, StopCircle } from "lucide-react"
import { cn } from "@/lib/utils"

const suggestions = [
  "Show me wireless headphones",
  "Track order ORD-001",
  "What running shoes do you have?",
  "Cancel my order",
  "Recommend me a gift",
]

interface ChatInputProps {
  onSend: (message: string) => void
  isProcessing: boolean
}

export function ChatInput({ onSend, isProcessing }: ChatInputProps) {
  const [input, setInput] = useState("")
  const [showSuggestions, setShowSuggestions] = useState(true)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!isProcessing) {
      inputRef.current?.focus()
    }
  }, [isProcessing])

  const handleSubmit = () => {
    if (!input.trim() || isProcessing) return
    onSend(input.trim())
    setInput("")
    setShowSuggestions(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="border-t bg-card p-4">
      {showSuggestions && !input && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-wrap gap-2 mb-3"
        >
          {suggestions.map((s, i) => (
            <motion.button
              key={s}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.05 }}
              onClick={() => {
                setInput(s)
                inputRef.current?.focus()
              }}
              className="text-xs px-3 py-1.5 rounded-full border bg-muted/30 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
            >
              <Sparkles className="h-3 w-3 inline mr-1" />
              {s}
            </motion.button>
          ))}
        </motion.div>
      )}

      <div className="flex items-center gap-2">
        <div className="flex-1 relative">
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about products, orders, or support..."
            disabled={isProcessing}
            className={cn(
              "w-full rounded-xl border bg-background px-4 py-2.5 text-sm",
              "placeholder:text-muted-foreground/60",
              "focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "transition-all duration-200"
            )}
          />
        </div>

        <motion.div whileTap={{ scale: 0.9 }}>
          <Button
            onClick={isProcessing ? undefined : handleSubmit}
            disabled={!input.trim()}
            size="icon"
            className={cn(
              "h-10 w-10 rounded-xl shrink-0",
              isProcessing && "bg-destructive hover:bg-destructive/90"
            )}
          >
            {isProcessing ? (
              <StopCircle className="h-4 w-4" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </motion.div>
      </div>
    </div>
  )
}
