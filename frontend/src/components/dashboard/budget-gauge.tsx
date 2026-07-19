"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

interface BudgetGaugeProps {
  value: number
  max: number
  label: string
  sublabel: string
  className?: string
  color?: "default" | "warning" | "danger"
}

export function BudgetGauge({
  value,
  max,
  label,
  sublabel,
  className,
  color = "default",
}: BudgetGaugeProps) {
  const percentage = max > 0 ? Math.min((value / max) * 100, 100) : 0
  const radius = 40
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (percentage / 100) * circumference

  const strokeColor =
    color === "danger"
      ? "stroke-red-500"
      : color === "warning"
      ? "stroke-amber-500"
      : "stroke-primary"

  return (
    <div className={cn("flex flex-col items-center", className)}>
      <div className="relative">
        <svg width="100" height="100" viewBox="0 0 100 100" className="-rotate-90">
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-muted/20"
          />
          <motion.circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            strokeWidth="8"
            strokeLinecap="round"
            className={strokeColor}
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.2, ease: "easeOut" }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-lg font-bold"
          >
            {percentage.toFixed(0)}%
          </motion.span>
        </div>
      </div>
      <div className="mt-2 text-center">
        <p className="text-sm font-medium">{label}</p>
        <p className="text-xs text-muted-foreground">{sublabel}</p>
      </div>
    </div>
  )
}
