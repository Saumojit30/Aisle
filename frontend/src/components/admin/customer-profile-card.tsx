"use client"

import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { InterestTags } from "./interest-tags"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { CalendarDays, MessageSquare } from "lucide-react"
import type { CustomerMemory } from "@/types"

interface CustomerProfileCardProps {
  customer: CustomerMemory
}

export function CustomerProfileCard({ customer }: CustomerProfileCardProps) {
  const initials = customer.customer_id.replace("CUST-", "C")
  const prefSummary = customer.preferences?._summary as string | undefined

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 200, damping: 20 }}
      whileHover={{ y: -2 }}
    >
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-3">
            <Avatar className="h-10 w-10">
              <AvatarFallback className="text-xs bg-primary/10 text-primary">
                {initials}
              </AvatarFallback>
            </Avatar>
            <div>
              <CardTitle className="text-sm">{customer.customer_id}</CardTitle>
              <div className="flex items-center gap-2 mt-0.5">
                <Badge variant="secondary" className="text-[10px]">
                  {customer.interaction_count} interactions
                </Badge>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {prefSummary && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-xs text-muted-foreground italic leading-relaxed"
            >
              &ldquo;{prefSummary}&rdquo;
            </motion.p>
          )}

          <div>
            <p className="text-xs font-medium text-muted-foreground mb-1.5">
              Interests
            </p>
            <InterestTags interests={customer.interests} />
          </div>

          {Object.keys(customer.preferences).length > 0 && (
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-1.5">
                Preferences
              </p>
              <div className="space-y-1">
                {Object.entries(customer.preferences)
                  .filter(([k]) => k !== "_summary")
                  .map(([key, val]) => (
                    <div
                      key={key}
                      className="flex items-center justify-between text-xs"
                    >
                      <span className="text-muted-foreground capitalize">
                        {key.replace(/_/g, " ")}
                      </span>
                      <span className="font-medium">
                        {typeof val === "boolean" ? "Yes" : String(val)}
                      </span>
                    </div>
                  ))}
              </div>
            </div>
          )}

          <div className="flex items-center gap-4 text-[10px] text-muted-foreground pt-1 border-t">
            <div className="flex items-center gap-1">
              <CalendarDays className="h-3 w-3" />
              <span>Since {customer.created_at?.slice(0, 10)}</span>
            </div>
            <div className="flex items-center gap-1">
              <MessageSquare className="h-3 w-3" />
              <span>{customer.interaction_count} chats</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
