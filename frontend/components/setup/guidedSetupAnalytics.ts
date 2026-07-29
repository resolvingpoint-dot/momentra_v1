/**
 * Generic guided-setup analytics — comparable across Personal, Group, and Business.
 *
 * Standard envelope fields (when present):
 *   context, template, step, saveState, action, elapsedMs
 */

export type GuidedSetupAnalyticsAction =
  | "setup_open"
  | "step_changed"
  | "autosave_started"
  | "autosave_completed"
  | "autosave_failed"
  | "review_opened"
  | "activation_started"
  | "activation_completed"
  | "activation_failed"
  | "continue"
  | "back"
  | "skip";

/** Comparable payload for dashboards across contexts. */
export type GuidedSetupAnalyticsPayload = {
  context?: string;
  template?: string;
  step?: string;
  stepIndex?: number;
  saveState?: string;
  action: GuidedSetupAnalyticsAction;
  elapsedMs?: number;
  momentId?: string;
  momentTypeCode?: string;
  error?: string;
};

export type GuidedSetupAnalyticsEvent =
  | {
      type: "setup_open";
      contextType?: string;
      templateId?: string;
      momentTypeCode?: string;
      momentId?: string;
      elapsedMs?: number;
    }
  | {
      type: "step_changed";
      stepId: string;
      stepIndex: number;
      templateId?: string;
      contextType?: string;
      saveState?: string;
      elapsedMs?: number;
    }
  | {
      type: "autosave_started";
      templateId?: string;
      contextType?: string;
      stepId?: string;
      saveState?: string;
    }
  | {
      type: "autosave_completed";
      templateId?: string;
      contextType?: string;
      stepId?: string;
      elapsedMs?: number;
    }
  | {
      type: "autosave_failed";
      templateId?: string;
      contextType?: string;
      stepId?: string;
      error?: string;
    }
  | {
      type: "review_opened";
      templateId?: string;
      contextType?: string;
      elapsedMs?: number;
    }
  | {
      type: "activation_started";
      templateId?: string;
      momentId?: string;
      contextType?: string;
    }
  | {
      type: "activation_completed";
      templateId?: string;
      momentId?: string;
      contextType?: string;
      elapsedMs?: number;
    }
  | {
      type: "activation_failed";
      templateId?: string;
      momentId?: string;
      contextType?: string;
      error?: string;
    };

export type GuidedSetupAnalyticsHandler = (
  event: GuidedSetupAnalyticsEvent,
) => void;

/** Normalize any guided-setup event into the standard comparable payload. */
export function toGuidedSetupAnalyticsPayload(
  event: GuidedSetupAnalyticsEvent,
): GuidedSetupAnalyticsPayload {
  const payload: GuidedSetupAnalyticsPayload = {
    action: event.type,
  };
  if ("contextType" in event && event.contextType) payload.context = event.contextType;
  if ("templateId" in event && event.templateId) payload.template = event.templateId;
  if ("stepId" in event && event.stepId) payload.step = event.stepId;
  if ("stepIndex" in event && event.stepIndex != null) payload.stepIndex = event.stepIndex;
  if ("saveState" in event && event.saveState) payload.saveState = event.saveState;
  if ("elapsedMs" in event && event.elapsedMs != null) payload.elapsedMs = event.elapsedMs;
  if ("momentId" in event && event.momentId) payload.momentId = event.momentId;
  if ("momentTypeCode" in event && event.momentTypeCode) {
    payload.momentTypeCode = event.momentTypeCode;
  }
  if ("error" in event && event.error) payload.error = event.error;
  return payload;
}

function payloadToParams(payload: GuidedSetupAnalyticsPayload): Record<string, string> {
  const params: Record<string, string> = { action: payload.action };
  if (payload.context) params.context = payload.context;
  if (payload.template) params.template = payload.template;
  if (payload.step) params.step = payload.step;
  if (payload.stepIndex != null) params.step_index = String(payload.stepIndex);
  if (payload.saveState) params.save_state = payload.saveState;
  if (payload.elapsedMs != null) params.elapsed_ms = String(payload.elapsedMs);
  if (payload.momentId) params.moment_id = payload.momentId;
  if (payload.momentTypeCode) params.moment_type_code = payload.momentTypeCode;
  if (payload.error) params.error = payload.error;
  return params;
}

/** Map generic setup events to MomentraAnalytics screen/custom event names. */
export function emitGuidedSetupAnalytics(
  event: GuidedSetupAnalyticsEvent,
  log: {
    logScreen?: (name: string) => void;
    logCustomEvent?: (name: string, params?: Record<string, string>) => void;
  },
): void {
  const payload = toGuidedSetupAnalyticsPayload(event);
  const params = payloadToParams(payload);

  void log.logCustomEvent?.(event.type, params);
  // Also emit a stable funnel name for cross-context dashboards.
  void log.logCustomEvent?.("guided_setup", params);

  if (event.type === "setup_open") {
    void log.logScreen?.("setup");
  }
  if (event.type === "step_changed") {
    void log.logScreen?.(`setup_step_${event.stepId}`);
  }
  if (event.type === "review_opened") {
    void log.logScreen?.("setup_review");
  }
}
