import {
  createPersonalMoment,
  getPersonalMomentSetup,
  previewPersonalSetup,
  savePersonalSetupDraft,
  submitPersonalSetup,
} from "@/lib/api/client";
import type {
  PersonalMomentCreateRequest,
  PersonalMomentResponse,
  PersonalSetupAnswers,
  PersonalSetupPreview,
  PersonalSetupResponse,
} from "@/lib/api/personal";
import {
  activateGroupSharedSetup,
  createGroupSharedDraft,
  getGroupSharedSetup,
  previewGroupSharedSetup,
  saveGroupSharedDraft,
  type GroupSharedCategory,
} from "@/lib/api/group";
import {
  GROUP_DEFAULT_PROFILES,
  GROUP_MOMENT_TYPES,
  groupCategoryForType,
} from "@/lib/setup/templates/group";
import { getTemplateByMomentType } from "@/lib/setup/templates/registry";
import { notifyMomentMutation } from "@/stores/bootstrapStore";

const groupMomentById = new Map<string, string>();

function isGroupType(typeCode: string | undefined | null): boolean {
  return !!typeCode && GROUP_MOMENT_TYPES.has(typeCode);
}

function categoryForMoment(momentId: string, typeHint?: string | null): GroupSharedCategory {
  const typeCode = typeHint ?? groupMomentById.get(momentId);
  const category = typeCode ? groupCategoryForType(typeCode) : null;
  if (!category) {
    throw new Error("Unknown group moment type for setup");
  }
  return category;
}

function createBodyForType(typeCode: string): Record<string, string> {
  const category = groupCategoryForType(typeCode);
  const profile = GROUP_DEFAULT_PROFILES[typeCode];
  if (!category || !profile) {
    throw new Error(`Unsupported group moment type: ${typeCode}`);
  }
  if (category === "experience") return { experience_profile: profile };
  if (category === "purchase") return { purchase_profile: profile };
  return { living_type: profile };
}

function toPersonalSetup(state: Record<string, unknown>): PersonalSetupResponse {
  const momentType =
    (state.moment_type_code as string) ||
    groupMomentById.get(String(state.moment_id)) ||
    "SHARED_EXPERIENCE";
  const template = getTemplateByMomentType(momentType);
  const saved = (state.saved_answers as PersonalSetupAnswers | null) ?? null;
  return {
    moment_id: String(state.moment_id),
    moment_type_code: momentType,
    moment_name: String(
      state.moment_name ??
        state.living_name ??
        state.experience_name ??
        state.trip_name ??
        "",
    ),
    status: String(state.status ?? state.lifecycle_status ?? "DRAFT").toUpperCase(),
    title: String(state.title ?? template?.title ?? "Group Setup"),
    subtitle: String(state.subtitle ?? template?.subtitle ?? ""),
    background_image_url: (state.background_image_url as string | null) ?? null,
    fields: Array.isArray(state.fields) ? (state.fields as PersonalSetupResponse["fields"]) : [],
    mission: (state.mission as PersonalSetupResponse["mission"]) ?? null,
    saved_answers: saved,
    cta_label: (state.cta_label as string | null) ?? template?.activation_cta.label ?? null,
    footer_note:
      (state.footer_note as string | null) ?? template?.activation_cta.footer_note ?? null,
  };
}

function toPersonalPreview(preview: Record<string, unknown>): PersonalSetupPreview {
  const narrative = String(preview.narrative ?? preview.insight_text ?? "");
  const blocks = Array.isArray(preview.preview_blocks)
    ? (preview.preview_blocks as Array<{ label: string; value: string | null }>)
    : [];
  const chips = Array.isArray(preview.identity_chips)
    ? (preview.identity_chips as string[])
    : blocks.map((b) => `${b.label}: ${b.value ?? ""}`);
  return {
    narrative,
    rhythm: { label: "Ready", pct: 70 },
    pressure: { label: "Focus", pct: 40 },
    recovery: { label: "Alignment", pct: 55 },
    runtime_priorities: Array.isArray(preview.runtime_priorities)
      ? (preview.runtime_priorities as string[])
      : blocks.slice(0, 3).map((b) => b.label),
    identity_chips: chips,
  };
}

/**
 * Shared setup engine — all MomentEngine setup mutations go through here.
 * Create/activate soft-refresh session stores; they do not force full app bootstrap.
 * Supports Personal (My Money) and Group shared-* backends via template routing.
 */
export const SetupRepository = {
  rememberGroupMoment(momentId: string, momentTypeCode: string) {
    groupMomentById.set(momentId, momentTypeCode);
  },

  async createDraft(
    body: PersonalMomentCreateRequest,
  ): Promise<PersonalMomentResponse> {
    if (isGroupType(body.moment_type_code)) {
      const category = groupCategoryForType(body.moment_type_code)!;
      const created = await createGroupSharedDraft(
        category,
        createBodyForType(body.moment_type_code),
      );
      groupMomentById.set(created.moment_id, created.moment_type_code || body.moment_type_code);
      notifyMomentMutation("GROUP", {
        contextState: "SETUP",
        pulse: "SETUP",
        moments: "SETUP",
      });
      return {
        moment_id: created.moment_id,
        moment_type_id: created.moment_id,
        moment_type_code: created.moment_type_code || body.moment_type_code,
        moment_name: body.moment_name ?? "",
        moment_description: null,
        status: "DRAFT",
        current_runtime_state: "SETUP",
        activated_at: null,
      };
    }
    const result = await createPersonalMoment(body);
    notifyMomentMutation("PERSONAL", {
      contextState: "SETUP",
      pulse: "SETUP",
      moments: "SETUP",
    });
    return result;
  },

  async getSetupState(momentId: string): Promise<PersonalSetupResponse> {
    const typeCode = groupMomentById.get(momentId);
    if (typeCode && isGroupType(typeCode)) {
      const state = await getGroupSharedSetup(categoryForMoment(momentId), momentId);
      if (state.moment_type_code) {
        groupMomentById.set(momentId, state.moment_type_code);
      }
      return toPersonalSetup(state);
    }
    try {
      return await getPersonalMomentSetup(momentId);
    } catch {
      // Fallback: try group categories when moment id was resumed from session.
      for (const category of ["experience", "purchase", "living"] as GroupSharedCategory[]) {
        try {
          const state = await getGroupSharedSetup(category, momentId);
          if (state.moment_type_code) {
            groupMomentById.set(momentId, state.moment_type_code);
          }
          return toPersonalSetup(state);
        } catch {
          /* try next */
        }
      }
      throw new Error("Failed to load setup state");
    }
  },

  async saveDraft(
    momentId: string,
    answers: PersonalSetupAnswers,
  ): Promise<PersonalSetupResponse> {
    const typeCode = groupMomentById.get(momentId);
    if (typeCode && isGroupType(typeCode)) {
      const state = await saveGroupSharedDraft(
        categoryForMoment(momentId),
        momentId,
        answers as Record<string, unknown>,
      );
      return toPersonalSetup(state);
    }
    return savePersonalSetupDraft(momentId, answers);
  },

  async preview(
    momentId: string,
    answers: PersonalSetupAnswers,
  ): Promise<PersonalSetupPreview> {
    const typeCode = groupMomentById.get(momentId);
    if (typeCode && isGroupType(typeCode)) {
      // Always persist latest answers before GET preview so blocks stay current.
      await saveGroupSharedDraft(
        categoryForMoment(momentId),
        momentId,
        answers as Record<string, unknown>,
      );
      const preview = await previewGroupSharedSetup(categoryForMoment(momentId), momentId);
      return toPersonalPreview(preview);
    }
    return previewPersonalSetup(momentId, answers);
  },

  async activate(
    momentId: string,
    answers: PersonalSetupAnswers,
  ): Promise<PersonalMomentResponse> {
    const typeCode = groupMomentById.get(momentId);
    if (typeCode && isGroupType(typeCode)) {
      await saveGroupSharedDraft(
        categoryForMoment(momentId),
        momentId,
        answers as Record<string, unknown>,
      );
      const result = await activateGroupSharedSetup(categoryForMoment(momentId), momentId);
      notifyMomentMutation("GROUP", {
        contextState: "ACTIVE",
        pulse: "ACTIVE",
        moments: "ACTIVE",
      });
      return {
        moment_id: result.moment_id,
        moment_type_id: result.moment_id,
        moment_type_code: typeCode,
        moment_name: "",
        moment_description: null,
        status: "ACTIVE",
        current_runtime_state: "ACTIVE",
        activated_at: new Date().toISOString(),
      };
    }
    const result = await submitPersonalSetup(momentId, answers);
    notifyMomentMutation("PERSONAL", {
      contextState: "ACTIVE",
      pulse: "ACTIVE",
      moments: "ACTIVE",
    });
    return result;
  },
};
