"use client"

import { motion } from "framer-motion"
import { Bot, Activity } from "lucide-react"
import { Badge } from "@/components/ui/badge"

export function Header() {
  return (
    <header className="flex items-center justify-between px-6 py-3 border-b bg-card">
      <div className="flex items-center gap-3">
        <motion.div
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        >
          <Bot className="h-5 w-5 text-primary" />
        </motion.div>
        <div>
          <h1 className="text-sm font-semibold">LangGraph E-Commerce Agent</h1>
          <p className="text-xs text-muted-foreground">Multi-agent conversational assistant</p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center gap-1.5"
        >
          <motion.div
            animate={{ opacity: [1, 0.5, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <Activity className="h-3.5 w-3.5 text-emerald-500" />
          </motion.div>
          <Badge variant="success" className="text-[10px] px-2 py-0">
            Online
          </Badge>
        </motion.div>
      </div>
    </header>
  )
}
