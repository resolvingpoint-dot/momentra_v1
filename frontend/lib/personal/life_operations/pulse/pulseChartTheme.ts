/** Shared react-gifted-charts styling for Life Ops Pulse — no legends, tooltips, or animations. */

export const PULSE_CHART_ANIMATION = { isAnimated: true } as const;

export const PULSE_PIE_PROPS = {
  showText: false,
  showTooltip: false,
  focusOnPress: false,
  toggleFocusOnPress: false,
  ...PULSE_CHART_ANIMATION,
} as const;

export const PULSE_LINE_PROPS = {
  hideDataPoints: true,
  hideDataPoints1: true,
  hideDataPoints2: true,
  hideAxesAndRules: true,
  hideRules: true,
  hideYAxisText: true,
  xAxisThickness: 0,
  yAxisThickness: 0,
  rulesThickness: 0,
  maxValue: 100,
  ...PULSE_CHART_ANIMATION,
} as const;

export const PULSE_BAR_PROPS = {
  horizontal: true,
  hideAxesAndRules: true,
  hideRules: true,
  hideYAxisText: true,
  xAxisThickness: 0,
  yAxisThickness: 0,
  maxValue: 100,
  noOfSections: 1,
  barBorderRadius: 4,
  initialSpacing: 0,
  endSpacing: 0,
  ...PULSE_CHART_ANIMATION,
} as const;

export const DONUT_SIZE = 128;
export const DONUT_RADIUS = 56;
export const DONUT_INNER_RADIUS = 44;

export const HERO_DONUT_SIZE = 160;
export const HERO_DONUT_RADIUS = 80;
/** 74% of outer radius — matches Android/iOS hero donut inner ratio. */
export const HERO_DONUT_INNER_RADIUS = 59;
/** Hero glass card surface — masks gifted-charts pie center to form the donut hole. */
export const HERO_DONUT_INNER_CIRCLE_COLOR = "#1a1728";

export const HERO_PIE_PROPS = {
  showText: false,
  showTooltip: false,
  focusOnPress: true,
  toggleFocusOnPress: true,
  ...PULSE_CHART_ANIMATION,
  paddingAngle: 2,
} as const;

export const ARC_GAUGE_TRACK = "#2b2933";

/** Memory Emotional DNA donut — matches mock w-20 h-20. */
export const MEMORY_DONUT_SIZE = 80;
export const MEMORY_DONUT_RADIUS = 36;
export const MEMORY_DONUT_INNER_RADIUS = 26;
