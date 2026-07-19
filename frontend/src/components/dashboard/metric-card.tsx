"use client"

import { motion } from "framer-motion"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface MetricCardProps {
  title: string
  value: string
  subtitle?: string
  icon: React.ElementType
  trend?: "up" | "down" | "neutral"
  className?: string
}

export function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  className,
}: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 200, damping: 20 }}
      whileHover={{ y: -2 }}
    >
      <Card className={cn("h-full", className)}>
        <CardContent className="p-4">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground">{title}</p>
              <motion.p
                initial={{ scale: 0.5 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 300, damping: 15 }}
                className="text-2xl font-bold"
              >
                {value}
              </motion.p>
              {subtitle && (
                <p className="text-xs text-muted-foreground">{subtitle}</p>
              )}
            </div>
            <div className="h-9 w-9 rounded-lg bg-primary/10 flex items-center justify-center">
              <Icon className="h-4 w-4 text-primary" />
            </div>
          </div>

          {trend && (
            <div className="mt-2 flex items-center gap-1">
              <motion.div
                animate={{ rotate: trend === "up" ? 0 : 180 }}
                className={cn(
                  "text-xs",
                  trend === "up" && "text-emerald-500",
                  trend === "down" && "text-red-500"
                )}
              >
                ▲
              </motion.div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
