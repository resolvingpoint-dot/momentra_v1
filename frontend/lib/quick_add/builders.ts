import type {
  ActionCapabilities,
  ActionCenterCategory,
  QuickAddActionTemplate,
  QuickAddBackendEndpoint,
  QuickAddContext,
  QuickAddField,
  QuickAddImpactPreview,
  QuickAddOutputEvent,
  QuickAddShell,
  QuickAddTemplateBundle,
  QuickAddValidation,
  ReusableActionType,
} from "./types";

export interface ActionDef {
  action_id: string;
  reusable_type: ReusableActionType;
  label: string;
  icon: string;
  display_order: number;
  cta_label: string;
  fields: QuickAddField[];
  validation: QuickAddValidation;
  impact_preview: QuickAddImpactPreview;
  backend_endpoint: QuickAddBackendEndpoint;
  output_event: QuickAddOutputEvent;
  affects_modules: string[];
  section?: string;
  tab_code?: string;
  shell?: QuickAddShell;
  subtitle?: string;
  category?: ActionCenterCategory;
  accent?: string;
  priority?: number;
  estimated_time_sec?: number;
  tags?: string[];
  synonyms?: string[];
  renderer_id?: string;
  analytics_id?: string;
  supports?: ActionCapabilities;
}

export function field(
  key: string,
  label: string,
  field_type: QuickAddField["field_type"],
  extra?: Partial<QuickAddField>,
): QuickAddField {
  return { key, label, field_type, ...extra };
}

export function buildBundle(
  template_id: string,
  context: QuickAddContext,
  shell: QuickAddShell,
  actions: ActionDef[],
  opts?: { default_action_id?: string; sub_flows?: ActionDef[] },
): QuickAddTemplateBundle {
  const toAction = (def: ActionDef, actionShell: QuickAddShell): QuickAddActionTemplate => ({
    template_id,
    context,
    shell: def.shell ?? actionShell,
    action_id: def.action_id,
    reusable_type: def.reusable_type,
    label: def.label,
    icon: def.icon,
    section: def.section,
    tab_code: def.tab_code,
    display_order: def.display_order,
    cta_label: def.cta_label,
    fields: def.fields,
    validation: def.validation,
    impact_preview: def.impact_preview,
    backend_endpoint: def.backend_endpoint,
    output_event: def.output_event,
    affects_modules: def.affects_modules,
    subtitle: def.subtitle,
    category: def.category,
    accent: def.accent,
    priority: def.priority,
    estimated_time_sec: def.estimated_time_sec,
    tags: def.tags,
    synonyms: def.synonyms,
    renderer_id: def.renderer_id,
    analytics_id: def.analytics_id,
    supports: def.supports,
  });

  return {
    template_id,
    context,
    shell,
    default_action_id: opts?.default_action_id,
    actions: actions.map((a) => toAction(a, shell)),
    sub_flows: opts?.sub_flows?.map((a) => toAction(a, "sub_flow")),
  };
}

export function personalEndpoint(path: string, contextGet?: string): QuickAddBackendEndpoint {
  return {
    context_get: contextGet,
    create_post: path,
    method: "POST",
  };
}

export function groupTripEndpoint(
  action: string,
  createPost: string,
): QuickAddBackendEndpoint {
  return {
    context_get: `GET /api/v1/group/trips/{moment_id}/quick-add/${action}/context`,
    create_post: createPost,
    method: "POST",
  };
}

export function groupPurchaseEndpoint(action: string): QuickAddBackendEndpoint {
  return {
    context_get: `GET /api/v1/group/shared-purchase/moments/{moment_id}/quick-add/${action}/context`,
    create_post: `POST /api/v1/group/shared-purchase/moments/{moment_id}/quick-add/${action}`,
    method: "POST",
  };
}

export function groupLivingEndpoint(action: string): QuickAddBackendEndpoint {
  return {
    context_get: `GET /api/v1/group/shared-living/moments/{moment_id}/quick-add/${action}/context`,
    create_post: `POST /api/v1/group/shared-living/moments/{moment_id}/quick-add/${action}`,
    method: "POST",
  };
}

export function businessEndpoint(path: string): QuickAddBackendEndpoint {
  return {
    create_post: path,
    method: "POST",
  };
}
