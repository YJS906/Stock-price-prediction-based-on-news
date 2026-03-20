import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-medium uppercase tracking-[0.24em]",
  {
    variants: {
      variant: {
        default: "border-white/12 bg-white/5 text-white/80",
        positive: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
        warning: "border-amber-400/30 bg-amber-400/10 text-amber-200",
        negative: "border-rose-500/30 bg-rose-500/10 text-rose-200",
        info: "border-cyan-400/30 bg-cyan-400/10 text-cyan-200"
      }
    },
    defaultVariants: {
      variant: "default"
    }
  }
);

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

