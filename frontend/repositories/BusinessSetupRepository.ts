import {
  activateBusinessSetup,
  createBusinessMoment,
  createBusinessSetupInviteDraft,
  getBusinessSetupState,
  previewBusinessSetup,
  saveBusinessSetupDraft,
} from "@/lib/api/client";
import type {
  BusinessActivateResponse,
  BusinessMomentCreateResponse,
  BusinessSetupInviteDraft,
  BusinessSetupPreview,
  BusinessSetupState,
} from "@/lib/api/business";
import { notifyMomentMutation } from "@/stores/bootstrapStore";
import { getBusinessSessionSnapshot } from "@/stores/businessSessionStore";

const TEMPLATE_ID_BY_TYPE: Record<string, string> = {
  TEAM_OPERATIONS: "team_ops",
  BUSINESS_RUNWAY: "business_runway",
  BUSINESS_OPERATIONS: "business_operations",
};

export const BusinessSetupRepository = {
  templateIdForType(momentTypeCode: string): string {
    return TEMPLATE_ID_BY_TYPE[momentTypeCode] ?? momentTypeCode.toLowerCase();
  },

  async createDraft(input: {
    moment_type_code: string;
    title?: string;
    template_id?: string;
  }): Promise<BusinessMomentCreateResponse> {
    const templateId =
      input.template_id ?? BusinessSetupRepository.templateIdForType(input.moment_type_code);
    const session = getBusinessSessionSnapshot();
    const workspaceId =
      session.selectedWorkspaceId ?? session.bootstrap?.selected_workspace?.id ?? null;
    const created = await createBusinessMoment({
      moment_type_code: input.moment_type_code,
      title: input.title,
      template_id: templateId,
      template_version: "1",
      workspace_id: workspaceId,
    });
    // Soft session refresh — does not force full app bootstrap.
    notifyMomentMutation("BUSINESS", { contextState: "SETUP" });
    return created;
  },

  getSetupState(momentId: string): Promise<BusinessSetupState> {
    return getBusinessSetupState(momentId);
  },

  saveDraft(
    momentId: string,
    answers: Record<string, unknown>,
    progress?: { current_step: number; completed_steps: number[] },
  ): Promise<BusinessSetupState> {
    return saveBusinessSetupDraft(momentId, {
      answers,
      progress,
      setup_version: "1",
    });
  },

  preview(momentId: string, answers?: Record<string, unknown>): Promise<BusinessSetupPreview> {
    return previewBusinessSetup(momentId, { answers });
  },

  async activate(momentId: string): Promise<BusinessActivateResponse> {
    const result = await activateBusinessSetup(momentId);
    notifyMomentMutation("BUSINESS", { contextState: "ACTIVE" });
    return result;
  },

  createInviteDraft(
    momentId: string,
    localId: string,
    channel = "EMAIL",
  ): Promise<BusinessSetupInviteDraft> {
    return createBusinessSetupInviteDraft(momentId, {
      local_id: localId,
      channel,
    });
  },
};
