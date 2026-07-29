import type {
  PersonalLifeOpsReturnBehaviors,
  PersonalLifestyleMemoryMetrics,
  PersonalLifestyleRoiAnalysis,
} from "@/lib/api/personal";

type TemplateMemoryMetrics = PersonalLifestyleMemoryMetrics & {
  highest_return_behaviors?: PersonalLifeOpsReturnBehaviors | null;
  roi_analysis?: PersonalLifestyleRoiAnalysis | null;
};

export function resolvedMemoryRoiAnalysis(
  metrics: TemplateMemoryMetrics | null | undefined,
): PersonalLifestyleRoiAnalysis | null {
  if (!metrics) return null;
  if (metrics.roi_analysis) return metrics.roi_analysis;
  const legacy = metrics.highest_return_behaviors;
  if (!legacy) return null;
  return {
    title: legacy.title,
    roi_label: legacy.roi_label,
    bars: legacy.bars,
  };
}

export function resolvedMemoryReturnBehaviors(
  metrics: TemplateMemoryMetrics | null | undefined,
): PersonalLifeOpsReturnBehaviors | null {
  const roi = resolvedMemoryRoiAnalysis(metrics);
  if (!roi) return null;
  return {
    title: roi.title,
    roi_label: roi.roi_label,
    bars: roi.bars,
  };
}
