import { lifeOpsPulseCopy } from "@/lib/personal/life_operations/pulse/lifeOpsPulseCopy";

export const AXIS_DONUT_MIN_WEIGHT = 1;

export type AxisId = "pressure" | "recovery" | "discipline" | "attention";

export type AxisScores = {
  pressure: number;
  recovery: number;
  discipline: number;
  attention: number;
};

export type AxisDonutSlice = {
  id: AxisId;
  label: string;
  score: number;
  value: number;
};

export function axisDonutWeight(score: number): number {
  return Math.max(score, AXIS_DONUT_MIN_WEIGHT);
}

export function axisDonutSlices(scores: AxisScores): AxisDonutSlice[] {
  return [
    { id: "pressure", label: lifeOpsPulseCopy.axisPressure, score: scores.pressure, value: axisDonutWeight(scores.pressure) },
    { id: "recovery", label: lifeOpsPulseCopy.axisRecovery, score: scores.recovery, value: axisDonutWeight(scores.recovery) },
    { id: "discipline", label: lifeOpsPulseCopy.axisDiscipline, score: scores.discipline, value: axisDonutWeight(scores.discipline) },
    { id: "attention", label: lifeOpsPulseCopy.axisAttention, score: scores.attention, value: axisDonutWeight(scores.attention) },
  ];
}

/** Distinct Personal axis hues — avoid primary vs secondary lavender collision. */
export const AXIS_DONUT_COLORS = {
  pressure: "#ffb4ab",
  recovery: "#c9bfff",
  discipline: "#6c4ef2",
  attention: "#4cd6ff",
} as const;

export function axisColorForId(
  id: AxisId,
  colors: { error: string; brandPrimary: string; primaryContainer: string; brandTertiary: string },
): string {
  switch (id) {
    case "pressure":
      return colors.error;
    case "recovery":
      return colors.brandPrimary;
    case "discipline":
      return colors.primaryContainer;
    case "attention":
      return colors.brandTertiary;
  }
}
