"use client"

import { ChatInterface } from "@/components/chat/chat-interface"
import { PipelineVisualizer } from "@/components/pipeline/pipeline-visualizer"
import { useChatStore } from "@/stores/chat-store"
import { AnimatePresence, motion } from "framer-motion"
import { X, Eye, EyeOff } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useState } from "react"

export default function ChatPage() {
  const [showPipeline, setShowPipeline] = useState(true)
  const messages = useChatStore((s) => s.messages)

  return (
    <div className="flex h-full">
      {/* Chat panel */}
      <div className="flex-1 min-w-0">
        <ChatInterface />
      </div>

      {/* Toggle button */}
      <AnimatePresence>
        {!showPipeline && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="absolute right-4 top-20 z-10"
          >
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowPipeline(true)}
              className="gap-2 shadow-sm"
            >
              <Eye className="h-4 w-4" />
              Pipeline
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Pipeline panel */}
      <AnimatePresence>
        {showPipeline && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 300, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="border-l bg-card overflow-hidden"
          >
            <div className="flex items-center justify-between p-3 border-b">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Agent Runtime
              </span>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={() => setShowPipeline(false)}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
            <PipelineVisualizer />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
