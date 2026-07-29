"use client";

import { PersonalMasterExpenseFab } from "@/components/personal/shared/PersonalMasterExpenseFab";

type MyMoneyFloatingAddProps = {
  onOpen: () => void;
};

/** My Money FAB — opens Master Expense Orchestrator above bottom nav. */
export function MyMoneyFloatingAdd({ onOpen }: MyMoneyFloatingAddProps) {
  return <PersonalMasterExpenseFab onOpen={onOpen} />;
}
