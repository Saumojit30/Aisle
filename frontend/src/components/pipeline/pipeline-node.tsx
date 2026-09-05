"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/utils"
import {
  ShieldCheck,
  Compass,
  Headphones,
  Package,
  Star,
  MessageCircle,
  UserSearch,
  CheckCircle2,
  XCircle,
  Loader2,
} from "lucide-react"
import type { PipelineNode as PipelineNodeType } from "@/types"

const nodeConfig: Record<
  PipelineNodeType,
  { label: string; icon: React.ElementType; color: string }
> = {
  guardrail: { label: "Guardrail", icon: ShieldCheck, color: "text-violet-500" },
  supervisor: { label: "Supervisor", icon: Compass, color: "text-blue-500" },
  support: { label: "Support", icon: Headphones, color: "text-emerald-500" },
  order: { label: "Order", icon: Package, color: "text-amber-500" },
  recommendation: { label: "Recommend", icon: Star, color: "text-rose-500" },
  respond: { label: "Respond", icon: MessageCircle, color: "text-cyan-500" },
  profiling: { label: "Profiling", icon: UserSearch, color: "text-indigo-500" },
}

interface PipelineNodeProps {
  name: PipelineNodeType
  status: "pending" | "active" | "completed" | "failed" | "skipped"
  result?: string
  elapsed_ms?: number
  isLast?: boolean
}

export function PipelineNode({ name, status, result, elapsed_ms, isLast }: PipelineNodeProps) {
  const config = nodeConfig[name]
  const Icon = config.icon

  const statusIcon = () => {
    switch (status) {
      case "active":
        return <Loader2 className="h-3.5 w-3.5 animate-spin" />
      case "completed":
        return <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
      case "failed":
        return <XCircle className="h-3.5 w-3.5 text-red-500" />
      default:
        return null
    }
  }

  return (
    <motion.div
      layout
      className="relative"
      animate={{
        scale: status === "active" ? 1.02 : 1,
      }}
      transition={{ duration: 0.3 }}
    >
      <motion.div
        className={cn(
          "flex items-center gap-2.5 px-3 py-2 rounded-lg border transition-colors",
          status === "active" && "border-primary/50 bg-primary/5 shadow-sm",
          status === "completed" && "border-emerald-200 dark:border-emerald-800 bg-emerald-50/50 dark:bg-emerald-950/20",
          status === "failed" && "border-red-200 dark:border-red-800 bg-red-50/50 dark:bg-red-950/20",
          status === "pending" && "border-muted bg-muted/20 opacity-50",
          status === "skipped" && "border-muted bg-muted/20 opacity-30"
        )}
      >
        <motion.div
          animate={
            status === "active"
              ? {
                  scale: [1, 1.15, 1],
                  transition: { duration: 1.5, repeat: Infinity },
                }
              : {}
          }
        >
          <Icon className={cn("h-4 w-4", config.color)} />
        </motion.div>

        <span
          className={cn(
            "text-xs font-medium",
            status === "active" && "text-primary"
          )}
        >
          {config.label}
        </span>

        {statusIcon() && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 400, damping: 15 }}
          >
            {statusIcon()}
          </motion.div>
        )}
      </motion.div>

      {/* Latency & Result badges */}
      <div className="absolute -top-2 -right-2 flex items-center gap-1 z-10">
        {elapsed_ms !== undefined && status === "completed" && (
          <motion.span
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-[9px] px-1.5 py-0.5 rounded-full bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300 font-mono font-medium shadow-xs"
          >
            {elapsed_ms < 1000 ? `${elapsed_ms}ms` : `${(elapsed_ms / 1000).toFixed(1)}s`}
          </motion.span>
        )}
        {result && status === "completed" && (
          <motion.span
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-[9px] px-1.5 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-900 text-emerald-700 dark:text-emerald-300 font-medium shadow-xs"
          >
            {result}
          </motion.span>
        )}
      </div>

      {/* Connecting line */}
      {!isLast && (
        <motion.div
          className="h-4 w-px bg-border mx-auto my-0.5"
          animate={
            status === "completed"
              ? { backgroundColor: ["rgb(203 213 225)", "rgb(34 197 94)", "rgb(203 213 225)"] }
              : {}
          }
          transition={{ duration: 0.5 }}
        />
      )}
    </motion.div>
  )
}
