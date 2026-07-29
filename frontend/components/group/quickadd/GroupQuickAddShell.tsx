"use client";

import { X } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

type GroupQuickAddShellProps = {
  title: string;
  children: React.ReactNode;
  onClose: () => void;
};

export function GroupQuickAddShell({ title, children, onClose }: GroupQuickAddShellProps) {
  const tokens = useThemeTokens();
  const { colors, radius } = tokens;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center md:items-center">
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
        role="presentation"
      />
      
      <div
        className="relative w-full max-w-md rounded-t-2xl md:rounded-2xl"
        style={{
          background: colors.background,
          color: colors.textPrimary,
          maxHeight: "90vh",
          ...(typeof radius?.card === "number" ? { borderRadius: radius.card } : {}),
        }}
      >
        {/* Header */}
        <div className="sticky top-0 z-10 flex items-center justify-between border-b px-5 py-4" 
             style={{ borderColor: `${colors.textSecondary}30` }}>
          <h2 className="text-lg font-semibold">{title}</h2>
          <button
            type="button"
            onClick={onClose}
            className="flex size-8 items-center justify-center rounded-full"
            style={{ background: colors.surfaceContainer }}
          >
            <X className="size-4" />
          </button>
        </div>
        
        {/* Content */}
        <div className="max-h-[calc(90vh-80px)] overflow-y-auto p-5">
          {children}
        </div>
      </div>
    </div>
  );
}
