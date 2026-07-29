"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { memoryMicroLabelStyle } from "@/components/personal/empty/shared/emptyStyles";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

export function LifeSectionLabel({
  children,
  explainerId,
}: {
  children: React.ReactNode;
  explainerId?: string;
}) {
  const tokens = useThemeTokens();
  if (!explainerId) {
    return <p style={memoryMicroLabelStyle(tokens)}>{children}</p>;
  }
  return (
    <div className="flex items-center gap-0.5">
      <p style={memoryMicroLabelStyle(tokens)}>{children}</p>
      <WidgetInfoButton explainerId={explainerId} />
    </div>
  );
}
