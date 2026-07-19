"use client"

import { motion } from "framer-motion"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Package, Truck, CheckCircle2, XCircle, Calendar } from "lucide-react"
import type { Order } from "@/types"

const statusConfig: Record<
  Order["status"],
  { label: string; color: string; icon: React.ElementType }
> = {
  shipped: { label: "Shipped", color: "text-blue-500 bg-blue-50 dark:bg-blue-950/20", icon: Truck },
  processing: {
    label: "Processing",
    color: "text-amber-500 bg-amber-50 dark:bg-amber-950/20",
    icon: Package,
  },
  delivered: {
    label: "Delivered",
    color: "text-emerald-500 bg-emerald-50 dark:bg-emerald-950/20",
    icon: CheckCircle2,
  },
  cancelled: { label: "Cancelled", color: "text-red-500 bg-red-50 dark:bg-red-950/20", icon: XCircle },
}

interface OrderCardProps {
  order: Order
}

export function OrderCard({ order }: OrderCardProps) {
  const status = statusConfig[order.status]
  const StatusIcon = status.icon

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 200, damping: 20 }}
      whileHover={{ y: -2 }}
    >
      <Card>
        <CardContent className="p-4">
          <div className="flex items-start justify-between mb-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-sm font-semibold">{order.order_id}</h3>
                <Badge
                  variant="outline"
                  className={`text-[10px] ${status.color} border-0`}
                >
                  <StatusIcon className="h-3 w-3 mr-1" />
                  {status.label}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground">
                Customer: {order.customer_id}
              </p>
            </div>
            <span className="text-lg font-bold">
              ${order.total.toFixed(2)}
            </span>
          </div>

          <div className="space-y-1 text-xs text-muted-foreground">
            {order.items.map((item, i) => (
              <div key={i} className="flex items-center justify-between">
                <span>
                  {item.name} x{item.qty}
                </span>
                <span>${(item.price * item.qty).toFixed(2)}</span>
              </div>
            ))}
          </div>

          <Separator className="my-2" />

          <div className="flex items-center gap-4 text-[10px] text-muted-foreground">
            {order.estimated_delivery && (
              <div className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                <span>
                  Est. {new Date(order.estimated_delivery).toLocaleDateString()}
                </span>
              </div>
            )}
            {order.tracking && (
              <span className="font-mono">{order.tracking}</span>
            )}
            {order.carrier && <span>{order.carrier}</span>}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
