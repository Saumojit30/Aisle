"use client"

import { motion } from "framer-motion"
import { Brain, Tags, Target, ShoppingBag } from "lucide-react"
import type { ProfilingEvent } from "@/types"

interface ProfilingCardProps {
  data: ProfilingEvent
}

export function ProfilingCard({ data }: ProfilingCardProps) {
  if (!data.interests?.length && !data.preferred_categories?.length) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 200, damping: 20 }}
      className="px-2 space-y-2"
    >
      <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground font-medium uppercase tracking-wider">
        <Brain className="h-3 w-3" />
        Silent Profiling
      </div>

      <div className="rounded-md border bg-indigo-50/50 dark:bg-indigo-950/20 px-2.5 py-2 space-y-2">
        {data.preferred_categories && data.preferred_categories.length > 0 && (
          <div>
            <div className="flex items-center gap-1 text-[10px] text-indigo-600 dark:text-indigo-400 mb-1">
              <ShoppingBag className="h-3 w-3" />
              <span className="font-medium">Categories</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {data.preferred_categories.map((cat, i) => (
                <motion.span
                  key={cat}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.1 }}
                  className="text-[10px] px-1.5 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300"
                >
                  {cat}
                </motion.span>
              ))}
            </div>
          </div>
        )}

        {data.interests && data.interests.length > 0 && (
          <div>
            <div className="flex items-center gap-1 text-[10px] text-indigo-600 dark:text-indigo-400 mb-1">
              <Tags className="h-3 w-3" />
              <span className="font-medium">Interests</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {data.interests.map((interest, i) => (
                <motion.span
                  key={interest}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.05, type: "spring" }}
                  className="text-[10px] px-1.5 py-0.5 rounded-full bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300"
                >
                  {interest}
                </motion.span>
              ))}
            </div>
          </div>
        )}

        {data.budget_preference && (
          <div className="flex items-center gap-1 text-[10px]">
            <Target className="h-3 w-3 text-indigo-500" />
            <span className="text-muted-foreground">Budget:</span>
            <span className="font-medium text-indigo-600 dark:text-indigo-400 capitalize">
              {data.budget_preference}
            </span>
          </div>
        )}

        {data.summary && (
          <p className="text-[10px] text-muted-foreground italic leading-relaxed">
            &ldquo;{data.summary}&rdquo;
          </p>
        )}
      </div>
    </motion.div>
  )
}
