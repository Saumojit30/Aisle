"use client"

import { motion } from "framer-motion"

interface InterestTagsProps {
  interests: string[]
}

export function InterestTags({ interests }: InterestTagsProps) {
  if (!interests.length) {
    return (
      <p className="text-xs text-muted-foreground italic">No interests recorded yet</p>
    )
  }

  return (
    <div className="flex flex-wrap gap-1.5">
      {interests.map((interest, i) => (
        <motion.span
          key={interest}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{
            delay: i * 0.05,
            type: "spring" as const,
            stiffness: 200,
            damping: 15,
          }}
          whileHover={{ scale: 1.05 }}
          className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary hover:bg-primary/20 transition-colors cursor-default"
        >
          {interest}
        </motion.span>
      ))}
    </div>
  )
}
