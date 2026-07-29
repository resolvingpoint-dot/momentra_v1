type PieRow = { value: number; color: string; strokeColor?: string };

export function trendPointCount(
  recovery: { value: number }[],
  pressure: { value: number }[],
): number {
  return Math.max(recovery.length, pressure.length);
}

export function alignSeriesValues(
  recovery: { value: number }[],
  pressure: { value: number }[],
): { recovery: number[]; pressure: number[]; count: number } {
  const count = trendPointCount(recovery, pressure);
  const recoveryValues = recovery.map((p) => p.value);
  const pressureValues = pressure.map((p) => p.value);
  while (recoveryValues.length < count) {
    recoveryValues.push(recoveryValues[recoveryValues.length - 1] ?? 0);
  }
  while (pressureValues.length < count) {
    pressureValues.push(pressureValues[pressureValues.length - 1] ?? 0);
  }
  return { recovery: recoveryValues, pressure: pressureValues, count };
}

export function toTrendLineData(values: number[]): { value: number }[] {
  return values.map((value) => ({ value }));
}

export function driverBarWidth(impact: number): number {
  return Math.min(100, Math.abs(impact) * 8);
}

export function arcGaugePieData(percent: number, color: string, trackColor: string): PieRow[] {
  const clamped = Math.min(100, Math.max(0, percent));
  if (clamped <= 0) {
    return [{ value: 100, color: trackColor }];
  }
  if (clamped >= 100) {
    return [{ value: 100, color }];
  }
  return [
    { value: clamped, color },
    { value: 100 - clamped, color: "transparent", strokeColor: "transparent" },
  ];
}
