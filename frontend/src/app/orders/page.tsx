"use client"

import { motion } from "framer-motion"
import { useQuery } from "@tanstack/react-query"
import { fetchOrders } from "@/lib/api"
import { OrderCard } from "@/components/orders/order-card"
import { ShoppingCart, Filter } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useState } from "react"

const statusFilters = ["All", "Processing", "Shipped", "Delivered", "Cancelled"]

export default function OrdersPage() {
  const { data: orders, isLoading } = useQuery({
    queryKey: ["orders"],
    queryFn: fetchOrders,
  })

  const [filter, setFilter] = useState("All")

  const filtered = (orders || []).filter((o) => {
    if (filter === "All") return true
    return o.status === filter.toLowerCase()
  })

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="h-full overflow-y-auto p-6 space-y-6"
    >
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">Orders</h1>
          <p className="text-sm text-muted-foreground">
            Order management ({orders?.length || 0} orders)
          </p>
        </div>
      </div>

      {/* Status filter */}
      <div className="flex gap-2 overflow-x-auto pb-1">
        {statusFilters.map((s) => (
          <Button
            key={s}
            variant={filter === s ? "default" : "outline"}
            size="sm"
            onClick={() => setFilter(s)}
            className="whitespace-nowrap text-xs"
          >
            {s}
          </Button>
        ))}
      </div>

      {/* Order List */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <div className="space-y-2 animate-pulse">
                  <div className="h-4 bg-muted rounded w-1/4" />
                  <div className="h-3 bg-muted rounded w-1/2" />
                  <div className="h-3 bg-muted rounded w-1/3" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filtered.length > 0 ? (
        <div className="space-y-3">
          {filtered.map((order) => (
            <OrderCard key={order.order_id} order={order} />
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <ShoppingCart className="h-8 w-8 mx-auto mb-3 text-muted-foreground/50" />
            <p className="text-sm text-muted-foreground">No orders found</p>
            <p className="text-xs text-muted-foreground/60 mt-1">
              {filter !== "All"
                ? `No orders with status "${filter}"`
                : "Order data will appear here"}
            </p>
          </CardContent>
        </Card>
      )}
    </motion.div>
  )
}
