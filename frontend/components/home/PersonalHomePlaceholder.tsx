"use client";

import { ContextHomePlaceholderLegacy } from "@/components/home/ContextHomePlaceholderLegacy";

type PersonalHomePlaceholderProps = {
  title: string;
};

/**
 * Personal / My Money home shell entry (parity with GroupHomePlaceholder).
 * Soft mutations + session store live in the shared legacy implementation;
 * MomentraAppShell owns ensurePersonalSession() on context entry.
 */
export function PersonalHomePlaceholder({ title }: PersonalHomePlaceholderProps) {
  return <ContextHomePlaceholderLegacy variant="personal" title={title} />;
}
