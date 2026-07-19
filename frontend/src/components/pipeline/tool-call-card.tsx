"use client"

import { motion, AnimatePresence } from "framer-motion"
import { Wrench, ArrowRight } from "lucide-react"
import type { ToolEvent } from "@/types"

interface ToolCallCardProps {
  events: ToolEvent[]
}

export function ToolCallCard({ events }: ToolCallCardProps) {
  const completedTools = events.filter((e) => e.status === "end")

  if (events.length === 0) return null

  return (
    <div className="px-2 space-y-1.5">
      <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground font-medium uppercase tracking-wider">
        <Wrench className="h-3 w-3" />
        Tool Calls
      </div>

      <AnimatePresence>
        {events.map((event, i) => (
          <motion.div
            key={`${event.node}-${event.tool}`}
            initial={{ opacity: 0, x: -10, height: 0 }}
            animate={{ opacity: 1, x: 0, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3, delay: i * 0.05 }}
            className="rounded-md border bg-card/50 px-2.5 py-1.5"
          >
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-medium font-mono">
                {event.tool}
              </span>
              <span className="text-[10px] text-muted-foreground">
                {event.status === "start" ? (
                  <span className="text-amber-500">running...</span>
                ) : (
                  <span className="text-emerald-500">
                    {event.duration_ms}ms
                  </span>
                )}
              </span>
            </div>

            {event.args && event.status === "start" && (
              <div className="mt-1 text-[10px] text-muted-foreground font-mono truncate">
                {Object.entries(event.args).map(([k, v]) => (
                  <span key={k} className="mr-2">
                    {k}: {String(v)}
                  </span>
                ))}
              </div>
            )}

            {event.result && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-1 flex items-start gap-1 text-[10px] text-muted-foreground"
              >
                <ArrowRight className="h-2.5 w-2.5 mt-0.5 shrink-0" />
                <span className="line-clamp-2">{event.result}</span>
              </motion.div>
            )}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
