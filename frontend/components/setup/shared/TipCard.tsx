"use client";

import { GuidedSetupTip } from "@/components/setup/GuidedSetupTip";

/** Alias for GuidedSetupTip — shared tip card in setup flows. */
export function TipCard({ tip }: { tip: string }) {
  return <GuidedSetupTip tip={tip} />;
}
