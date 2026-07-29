"use client";

import { GuidedSetupExplainer } from "@/components/setup/GuidedSetupExplainer";

/** Alias for GuidedSetupExplainer — shared explainer control. */
export function ExplainerButton({
  title,
  body,
}: {
  title: string;
  body: string;
}) {
  return <GuidedSetupExplainer title={title} body={body} />;
}
