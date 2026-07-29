import type { QuickAddActionTemplate } from "./types";
import { getQuickAddAction, getQuickAddActionsForTemplate } from "./registry";

export interface ResolvedBackendEndpoint {
  context_get?: string;
  create_post: string;
  method: "POST" | "PUT";
}

export function resolveBackendEndpoint(
  action: QuickAddActionTemplate,
  momentId: string,
): ResolvedBackendEndpoint {
  const replace = (path: string) => path.replace(/\{moment_id\}/g, momentId);
  return {
    context_get: action.backend_endpoint.context_get
      ? replace(action.backend_endpoint.context_get)
      : undefined,
    create_post: replace(action.backend_endpoint.create_post),
    method: action.backend_endpoint.method ?? "POST",
  };
}

export function getBackendEndpointForAction(
  templateId: string,
  actionId: string,
  momentId: string,
): ResolvedBackendEndpoint | null {
  const action = getQuickAddAction(templateId, actionId);
  if (!action) return null;
  return resolveBackendEndpoint(action, momentId);
}

/** Read-only index of create endpoints grouped by template (for diagnostics). */
export function listCreateEndpointsByTemplate(templateId: string): string[] {
  return getQuickAddActionsForTemplate(templateId).map((a) => a.backend_endpoint.create_post);
}
