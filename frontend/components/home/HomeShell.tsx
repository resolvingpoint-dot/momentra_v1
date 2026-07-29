"use client";

import type { AppContext } from "@/lib/appContext";
import { ContextHomePlaceholder } from "@/components/home/ContextHomePlaceholder";

const TITLES: Record<AppContext, string> = {
  personal: "My Money",
  group: "Group",
  business: "Business",
  circle: "Circle",
};

const VARIANTS: Record<AppContext, "personal" | "group" | "business" | "circle"> = {
  personal: "personal",
  group: "group",
  business: "business",
  circle: "circle",
};

export function HomeShell({ context }: { context: AppContext }) {
  return (
    <ContextHomePlaceholder
      variant={VARIANTS[context]}
      title={TITLES[context]}
    />
  );
}
