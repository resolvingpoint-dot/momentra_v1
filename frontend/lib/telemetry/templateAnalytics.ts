/** Setup funnel telemetry spans — consumed later for completion / drop-off metrics. */

import { endSpan, startSpan } from "@/lib/telemetry/performanceTelemetry";

export type TemplateCode =
  | "life_operations"
  | "future_building"
  | "lifestyle"
  | "relationships"
  | "emotional_security";

type SetupSession = {
  templateCode: TemplateCode;
  momentId: string;
  spanId: string;
  currentStep: string | null;
  completedSteps: string[];
  startedAt: number;
};

const sessions = new Map<string, SetupSession>();

function sessionKey(templateCode: TemplateCode, momentId: string): string {
  return `${templateCode}:${momentId}`;
}

export function startSetupSession(
  templateCode: TemplateCode,
  momentId: string,
  metadata?: Record<string, unknown>,
): void {
  const key = sessionKey(templateCode, momentId);
  const existing = sessions.get(key);
  if (existing) endSpan(existing.spanId);

  const spanId = startSpan("bootstrap.load", {
    kind: "setup.session",
    template: templateCode,
    momentId,
    ...metadata,
  });
  sessions.set(key, {
    templateCode,
    momentId,
    spanId,
    currentStep: null,
    completedSteps: [],
    startedAt: Date.now(),
  });
}

export function recordSetupStepCompleted(
  templateCode: TemplateCode,
  momentId: string,
  stepId: string,
): void {
  const session = sessions.get(sessionKey(templateCode, momentId));
  if (!session) return;
  session.completedSteps.push(stepId);
  session.currentStep = stepId;
  if (process.env.NODE_ENV === "development") {
    console.debug("[TemplateAnalytics] step_completed", {
      template: templateCode,
      stepId,
      completedCount: session.completedSteps.length,
    });
  }
}

export function recordSetupAbandoned(
  templateCode: TemplateCode,
  momentId: string,
  atStep: string,
): void {
  const key = sessionKey(templateCode, momentId);
  const session = sessions.get(key);
  if (!session) return;
  endSpan(session.spanId, {
    metadata: {
      kind: "setup.abandoned",
      template: templateCode,
      momentId,
      abandonedAtStep: atStep,
      completedSteps: session.completedSteps,
      durationMs: Date.now() - session.startedAt,
    },
  });
  sessions.delete(key);
}

export function completeSetupSession(
  templateCode: TemplateCode,
  momentId: string,
  totalSteps: number,
): void {
  const key = sessionKey(templateCode, momentId);
  const session = sessions.get(key);
  if (!session) return;
  const completionPct =
    totalSteps > 0 ? Math.round((session.completedSteps.length / totalSteps) * 100) : 100;
  endSpan(session.spanId, {
    metadata: {
      kind: "setup.completed",
      template: templateCode,
      momentId,
      completionPct,
      completedSteps: session.completedSteps,
      durationMs: Date.now() - session.startedAt,
    },
  });
  sessions.delete(key);
}

export function getSetupSession(
  templateCode: TemplateCode,
  momentId: string,
): SetupSession | undefined {
  return sessions.get(sessionKey(templateCode, momentId));
}
