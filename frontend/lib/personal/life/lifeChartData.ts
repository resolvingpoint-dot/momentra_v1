import type { PersonalLifeTrendPoint } from "@/lib/api/personal";

export function alignEmotionalSeries(series: PersonalLifeTrendPoint[]) {
  const connection = series.map((p) => p.connection);
  const joy = series.map((p) => p.joy);
  const stress = series.map((p) => p.stress);
  const fulfillment = series.map((p) => p.fulfillment);
  const count = series.length;
  return { connection, joy, stress, fulfillment, count };
}

export function toLineData(values: number[]): { value: number }[] {
  return values.map((value) => ({ value }));
}
