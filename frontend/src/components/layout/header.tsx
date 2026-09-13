"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Bot, Activity, Loader2, AlertCircle } from "lucide-react"
import { Badge } from "@/components/ui/badge"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"

export function Header() {
  const [status, setStatus] = useState<"checking" | "waking" | "online" | "offline">("checking")

  useEffect(() => {
    let isMounted = true
    let wakingTimeout: NodeJS.Timeout

    const pingBackend = async () => {
      // If it takes more than 2 seconds, mark it as waking up
      wakingTimeout = setTimeout(() => {
        if (isMounted) setStatus("waking")
      }, 2000)

      try {
        const res = await fetch(`${API_BASE}/health`, { cache: "no-store" })
        if (res.ok && isMounted) {
          clearTimeout(wakingTimeout)
          setStatus("online")
        } else if (isMounted) {
          setStatus("offline")
        }
      } catch (err) {
        if (isMounted) {
          // If network failed on initial check, it's often waking from Render cold start
          setStatus("waking")
          // Retry in 5 seconds
          setTimeout(pingBackend, 5000)
        }
      }
    }

    pingBackend()

    return () => {
      isMounted = false
      clearTimeout(wakingTimeout)
    }
  }, [])

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
        {status === "online" && (
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
        )}

        {status === "waking" && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-1.5"
          >
            <Loader2 className="h-3.5 w-3.5 text-amber-500 animate-spin" />
            <Badge variant="warning" className="text-[10px] px-2 py-0">
              Waking Backend (~20s)
            </Badge>
          </motion.div>
        )}

        {status === "checking" && (
          <div className="flex items-center gap-1.5">
            <Loader2 className="h-3.5 w-3.5 text-muted-foreground animate-spin" />
            <span className="text-[10px] text-muted-foreground">Connecting...</span>
          </div>
        )}

        {status === "offline" && (
          <div className="flex items-center gap-1.5">
            <AlertCircle className="h-3.5 w-3.5 text-destructive" />
            <Badge variant="destructive" className="text-[10px] px-2 py-0">
              Offline
            </Badge>
          </div>
        )}
      </div>
    </header>
  )
}
