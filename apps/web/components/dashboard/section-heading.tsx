import { ReactNode } from "react";

import { Badge } from "@/components/ui/badge";

export function SectionHeading({
  eyebrow,
  title,
  description,
  action
}: {
  eyebrow?: string;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="mb-5 flex items-end justify-between gap-4">
      <div className="space-y-2">
        {eyebrow ? <Badge variant="default">{eyebrow}</Badge> : null}
        <div>
          <h2 className="text-xl font-semibold tracking-tight text-white">{title}</h2>
          <p className="mt-1 text-sm text-muted-foreground">{description}</p>
        </div>
      </div>
      {action}
    </div>
  );
}

