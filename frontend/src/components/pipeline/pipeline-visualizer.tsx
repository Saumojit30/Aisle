"use client"

import { motion, AnimatePresence } from "framer-motion"
import { PipelineNode } from "./pipeline-node"
import { ToolCallCard } from "./tool-call-card"
import { ProfilingCard } from "./profiling-card"
import { useChatStore } from "@/stores/chat-store"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { Cpu, ArrowDown } from "lucide-react"
import type { PipelineNode as PipelineNodeType } from "@/types"

const nodeOrder: PipelineNodeType[] = [
  "guardrail",
  "supervisor",
  "support",
  "order",
  "recommendation",
  "respond",
  "profiling",
]

export function PipelineVisualizer() {
  const { pipelineState, activeToolCalls, profilingData, isProcessing } = useChatStore()

  const completedCount = Object.values(pipelineState).filter(
    (s) => s.status === "completed" || s.status === "failed"
  ).length
  const totalNodes = nodeOrder.length

  const activeNode = nodeOrder.find(
    (n) => pipelineState[n]?.status === "active"
  )

  const specialistNodes: PipelineNodeType[] = ["support", "order", "recommendation", "respond"]
  const specialistActive = specialistNodes.find(
    (n) => pipelineState[n]?.status === "completed" || pipelineState[n]?.status === "active"
  )

  const showToolCalls = activeToolCalls.length > 0
  const showProfiling =
    pipelineState.profiling?.status === "completed" && profilingData !== null

  return (
    <div className="flex flex-col h-full bg-muted/20">
      <div className="p-3 border-b flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Cpu className="h-4 w-4 text-primary" />
          <span className="text-xs font-semibold">Pipeline</span>
        </div>
        {isProcessing && (
          <Badge variant="secondary" className="text-[10px]">
            <motion.span
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            >
              {completedCount}/{totalNodes}
            </motion.span>
          </Badge>
        )}
      </div>

      <ScrollArea className="flex-1">
        <div className="p-3">
          <div className="flex flex-col items-center">
            {/* Entry point */}
            <motion.div
              className="text-[10px] text-muted-foreground mb-1 px-3 py-1 rounded-full border border-dashed"
              animate={isProcessing ? { opacity: [0.5, 1, 0.5] } : {}}
              transition={{ duration: 2, repeat: Infinity }}
            >
              User Input
            </motion.div>

            <motion.div
              animate={isProcessing ? { y: [0, 3, 0] } : {}}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              <ArrowDown className="h-3 w-3 text-muted-foreground my-1" />
            </motion.div>

            {/* Main pipeline nodes */}
            {nodeOrder.map((nodeName, idx) => {
              const state = pipelineState[nodeName]
              if (!state) return null

              // For specialist nodes: show all but highlight the active one
              const isSpecialist = specialistNodes.includes(nodeName)
              const isInactiveSpecialist =
                isSpecialist &&
                nodeName !== specialistActive &&
                state.status !== "active" &&
                state.status !== "completed"

              if (isInactiveSpecialist && !isProcessing) {
                return null
              }

              return (
                <div key={nodeName} className="w-full">
                  <PipelineNode
                    name={nodeName}
                    status={state.status}
                    result={state.result}
                    isLast={idx === nodeOrder.length - 1}
                  />

                  {/* After specialist nodes, show tool calls */}
                  {isSpecialist && state.status === "completed" && showToolCalls && (
                    <div className="ml-4 mb-1">
                      <ToolCallCard events={activeToolCalls} />
                    </div>
                  )}

                  {/* After profiling, show profiling data */}
                  {nodeName === "profiling" && showProfiling && (
                    <div className="mt-2 mb-1">
                      <ProfilingCard data={profilingData!} />
                    </div>
                  )}

                  {/* Animated connecting arrow */}
                  {state.status === "active" && (
                    <motion.div
                      initial={{ scaleY: 0 }}
                      animate={{ scaleY: 1 }}
                      className="h-4 w-px bg-primary/50 mx-auto"
                    />
                  )}
                </div>
              )
            })}

            {/* END node */}
            {completedCount === totalNodes && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="mt-2 text-[10px] text-emerald-600 dark:text-emerald-400 px-3 py-1 rounded-full border border-emerald-200 dark:border-emerald-800 bg-emerald-50/50 dark:bg-emerald-950/20"
              >
                Complete
              </motion.div>
            )}
          </div>
        </div>
      </ScrollArea>

      {/* Mini budget indicator */}
      <BudgetMini />
    </div>
  )
}

function BudgetMini() {
  const { messages } = useChatStore()
  const lastMsg = messages[messages.length - 1]
  const budget = lastMsg?.budgetAfter

  if (!budget) return null

  return (
    <motion.div
      initial={{ y: 20 }}
      animate={{ y: 0 }}
      className="p-3 border-t"
    >
      <div className="text-[10px] text-muted-foreground mb-1 font-medium">
        Budget
      </div>
      <div className="space-y-1">
        <div className="flex items-center justify-between text-[10px]">
          <span>Daily</span>
          <span>${budget.daily_cost.toFixed(2)}</span>
        </div>
        <div className="h-1.5 rounded-full bg-muted overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${Math.min(budget.daily_usage_pct, 100)}%` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className={`h-full rounded-full ${
              budget.approaching_limit
                ? "bg-amber-500"
                : "bg-primary"
            }`}
          />
        </div>
        <div className="flex items-center justify-between text-[10px]">
          <span>Session</span>
          <span>${budget.session_cost.toFixed(4)}</span>
        </div>
        <div className="flex items-center justify-between text-[10px]">
          <span>Tokens</span>
          <span>{budget.session_tokens}</span>
        </div>
      </div>
    </motion.div>
  )
}
