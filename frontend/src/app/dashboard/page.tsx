"use client"

import { motion } from "framer-motion"
import { useQuery } from "@tanstack/react-query"
import { fetchAdminStats, fetchBudget } from "@/lib/api"
import { useChatStore } from "@/stores/chat-store"
import { BudgetGauge } from "@/components/dashboard/budget-gauge"
import { MetricCard } from "@/components/dashboard/metric-card"
import { CostChart } from "@/components/dashboard/cost-chart"
import {
  DollarSign,
  Activity,
  AlertTriangle,
  TrendingUp,
  Users,
} from "lucide-react"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

export default function DashboardPage() {
  const sessionId = useChatStore((s) => s.sessionId)

  const { data: stats } = useQuery({
    queryKey: ["admin-stats"],
    queryFn: fetchAdminStats,
    refetchInterval: 10_000,
  })

  const { data: budget } = useQuery({
    queryKey: ["budget", sessionId],
    queryFn: () => fetchBudget(sessionId || ""),
    enabled: !!sessionId,
    refetchInterval: 10_000,
  })

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.08 },
    },
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="h-full overflow-y-auto p-6 space-y-6"
    >
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Agent performance metrics and budget tracking
        </p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Daily Cost"
          value={`$${stats?.budget.daily_cost.toFixed(2) || "0.00"}`}
          subtitle={`of $10.00 limit`}
          icon={DollarSign}
          trend="up"
        />
        <MetricCard
          title="Total Tokens"
          value={(stats?.budget.total_tokens_all_time || 0).toLocaleString()}
          subtitle="All time"
          icon={Activity}
          trend="up"
        />
        <MetricCard
          title="Customers Profiled"
          value={String(stats?.memory.customers || 0)}
          subtitle="In memory store"
          icon={Users}
          trend="neutral"
        />
        <MetricCard
          title="Active Sessions"
          value={String(stats?.memory.active_sessions || 0)}
          subtitle="Currently tracked"
          icon={TrendingUp}
          trend="neutral"
        />
      </div>

      {/* Budget Gauges */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Daily Budget</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center pb-6">
              <div className="relative">
                <BudgetGauge
                  value={stats?.budget.daily_cost || 0}
                  max={10}
                  label="Daily Spend"
                  sublabel={`$${(stats?.budget.daily_cost || 0).toFixed(2)} / $10.00`}
                  color={
                    (stats?.budget.daily_usage_pct || 0) >= 80
                      ? "danger"
                      : (stats?.budget.daily_usage_pct || 0) >= 50
                      ? "warning"
                      : "default"
                  }
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
        >
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Session Budget</CardTitle>
            </CardHeader>
            <CardContent className="pb-6">
              {budget ? (
                <div className="space-y-4 pt-2">
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                      <span className="text-muted-foreground">Session Cost</span>
                      <span className="font-medium">
                        ${budget.session_cost.toFixed(4)}
                      </span>
                    </div>
                    <Progress
                      value={(budget.session_cost / 2) * 100}
                      className="h-2"
                    />
                    <div className="flex justify-between text-[10px] text-muted-foreground">
                      <span>of $2.00 limit</span>
                      <span>
                        {((budget.session_cost / 2) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                      <span className="text-muted-foreground">Session Tokens</span>
                      <span className="font-medium">
                        {budget.session_tokens.toLocaleString()}
                      </span>
                    </div>
                    <Progress
                      value={(budget.session_tokens / 50000) * 100}
                      className="h-2"
                    />
                    <div className="flex justify-between text-[10px] text-muted-foreground">
                      <span>of 50,000 limit</span>
                      <span>
                        {((budget.session_tokens / 50000) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-muted-foreground text-center py-8">
                  Start a chat session to see budget data
                </p>
              )}
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Usage Alerts</CardTitle>
            </CardHeader>
            <CardContent className="pb-6">
              <div className="space-y-3 pt-2">
                <div className="flex items-center gap-3 p-2 rounded-lg bg-amber-50 dark:bg-amber-950/20">
                  <AlertTriangle className="h-4 w-4 text-amber-500 shrink-0" />
                  <div>
                    <p className="text-xs font-medium text-amber-700 dark:text-amber-400">
                      {(stats?.budget.daily_usage_pct || 0) >= 80
                        ? "Approaching daily limit"
                        : "Budget healthy"}
                    </p>
                    <p className="text-[10px] text-muted-foreground">
                      {(stats?.budget.daily_usage_pct || 0).toFixed(0)}% of daily
                      budget used
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-2 rounded-lg bg-muted/50">
                  <Activity className="h-4 w-4 text-primary shrink-0" />
                  <div>
                    <p className="text-xs font-medium">Request Rate</p>
                    <p className="text-[10px] text-muted-foreground">
                      {stats?.budget.approaching_limit
                        ? "Near rate limit"
                        : "Normal operation"}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Cost Chart */}
      <CostChart />
    </motion.div>
  )
}
