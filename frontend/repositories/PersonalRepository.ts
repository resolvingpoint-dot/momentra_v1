import {
  archiveTemplateMoment,
  completeTemplateMoment,
  createPersonalMoment,
  createPersonalQuickAdd,
  createMasterExpense,
  deleteTemplateActivity,
  getMasterExpenseOptions,
  getPersonalCreateOptions,
  getPersonalInventory,
  getPersonalLife,
  getPersonalMemory,
  getPersonalMomentsHome,
  getPersonalPulse,
  getPersonalQuickAddOptions,
  getPersonalSession,
  getTemplateActivity,
  getTemplateActivityDetail,
  getUnifiedPersonalActivity,
  getTemplateLife,
  getTemplateMemory,
  getTemplateMoments,
  getTemplatePulse,
  patchPersonalMoment,
  patchTemplateActivity,
  updateTemplateMoment,
  listPersonalAccounts,
  getPersonalAccount,
  createPersonalAccount,
  patchPersonalAccount,
  archivePersonalAccount,
  deletePersonalAccount,
  ApiError,
  type PersonalAccountPatchRequest,
} from "@/lib/api/client";
import {
  parsePersonalMemoryResponse,
  parsePersonalMomentsHomeResponse,
  parsePersonalPulseResponse,
  parseTemplateMemoryResponse,
  parseTemplateMomentsResponse,
  parseTemplatePulseResponse,
} from "@/lib/personal/personalApiMappers";
import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";
import type {
  TemplateActivityDetail,
  TemplateActivityItem,
  TemplateActivityListResponse,
} from "@/lib/personal/template/activity/types";
import type {
  PersonalMomentCreateRequest,
  PersonalMomentResponse,
  PersonalMomentUpdateRequest,
} from "@/lib/api/personal";
import { invalidateQuickAddOptionsCache } from "@/hooks/useQuickAddOptions";
import { invalidatePersonalLifeCache } from "@/hooks/usePersonalLife";
import { invalidatePersonalMemoryCache } from "@/hooks/usePersonalMemory";
import { invalidatePersonalPulseCache } from "@/hooks/usePersonalPulse";
import { invalidatePersonalMomentsCache } from "@/hooks/usePersonalMoments";
import {
  invalidateTemplateProjectionCaches,
} from "@/hooks/useTemplateProjection";
import { notifyMomentMutation } from "@/stores/bootstrapStore";
import {
  clearQuickAddDraft,
  createClientRequestId,
  isNetworkFailure,
  saveQuickAddDraft,
  type QuickAddDraft,
} from "@/lib/quick_add/draftStore";

export type SubmitQuickAddOptions = {
  clientRequestId?: string;
  momentId?: string;
  tab?: string;
  form?: Record<string, unknown>;
  momentTypeCode?: PersonalMomentTypeCode;
};

export function invalidateAfterQuickAdd(
  momentTypeCode: PersonalMomentTypeCode = "LIFE_OPERATIONS",
) {
  invalidatePersonalPulseCache(momentTypeCode);
  invalidatePersonalMemoryCache(momentTypeCode);
  invalidatePersonalLifeCache();
  invalidatePersonalMomentsCache(momentTypeCode);
  invalidateTemplateProjectionCaches(momentTypeCode);
  invalidateQuickAddOptionsCache();
}

/** Narrow invalidation for Build Momentum / Future Building saves — no life or bootstrap. */
export function invalidateAfterFutureBuildingQuickAdd() {
  invalidatePersonalPulseCache("FUTURE_BUILDING");
  invalidatePersonalMomentsCache("FUTURE_BUILDING");
  invalidatePersonalMemoryCache("FUTURE_BUILDING");
  invalidateTemplateProjectionCaches("FUTURE_BUILDING");
  invalidateQuickAddOptionsCache();
}

/** Narrow invalidation for Capture Lifestyle — no life or bootstrap. */
export function invalidateAfterLifestyleQuickAdd() {
  invalidatePersonalPulseCache("LIFESTYLE");
  invalidatePersonalMomentsCache("LIFESTYLE");
  invalidatePersonalMemoryCache("LIFESTYLE");
  invalidateTemplateProjectionCaches("LIFESTYLE");
  invalidateQuickAddOptionsCache();
}

/** Narrow invalidation for Capture Relationships — no life or bootstrap. */
export function invalidateAfterRelationshipsQuickAdd() {
  invalidatePersonalPulseCache("RELATIONSHIPS");
  invalidatePersonalMomentsCache("RELATIONSHIPS");
  invalidatePersonalMemoryCache("RELATIONSHIPS");
  invalidateTemplateProjectionCaches("RELATIONSHIPS");
  invalidateQuickAddOptionsCache();
}

export function invalidateAfterMasterExpense(includeRelationships: boolean) {
  invalidatePersonalPulseCache("LIFE_OPERATIONS");
  invalidatePersonalMemoryCache("LIFE_OPERATIONS");
  invalidatePersonalPulseCache("LIFESTYLE");
  invalidatePersonalMomentsCache("LIFESTYLE");
  invalidatePersonalMemoryCache("LIFESTYLE");
  if (includeRelationships) {
    invalidatePersonalPulseCache("RELATIONSHIPS");
    invalidatePersonalMomentsCache("RELATIONSHIPS");
    invalidatePersonalMemoryCache("RELATIONSHIPS");
  }
  invalidatePersonalLifeCache();
  invalidateQuickAddOptionsCache();
  void import("@/hooks/useMasterExpenseOptions").then((m) =>
    m.invalidateMasterExpenseOptionsCache(),
  );
}

export function invalidateAfterTemplateLifecycle(
  momentTypeCode: PersonalMomentTypeCode = "LIFE_OPERATIONS",
) {
  notifyMomentMutation("PERSONAL", {
    contextState: "ACTIVE",
    pulse: "ACTIVE",
    moments: "ACTIVE",
  });
  invalidateTemplateProjectionCaches(momentTypeCode);
  invalidatePersonalPulseCache(momentTypeCode);
  invalidatePersonalMomentsCache(momentTypeCode);
  invalidatePersonalMemoryCache(momentTypeCode);
  invalidatePersonalLifeCache();
}

export const PersonalRepository = {
  getPulse: async (options?: { momentTypeCode?: string; forceRefresh?: boolean }) =>
    parsePersonalPulseResponse(await getPersonalPulse(options)),
  getMomentsHome: async (options?: { momentTypeCode?: string; forceRefresh?: boolean }) =>
    parsePersonalMomentsHomeResponse(await getPersonalMomentsHome(options)),
  getMemory: async (options?: { momentTypeCode?: string; forceRefresh?: boolean }) =>
    parsePersonalMemoryResponse(await getPersonalMemory(options)),
  getLife: getPersonalLife,
  getCreateOptions: getPersonalCreateOptions,
  getSession: getPersonalSession,
  getInventory: getPersonalInventory,
  getQuickAddOptions: getPersonalQuickAddOptions,

  getTemplateMoments: async (momentTypeCode: PersonalMomentTypeCode) =>
    parseTemplateMomentsResponse(await getTemplateMoments(momentTypeCode)),
  getTemplatePulse: async (momentTypeCode: PersonalMomentTypeCode) =>
    parseTemplatePulseResponse(await getTemplatePulse(momentTypeCode)),
  getTemplateLife: getTemplateLife,
  getTemplateMemory: async (momentTypeCode: PersonalMomentTypeCode) =>
    parseTemplateMemoryResponse(await getTemplateMemory(momentTypeCode)),
  updateTemplateMoment,
  archiveTemplateMoment,
  completeTemplateMoment,

  async createMoment(
    body: PersonalMomentCreateRequest,
  ): Promise<PersonalMomentResponse> {
    const result = await createPersonalMoment(body);
    notifyMomentMutation("PERSONAL", {
      contextState: "SETUP",
      pulse: "SETUP",
      moments: "SETUP",
    });
    return result;
  },

  async patchMoment(
    momentId: string,
    body: PersonalMomentUpdateRequest,
  ): Promise<PersonalMomentResponse> {
    const result = await patchPersonalMoment(momentId, body);
    notifyMomentMutation("PERSONAL");
    return result;
  },

  async submitQuickAdd(
    body: Record<string, unknown>,
    options: SubmitQuickAddOptions = {},
  ) {
    const clientRequestId = options.clientRequestId ?? createClientRequestId();
    const momentTypeCode =
      options.momentTypeCode ??
      ((body.moment_type_code as PersonalMomentTypeCode | undefined) ?? "LIFE_OPERATIONS");

    try {
      const result = await createPersonalQuickAdd(body, { clientRequestId });
      if (options.momentId && options.tab) {
        clearQuickAddDraft(options.momentId, options.tab);
      }
      if (momentTypeCode === "RELATIONSHIPS") {
        invalidateAfterRelationshipsQuickAdd();
      } else if (momentTypeCode === "LIFESTYLE") {
        invalidateAfterLifestyleQuickAdd();
      } else if (momentTypeCode === "FUTURE_BUILDING") {
        invalidateAfterFutureBuildingQuickAdd();
      } else {
        invalidateAfterQuickAdd(momentTypeCode);
      }
      return { result, clientRequestId };
    } catch (err) {
      const { momentId, tab, form } = options;

      if (isNetworkFailure(err) && momentId && tab && form) {
        const draft: QuickAddDraft = {
          momentId,
          tab,
          form,
          payload: body,
          clientRequestId,
          savedAt: new Date().toISOString(),
        };
        saveQuickAddDraft(draft);
      }

      if (err instanceof ApiError && err.status === 409 && err.code === "conflict") {
        if (momentId && tab) {
          clearQuickAddDraft(momentId, tab);
        }
        if (momentTypeCode === "RELATIONSHIPS") {
          invalidateAfterRelationshipsQuickAdd();
        } else if (momentTypeCode === "LIFESTYLE") {
          invalidateAfterLifestyleQuickAdd();
        } else if (momentTypeCode === "FUTURE_BUILDING") {
          invalidateAfterFutureBuildingQuickAdd();
        } else {
          invalidateAfterQuickAdd(momentTypeCode);
        }
        return { result: null, clientRequestId, idempotent: true as const };
      }

      throw err;
    }
  },

  listAccounts: listPersonalAccounts,
  getAccount: getPersonalAccount,
  createAccount: createPersonalAccount,
  patchAccount: patchPersonalAccount,
  archiveAccount: archivePersonalAccount,
  deleteAccount: deletePersonalAccount,

  getMasterExpenseOptions,
  createMasterExpense,

  async listTemplateActivity(
    momentTypeCode: PersonalMomentTypeCode,
    momentId: string,
  ): Promise<TemplateActivityListResponse> {
    return getTemplateActivity(momentTypeCode, momentId);
  },

  async listUnifiedActivity(params?: {
    range?: string;
    domain?: string;
    kind?: string;
    q?: string;
    cursor?: string;
    limit?: number;
  }) {
    return getUnifiedPersonalActivity(params);
  },

  async getTemplateActivityDetail(
    momentTypeCode: PersonalMomentTypeCode,
    eventId: string,
  ): Promise<TemplateActivityDetail> {
    return getTemplateActivityDetail(momentTypeCode, eventId);
  },

  async patchTemplateActivity(
    momentTypeCode: PersonalMomentTypeCode,
    eventId: string,
    body: Record<string, unknown>,
  ): Promise<TemplateActivityDetail> {
    const result = await patchTemplateActivity(momentTypeCode, eventId, body);
    invalidateAfterQuickAdd(momentTypeCode);
    return result;
  },

  async deleteTemplateActivity(
    momentTypeCode: PersonalMomentTypeCode,
    eventId: string,
  ): Promise<void> {
    await deleteTemplateActivity(momentTypeCode, eventId);
    invalidateAfterQuickAdd(momentTypeCode);
  },
};

export type { PersonalAccountPatchRequest, TemplateActivityItem, TemplateActivityDetail };
