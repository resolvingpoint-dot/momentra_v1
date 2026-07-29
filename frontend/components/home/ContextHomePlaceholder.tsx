"use client";

import { GroupHomePlaceholder } from "@/components/home/GroupHomePlaceholder";
import { PersonalHomePlaceholder } from "@/components/home/PersonalHomePlaceholder";
import { ContextHomePlaceholderLegacy } from "@/components/home/ContextHomePlaceholderLegacy";
import { CircleHomePlaceholder } from "@/components/circle/CircleHomePlaceholder";

type ContextHomePlaceholderProps = {
  variant: "personal" | "group" | "business" | "circle";
  title: string;
};

export function ContextHomePlaceholder(props: ContextHomePlaceholderProps) {
  const { variant, title } = props;
  if (variant === "circle") {
    return <CircleHomePlaceholder title={title} />;
  }
  if (variant === "group") {
    return <GroupHomePlaceholder title={title} />;
  }
  if (variant === "personal") {
    return <PersonalHomePlaceholder title={title} />;
  }
  return <ContextHomePlaceholderLegacy variant="business" title={title} />;
}
