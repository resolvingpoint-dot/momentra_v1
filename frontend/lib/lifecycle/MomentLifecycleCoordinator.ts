/**
 * Cross-context moment lifecycle coordinator (Web).
 *
 * UI must call this — never pick Personal/Group/Business repositories ad hoc
 * for pause / resume / complete / archive.
 */
import { ApiError } from "@/lib/api/client";
import { PersonalRepository } from "@/repositories/PersonalRepository";
import { GroupRepository } from "@/repositories/GroupRepository";
import { BusinessRepository } from "@/repositories/BusinessRepository";
import { notifyMomentMutation } from "@/stores/bootstrapStore";

export type LifecycleContextType = "PERSONAL" | "GROUP" | "BUSINESS";
export type LifecycleAction = "pause" | "resume" | "complete" | "archive";

export type LifecycleInventoryItem = {
  momentId: string;
  momentTypeCode: string;
  status: string;
};

export type LifecycleResponse = {
  moment_id: string;
  context_type?: string;
  moment_type_code?: string;
  previous_status?: string;
  status: string;
  updated_at?: string | null;
  module_state?: string | null;
  replacement_moment_id?: string | null;
  replacement_moment_type_code?: string | null;
};

export type LifecycleErrorCode =
  | "permission_denied"
  | "moment_not_owned"
  | "membership_missing"
  | "context_mismatch"
  | "not_found"
  | "lifecycle_transition_invalid"
  | "validation_error"
  | "network"
  | "unknown";

export class MomentLifecycleError extends Error {
  readonly httpStatus: number;
  readonly errorCode: LifecycleErrorCode;
  readonly userMessage: string;

  constructor(httpStatus: number, errorCode: LifecycleErrorCode, userMessage: string, cause?: unknown) {
    super(userMessage);
    this.name = "MomentLifecycleError";
    this.httpStatus = httpStatus;
    this.errorCode = errorCode;
    this.userMessage = userMessage;
    if (cause !== undefined) {
      (this as Error & { cause?: unknown }).cause = cause;
    }
  }
}

export type MomentLifecycleRequest = {
  contextType: LifecycleContextType;
  momentId: string;
  momentTypeCode: string;
  action: LifecycleAction;
  previousStatus: string;
  /** Current inventory used for optimistic replacement. */
  inventory: LifecycleInventoryItem[];
  selectedMomentId: string | null;
  /** When true (default), invalidate app bootstrap once after success. */
  refreshBootstrap?: boolean;
};

export type MomentLifecycleResult = {
  response: LifecycleResponse;
  replacementMomentId: string | null;
  replacementMomentTypeCode: string | null;
  optimisticStatus: string;
  rollback: boolean;
  bootstrapRefreshCount: number;
  durationMs: number;
};

const REPLACEMENT_RANK: Record<string, number> = {
  ACTIVE: 0,
  PAUSED: 1,
  COMPLETED: 2,
  DRAFT: 3,
  SETUP: 3,
};

function norm(s: string | null | undefined): string {
  return (s || "").trim().toUpperCase();
}

export function pickReplacementLocally(
  inventory: LifecycleInventoryItem[],
  opts: {
    excludeId?: string | null;
    preferredId?: string | null;
    backendReplacementId?: string | null;
    backendReplacementType?: string | null;
  } = {},
): { momentId: string | null; momentTypeCode: string | null } {
  if (opts.backendReplacementId) {
    const hit = inventory.find(
      (m) => m.momentId === opts.backendReplacementId && norm(m.status) !== "ARCHIVED",
    );
    if (hit) {
      return {
        momentId: hit.momentId,
        momentTypeCode: hit.momentTypeCode || opts.backendReplacementType || null,
      };
    }
    return {
      momentId: opts.backendReplacementId,
      momentTypeCode: opts.backendReplacementType || null,
    };
  }

  const candidates = inventory.filter((m) => {
    if (opts.excludeId && m.momentId === opts.excludeId) return false;
    return norm(m.status) !== "ARCHIVED";
  });

  if (opts.preferredId) {
    const pref = candidates.find((m) => m.momentId === opts.preferredId);
    if (pref) return { momentId: pref.momentId, momentTypeCode: pref.momentTypeCode };
  }

  const sorted = [...candidates].sort((a, b) => {
    const ra = REPLACEMENT_RANK[norm(a.status)] ?? 99;
    const rb = REPLACEMENT_RANK[norm(b.status)] ?? 99;
    return ra - rb;
  });
  const best = sorted[0];
  return best
    ? { momentId: best.momentId, momentTypeCode: best.momentTypeCode }
    : { momentId: null, momentTypeCode: null };
}

function mapUserMessage(httpStatus: number, code: LifecycleErrorCode): string {
  if (httpStatus === 403 || code === "permission_denied" || code === "moment_not_owned") {
    return "You don’t have permission to change this moment.";
  }
  if (httpStatus === 404 || code === "not_found") {
    return "This moment no longer exists.";
  }
  if (httpStatus === 409 || code === "lifecycle_transition_invalid") {
    return "This moment has already changed state. Refreshing…";
  }
  if (httpStatus === 422 || code === "validation_error") {
    return "Some lifecycle details are invalid.";
  }
  if (code === "network") {
    return "We couldn’t update this moment. Your current view has been restored.";
  }
  return "We couldn’t update this moment. Your current view has been restored.";
}

function parseLifecycleError(err: unknown): MomentLifecycleError {
  if (err instanceof MomentLifecycleError) return err;
  if (err instanceof ApiError) {
    const rawCode = (err.code || "").toLowerCase();
    let code: LifecycleErrorCode = "unknown";
    if (err.status === 403) code = "permission_denied";
    else if (err.status === 404) code = "not_found";
    else if (err.status === 409 || rawCode.includes("lifecycle") || rawCode.includes("transition")) {
      code = "lifecycle_transition_invalid";
    } else if (err.status === 422) code = "validation_error";
    else if (!err.status) code = "network";
    return new MomentLifecycleError(err.status || 0, code, mapUserMessage(err.status || 0, code), err);
  }
  return new MomentLifecycleError(0, "network", mapUserMessage(0, "network"), err);
}

function targetStatus(action: LifecycleAction): string {
  switch (action) {
    case "pause":
      return "PAUSED";
    case "resume":
      return "ACTIVE";
    case "complete":
      return "COMPLETED";
    case "archive":
      return "ARCHIVED";
  }
}

async function dispatchLifecycle(
  contextType: LifecycleContextType,
  momentId: string,
  momentTypeCode: string,
  action: LifecycleAction,
): Promise<LifecycleResponse> {
  if (contextType === "PERSONAL") {
    if (action === "pause") {
      // patchMoment already invalidates bootstrap once
      return (await PersonalRepository.patchMoment(momentId, { status: "PAUSED" })) as LifecycleResponse;
    }
    if (action === "resume") {
      return (await PersonalRepository.patchMoment(momentId, { status: "ACTIVE" })) as LifecycleResponse;
    }
    if (action === "complete") {
      return (await PersonalRepository.completeTemplateMoment(
        momentTypeCode as import("@/lib/personal/personalMomentSession").PersonalMomentTypeCode,
        momentId,
      )) as LifecycleResponse;
    }
    return (await PersonalRepository.archiveTemplateMoment(
      momentTypeCode as import("@/lib/personal/personalMomentSession").PersonalMomentTypeCode,
      momentId,
    )) as LifecycleResponse;
  }

  if (contextType === "GROUP") {
    if (action === "pause") {
      return (await GroupRepository.patchMoment(momentId, { status: "PAUSED" })) as LifecycleResponse;
    }
    if (action === "resume") {
      return (await GroupRepository.patchMoment(momentId, { status: "ACTIVE" })) as LifecycleResponse;
    }
    if (action === "complete") {
      return (await GroupRepository.completeMoment(momentId)) as LifecycleResponse;
    }
    return (await GroupRepository.archiveMoment(momentId)) as LifecycleResponse;
  }

  // BUSINESS
  if (action === "pause") {
    return (await BusinessRepository.patchMoment(momentId, { status: "PAUSED" })) as LifecycleResponse;
  }
  if (action === "resume") {
    return (await BusinessRepository.patchMoment(momentId, { status: "ACTIVE" })) as LifecycleResponse;
  }
  if (action === "complete") {
    return (await BusinessRepository.completeMoment(momentId)) as LifecycleResponse;
  }
  return (await BusinessRepository.archiveMoment(momentId)) as LifecycleResponse;
}

function emitTelemetry(payload: Record<string, unknown>) {
  if (typeof console !== "undefined") {
    console.info("event=MomentLifecycle", payload);
  }
}

/**
 * Execute a lifecycle action with optimistic inventory math + one bootstrap refresh.
 *
 * Callers should:
 * 1. Apply optimistic inventory/selection from the returned replacement before await settles
 *    via `onOptimistic` if provided.
 * 2. On success, reconcile with `result.response` and refresh session surfaces once.
 * 3. On failure, rollback using `onRollback`.
 */
export async function runMomentLifecycle(
  req: MomentLifecycleRequest,
  hooks?: {
    onOptimistic?: (next: {
      optimisticStatus: string;
      replacementMomentId: string | null;
      replacementMomentTypeCode: string | null;
      inventory: LifecycleInventoryItem[];
    }) => void;
    onRollback?: () => void;
  },
): Promise<MomentLifecycleResult> {
  const t0 = performance.now();
  const optimisticStatus = targetStatus(req.action);
  const excludeOnSuccess = req.action === "archive" || req.action === "complete";

  const optimisticInventory = req.inventory.map((m) =>
    m.momentId === req.momentId ? { ...m, status: optimisticStatus } : m,
  ).filter((m) => !(req.action === "archive" && m.momentId === req.momentId));

  const localRepl = pickReplacementLocally(optimisticInventory, {
    excludeId: excludeOnSuccess ? req.momentId : null,
    preferredId:
      req.action === "resume"
        ? req.momentId
        : excludeOnSuccess
          ? null
          : req.selectedMomentId,
  });

  hooks?.onOptimistic?.({
    optimisticStatus,
    replacementMomentId: localRepl.momentId,
    replacementMomentTypeCode: localRepl.momentTypeCode,
    inventory: optimisticInventory,
  });

  let bootstrapRefreshCount = 0;
  try {
    const response = await dispatchLifecycle(
      req.contextType,
      req.momentId,
      req.momentTypeCode,
      req.action,
    );

    if (req.refreshBootstrap !== false) {
      // Personal pause/resume already soft-refresh inside PersonalRepository.patchMoment.
      const alreadyRefreshed =
        req.contextType === "PERSONAL" && (req.action === "pause" || req.action === "resume");
      if (!alreadyRefreshed) {
        notifyMomentMutation(req.contextType);
        bootstrapRefreshCount = 1;
      } else {
        bootstrapRefreshCount = 1; // counted as the repo's single refresh
      }
    }

    const repl = pickReplacementLocally(optimisticInventory, {
      excludeId: excludeOnSuccess ? req.momentId : null,
      preferredId: req.action === "resume" ? req.momentId : null,
      backendReplacementId: response.replacement_moment_id,
      backendReplacementType: response.replacement_moment_type_code,
    });

    const durationMs = Math.round(performance.now() - t0);
    emitTelemetry({
      platform: "web",
      contextType: req.contextType,
      momentId: req.momentId,
      momentType: req.momentTypeCode,
      action: req.action,
      previousStatus: req.previousStatus,
      optimisticStatus,
      finalStatus: response.status || optimisticStatus,
      replacementMomentId: repl.momentId,
      durationMs,
      success: true,
      httpStatus: 200,
      errorCode: null,
      rollback: false,
      bootstrapRefreshCount,
    });

    return {
      response,
      replacementMomentId: repl.momentId,
      replacementMomentTypeCode: repl.momentTypeCode,
      optimisticStatus,
      rollback: false,
      bootstrapRefreshCount,
      durationMs,
    };
  } catch (err) {
    hooks?.onRollback?.();
    const mapped = parseLifecycleError(err);
    const durationMs = Math.round(performance.now() - t0);
    emitTelemetry({
      platform: "web",
      contextType: req.contextType,
      momentId: req.momentId,
      momentType: req.momentTypeCode,
      action: req.action,
      previousStatus: req.previousStatus,
      optimisticStatus,
      finalStatus: req.previousStatus,
      replacementMomentId: null,
      durationMs,
      success: false,
      httpStatus: mapped.httpStatus,
      errorCode: mapped.errorCode,
      rollback: true,
      bootstrapRefreshCount: 0,
    });
    throw mapped;
  }
}

/** Explicit context → repository dispatch table (for tests / audits). */
export const LIFECYCLE_DISPATCH = {
  PERSONAL: "PersonalRepository",
  GROUP: "GroupRepository",
  BUSINESS: "BusinessRepository",
} as const;
