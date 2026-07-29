/** Client-side runway estimate for setup live summary (presentation only). */

export type RunwayEstimateInput = {
  currentCashMinor: number | null | undefined;
  monthlyBurnMinor: number | null | undefined;
  estimatedMonthlyRevenueMinor?: number | null;
  collectionRatePercent?: number | null;
  revenueStatus?: string | null;
  minorUnit?: number;
};

export type RunwayEstimateResult =
  | { kind: "months"; months: number; detail: string }
  | { kind: "positive_cashflow"; detail: string }
  | { kind: "need_burn"; detail: string }
  | { kind: "incomplete"; detail: string };

function major(minor: number, minorUnit: number): number {
  return minor / 10 ** minorUnit;
}

export function estimateRunwayMonths(input: RunwayEstimateInput): RunwayEstimateResult {
  const minorUnit = input.minorUnit ?? 2;
  const cash = input.currentCashMinor;
  const burn = input.monthlyBurnMinor;

  if (cash == null || burn == null) {
    return { kind: "incomplete", detail: "Enter cash and monthly spending to estimate runway." };
  }
  if (burn <= 0) {
    return {
      kind: "need_burn",
      detail: "Add monthly spending to estimate runway",
    };
  }

  const hasRevenue =
    input.revenueStatus &&
    input.revenueStatus !== "NO_REVENUE" &&
    (input.estimatedMonthlyRevenueMinor ?? 0) > 0;

  const revenue = hasRevenue ? (input.estimatedMonthlyRevenueMinor ?? 0) : 0;
  const rate = hasRevenue ? Math.min(100, Math.max(0, input.collectionRatePercent ?? 100)) / 100 : 0;
  const collected = revenue * rate;
  const netBurn = burn - collected;

  if (netBurn <= 0) {
    return {
      kind: "positive_cashflow",
      detail:
        "Based on the cash, monthly spending and expected collected revenue entered above.",
    };
  }

  const months = cash / netBurn;
  const rounded = Math.round(months * 10) / 10;
  const cashMajor = major(cash, minorUnit);
  const netMajor = major(netBurn, minorUnit);

  return {
    kind: "months",
    months: rounded,
    detail: `Based on approximately ${cashMajor.toLocaleString()} cash and ${netMajor.toLocaleString()} net monthly burn.`,
  };
}

export function formatRunwayEstimatePrimary(result: RunwayEstimateResult): string {
  if (result.kind === "months") return `About ${result.months} months`;
  if (result.kind === "positive_cashflow") return "Positive monthly cash flow";
  if (result.kind === "need_burn") return "—";
  return "—";
}
