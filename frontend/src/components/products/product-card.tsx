"use client"

import { motion } from "framer-motion"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Star, Package, ShoppingCart } from "lucide-react"
import { cn } from "@/lib/utils"
import type { Product } from "@/types"

interface ProductCardProps {
  product: Product
}

export function ProductCard({ product }: ProductCardProps) {
  const stockStatus =
    product.stock < 10
      ? { label: "Low stock", variant: "warning" as const }
      : { label: "In stock", variant: "success" as const }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: "spring", stiffness: 200, damping: 20 }}
      whileHover={{ y: -4 }}
      className="perspective-1000"
    >
      <motion.div
        whileHover={{ rotateX: 3, rotateY: -3 }}
        transition={{ type: "spring", stiffness: 200, damping: 15 }}
      >
        <Card className="h-full overflow-hidden">
          <div className="h-32 bg-gradient-to-br from-primary/5 to-primary/10 flex items-center justify-center">
            <motion.div
              animate={{ y: [0, -3, 0] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            >
              <Package className="h-10 w-10 text-primary/30" />
            </motion.div>
          </div>
          <CardContent className="p-4 pb-2">
            <div className="flex items-start justify-between mb-1">
              <h3 className="text-sm font-semibold">{product.name}</h3>
              <Badge variant={stockStatus.variant} className="text-[10px]">
                {stockStatus.label}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground mb-2">
              {product.category}
            </p>
            <div className="flex items-center gap-1 mb-2">
              <Star className="h-3 w-3 text-amber-500 fill-amber-500" />
              <span className="text-xs font-medium">{product.rating}</span>
              <span className="text-xs text-muted-foreground">
                ({product.stock} units)
              </span>
            </div>
            <div className="flex flex-wrap gap-1">
              {product.tags.slice(0, 3).map((tag) => (
                <span
                  key={tag}
                  className="text-[9px] px-1.5 py-0.5 rounded-full bg-muted text-muted-foreground"
                >
                  {tag}
                </span>
              ))}
            </div>
          </CardContent>
          <CardFooter className="p-4 pt-2 flex items-center justify-between">
            <span className="text-lg font-bold">${product.price.toFixed(2)}</span>
            <Button size="sm" variant="outline" className="h-8 text-xs gap-1">
              <ShoppingCart className="h-3 w-3" />
              View
            </Button>
          </CardFooter>
        </Card>
      </motion.div>
    </motion.div>
  )
}
