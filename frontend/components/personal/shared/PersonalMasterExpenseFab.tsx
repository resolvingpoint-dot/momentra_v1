"use client";

import { Plus } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { MASTER_EXPENSE_FAB_CLEARANCE_PX } from "@/lib/master_expense/defaultOptions";

type PersonalMasterExpenseFabProps = {
  onOpen: () => void;
};

export function PersonalMasterExpenseFab({ onOpen }: PersonalMasterExpenseFabProps) {
  const tokens = useThemeTokens();
  const { colors, gradients, shadows, spacing } = tokens;

  return (
    <button
      type="button"
      onClick={onOpen}
      className="fixed right-5 z-40 flex size-14 items-center justify-center rounded-full transition-transform duration-200 active:scale-95 hover:scale-105"
      style={{
        bottom: spacing.bottomNavHeight + MASTER_EXPENSE_FAB_CLEARANCE_PX,
        background: `linear-gradient(135deg, ${gradients.heroStart}, ${gradients.heroEnd})`,
        color: colors.onPrimary,
        boxShadow: `0 ${shadows.fabOffsetY}px ${shadows.fabRadius}px ${shadows.fabColor}`,
      }}
      aria-label="Master expense"
    >
      <Plus size={24} strokeWidth={2.5} />
    </button>
  );
}
