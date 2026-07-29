/** Life Operations quick-add form state and API payload builders. */
import { composeOccurredAt, nowISOTime, todayISODate } from "@/lib/quick_add/dateTimeDefaults";

export type RuntimeSignalKey = "pressure" | "recovery" | "focus" | "momentum";
export type RuntimeSignalDirection = "DOWN" | "STABLE" | "UP";

export type LifeOpsQuickAddFormState = {
  transactionType: string;
  expenseTitle: string;
  amountMinor: number;
  currencyCode: string;
  accountId: string;
  categoryCode: string;
  subcategoryCode: string;
  occurredDate: string;
  occurredTime: string;
  pressureImpact: string;
  expenseNotes: string;
  showMoreDetails: boolean;
  commitmentName: string;
  commitmentType: string;
  focusArea: string;
  commitmentStatus: string;
  intensity: string;
  expectedAmountMinor: number;
  showExpectedAmount: boolean;
  commitmentNotes: string;
  showCommitmentNotes: boolean;
  feelingState: string;
  reflectionNote: string;
  reflectionTags: string[];
  showMoodNote: boolean;
  recoveryType: string;
  recoveryDuration: string;
  recoveryEnergyImpact: string;
  recoveryNotes: string;
  showRecoveryNotes: boolean;
  rhythmActions: Set<string>;
  runtimeMode: string;
  runtimeSignals: Partial<Record<RuntimeSignalKey, RuntimeSignalDirection>>;
};

export function defaultLifeOpsFormState(defaultCurrencyCode = "INR"): LifeOpsQuickAddFormState {
  return {
    transactionType: "EXPENSE",
    expenseTitle: "",
    amountMinor: 0,
    currencyCode: defaultCurrencyCode,
    accountId: "",
    categoryCode: "",
    subcategoryCode: "",
    occurredDate: todayISODate(),
    occurredTime: nowISOTime(),
    pressureImpact: "",
    expenseNotes: "",
    showMoreDetails: false,
    commitmentName: "",
    commitmentType: "TASK",
    focusArea: "",
    commitmentStatus: "IN_PROGRESS",
    intensity: "MODERATE",
    expectedAmountMinor: 0,
    showExpectedAmount: false,
    commitmentNotes: "",
    showCommitmentNotes: false,
    feelingState: "OKAY",
    reflectionNote: "",
    reflectionTags: [],
    showMoodNote: false,
    recoveryType: "",
    recoveryDuration: "",
    recoveryEnergyImpact: "MODERATE",
    recoveryNotes: "",
    showRecoveryNotes: false,
    rhythmActions: new Set(),
    runtimeMode: "FLOW_MODE",
    runtimeSignals: {
      pressure: "STABLE",
      recovery: "STABLE",
      focus: "STABLE",
      momentum: "STABLE",
    },
  };
}

function basePayload(momentId: string, eventType: string, eventTitle: string) {
  return { moment_id: momentId, event_type: eventType, event_title: eventTitle };
}

export function buildExpensePayload(
  momentId: string,
  eventTitle: string,
  state: LifeOpsQuickAddFormState,
) {
  const stamp = composeOccurredAt(state.occurredDate, state.occurredTime);
  const title = state.expenseTitle.trim() || eventTitle || "Money entry";
  return {
    ...basePayload(momentId, "EXPENSE", title),
    expense: {
      transaction_type: state.transactionType,
      title: state.expenseTitle.trim() || undefined,
      amount_minor: state.amountMinor,
      currency_code: state.currencyCode,
      account_id: state.accountId,
      category_code: state.categoryCode || undefined,
      subcategory_code: state.subcategoryCode || null,
      pressure_impact: state.pressureImpact || undefined,
      transaction_date: stamp || undefined,
      notes: state.expenseNotes.trim() || undefined,
    },
    occurred_at: stamp || undefined,
  };
}

export function buildCommitmentPayload(
  momentId: string,
  eventTitle: string,
  state: LifeOpsQuickAddFormState,
) {
  const title = state.commitmentName.trim() || eventTitle;
  const commitment: Record<string, unknown> = {
    commitment_name: state.commitmentName.trim(),
    commitment_type: state.commitmentType,
    focus_area: state.focusArea || undefined,
    commitment_status: state.commitmentStatus,
    intensity: state.intensity || "MODERATE",
  };
  if (state.showExpectedAmount && state.expectedAmountMinor > 0) {
    commitment.expected_amount = state.expectedAmountMinor;
  }
  if (state.showCommitmentNotes && state.commitmentNotes.trim()) {
    commitment.notes = state.commitmentNotes.trim();
  }
  return {
    ...basePayload(momentId, "COMMITMENT", title),
    commitment,
  };
}

export function buildReflectionPayload(
  momentId: string,
  eventTitle: string,
  state: LifeOpsQuickAddFormState,
) {
  const tags = state.reflectionTags.filter(Boolean);
  return {
    ...basePayload(momentId, "REFLECTION", eventTitle),
    reflection: {
      feeling_state: state.feelingState,
      reflection_note: state.reflectionNote.trim() || undefined,
      reflection_tag: tags.length === 1 ? tags[0] : tags.length > 1 ? tags : undefined,
    },
  };
}

export function buildRecoveryPayload(
  momentId: string,
  eventTitle: string,
  state: LifeOpsQuickAddFormState,
) {
  return {
    ...basePayload(momentId, "RECOVERY", eventTitle),
    recovery: {
      recovery_type: state.recoveryType,
      recovery_intensity: state.recoveryEnergyImpact,
      duration_minutes: Number(state.recoveryDuration) || undefined,
      notes:
        state.showRecoveryNotes && state.recoveryNotes.trim()
          ? state.recoveryNotes.trim()
          : undefined,
    },
  };
}

export function buildRhythmPayload(
  momentId: string,
  eventTitle: string,
  state: LifeOpsQuickAddFormState,
) {
  const actions = Array.from(state.rhythmActions).sort();
  const signals = state.runtimeSignals;
  return {
    ...basePayload(momentId, "RHYTHM", eventTitle),
    rhythm: {
      rhythm_actions: actions,
      rhythm_action: actions[0],
      new_runtime_mode: state.runtimeMode,
      new_runtime_priority: state.runtimeMode === "SURVIVAL_MODE" ? "HIGH" : "MEDIUM",
      runtime_signals: {
        pressure: signals.pressure ?? "STABLE",
        recovery: signals.recovery ?? "STABLE",
        focus: signals.focus ?? "STABLE",
        momentum: signals.momentum ?? "STABLE",
      },
    },
  };
}

export function buildLifeOpsQuickAddPayload(
  eventType: string,
  momentId: string,
  eventTitle: string,
  state: LifeOpsQuickAddFormState,
): Record<string, unknown> {
  switch (eventType) {
    case "EXPENSE":
      return buildExpensePayload(momentId, eventTitle, state);
    case "COMMITMENT":
      return buildCommitmentPayload(momentId, eventTitle, state);
    case "REFLECTION":
      return buildReflectionPayload(momentId, eventTitle, state);
    case "RECOVERY":
      return buildRecoveryPayload(momentId, eventTitle, state);
    case "RHYTHM":
      return buildRhythmPayload(momentId, eventTitle, state);
    default:
      return basePayload(momentId, eventType, eventTitle);
  }
}

export function canSubmitLifeOpsTab(tab: string, state: LifeOpsQuickAddFormState): boolean {
  switch (tab) {
    case "EXPENSE":
      return (
        state.amountMinor > 0 &&
        Boolean(state.accountId) &&
        Boolean(state.categoryCode) &&
        Number.isFinite(state.amountMinor)
      );
    case "COMMITMENT":
      if (!state.commitmentName.trim()) return false;
      if (state.showExpectedAmount && state.expectedAmountMinor < 0) return false;
      if (state.showExpectedAmount && !Number.isFinite(state.expectedAmountMinor)) return false;
      return true;
    case "REFLECTION":
      return Boolean(state.feelingState);
    case "RECOVERY":
      return Boolean(state.recoveryType);
    case "RHYTHM":
      return (
        Boolean(state.runtimeMode) ||
        state.rhythmActions.size > 0 ||
        Object.values(state.runtimeSignals).some(Boolean)
      );
    default:
      return false;
  }
}

/** True when the user has entered meaningful data beyond defaults for the active tab. */
export function isLifeOpsTabDirty(tab: string, state: LifeOpsQuickAddFormState): boolean {
  switch (tab) {
    case "EXPENSE":
      return (
        state.amountMinor > 0 ||
        Boolean(state.expenseTitle.trim()) ||
        Boolean(state.pressureImpact) ||
        Boolean(state.expenseNotes.trim()) ||
        state.transactionType !== "EXPENSE"
      );
    case "COMMITMENT":
      return Boolean(state.commitmentName.trim()) || state.showExpectedAmount || state.showCommitmentNotes;
    case "REFLECTION":
      return (
        state.feelingState !== "OKAY" ||
        state.reflectionTags.length > 0 ||
        Boolean(state.reflectionNote.trim())
      );
    case "RECOVERY":
      return Boolean(state.recoveryType) || Boolean(state.recoveryDuration) || state.showRecoveryNotes;
    case "RHYTHM":
      return (
        state.rhythmActions.size > 0 ||
        state.runtimeMode !== "FLOW_MODE" ||
        Object.values(state.runtimeSignals).some((v) => v && v !== "STABLE")
      );
    default:
      return false;
  }
}
