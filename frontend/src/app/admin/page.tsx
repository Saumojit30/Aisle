"use client"

import { motion } from "framer-motion"
import { useQuery } from "@tanstack/react-query"
import { fetchAdminStats, fetchCustomers } from "@/lib/api"
import { MetricCard } from "@/components/dashboard/metric-card"
import { CustomerProfileCard } from "@/components/admin/customer-profile-card"
import { ApprovalQueue } from "@/components/admin/approval-queue"
import { Users, Database, Activity, BrainCircuit } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function AdminPage() {
  const { data: stats } = useQuery({
    queryKey: ["admin-stats"],
    queryFn: fetchAdminStats,
    refetchInterval: 10_000,
  })

  const { data: customers } = useQuery({
    queryKey: ["customers"],
    queryFn: fetchCustomers,
  })

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="h-full overflow-y-auto p-6 space-y-6"
    >
      <div>
        <h1 className="text-2xl font-bold">Admin</h1>
        <p className="text-sm text-muted-foreground">
          Customer profiling and memory store insights
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Customers"
          value={String(stats?.memory.customers || 0)}
          subtitle="Profiled in memory"
          icon={Users}
        />
        <MetricCard
          title="Active Sessions"
          value={String(stats?.memory.active_sessions || 0)}
          subtitle="Linked to customers"
          icon={Activity}
        />
        <MetricCard
          title="Memory Store"
          value="In-Memory"
          subtitle="Python dict store"
          icon={Database}
        />
        <MetricCard
          title="Profiling Agent"
          value="Silent"
          subtitle="Extracts preferences"
          icon={BrainCircuit}
        />
      </div>

      {/* Human Approval Queue (HITL) */}
      <ApprovalQueue />

      {/* Customer Profiles */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Customer Profiles</h2>
        {customers && customers.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {customers.map((customer) => (
              <CustomerProfileCard key={customer.customer_id} customer={customer} />
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="py-12 text-center">
              <BrainCircuit className="h-8 w-8 mx-auto mb-3 text-muted-foreground/50" />
              <p className="text-sm text-muted-foreground">
                No customer profiles yet
              </p>
              <p className="text-xs text-muted-foreground/60 mt-1">
                Profiles are created automatically when customers interact with the agent
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Memory Store Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Memory Store Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Storage Type</span>
              <span className="font-medium">In-memory Python dict</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Thread Safety</span>
              <span className="font-medium">threading.RLock()</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Profiling Model</span>
              <span className="font-medium">mixtral-8x7b-32768</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Profile Fields</span>
              <span className="font-medium">
                preferences, interests, interaction_count
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
