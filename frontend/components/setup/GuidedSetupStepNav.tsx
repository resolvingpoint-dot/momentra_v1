"use client";

import { Check, ChevronRight } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import {
  stepVisualState,
  type GuidedSetupStep,
  type GuidedSetupStepVisualState,
} from "@/components/setup/guidedSetupTypes";

type Props = {
  steps: GuidedSetupStep[];
  currentStep: number;
  orientation?: "horizontal" | "vertical";
  warningSteps?: number[];
  blockedSteps?: number[];
};

function chipStyle(
  state: GuidedSetupStepVisualState,
  colors: ReturnType<typeof useThemeTokens>["colors"],
) {
  switch (state) {
    case "current":
      return {
        background: colors.primaryContainer,
        color: colors.brandOnPrimary,
        opacity: 1,
      };
    case "complete":
      return {
        background: `color-mix(in srgb, ${colors.primary} 18%, transparent)`,
        color: colors.textPrimary,
        opacity: 1,
      };
    case "warning":
      return {
        background: "rgba(245,158,11,0.18)",
        color: colors.textPrimary,
        opacity: 1,
      };
    case "blocked":
      return {
        background: "rgba(239,68,68,0.14)",
        color: colors.error,
        opacity: 1,
      };
    default:
      return {
        background: colors.surfaceContainer,
        color: colors.textPrimary,
        opacity: 0.55,
      };
  }
}

export function GuidedSetupStepNav({
  steps,
  currentStep,
  orientation = "horizontal",
  warningSteps,
  blockedSteps,
}: Props) {
  const { colors } = useThemeTokens();
  const vertical = orientation === "vertical";

  return (
    <nav
      className={
        vertical
          ? "hidden shrink-0 lg:block"
          : "shrink-0 overflow-x-auto border-b px-4 py-1.5 lg:hidden"
      }
      style={
        vertical
          ? undefined
          : { borderColor: `color-mix(in srgb, ${colors.border} 30%, transparent)` }
      }
      aria-label="Setup steps"
    >
      <ol className={vertical ? "space-y-2" : "flex min-w-max items-center gap-1"}>
        {steps.map((step, index) => {
          const state = stepVisualState(index, currentStep, warningSteps, blockedSteps);
          const style = chipStyle(state, colors);
          return (
            <li key={step.id} className={vertical ? "w-full" : "flex items-center gap-1"}>
              {!vertical && index > 0 ? (
                <ChevronRight className="size-3.5 opacity-40" aria-hidden />
              ) : null}
              <span
                className={
                  vertical
                    ? "flex min-h-10 w-full items-center gap-2 rounded-lg px-2.5 py-1.5 text-sm font-semibold"
                    : "inline-flex min-h-8 items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-semibold"
                }
                style={style}
                aria-current={state === "current" ? "step" : undefined}
              >
                {state === "complete" ? (
                  <Check className="size-3 shrink-0" aria-hidden />
                ) : state === "current" ? (
                  <span
                    className="size-1.5 shrink-0 rounded-full"
                    style={{ background: "currentColor" }}
                    aria-hidden
                  />
                ) : (
                  <span className="tabular-nums opacity-70" aria-hidden>
                    {index + 1}
                  </span>
                )}
                <span className="truncate">{step.shortTitle}</span>
                {step.optional ? (
                  <span className="text-[10px] font-medium uppercase opacity-50">Optional</span>
                ) : null}
              </span>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
