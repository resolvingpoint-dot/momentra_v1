/** Debug trace fields for Quick Add v1 (never log PII beyond ids). */
export type QuickAddTrace = {
  contract_version: "v1";
  handler_version: string;
  projection_version: string;
  request_id?: string;
  client_request_id?: string;
  user_id?: string;
  moment_id?: string;
  moment_type_code?: string;
  action_id?: string;
  endpoint?: string;
  handler_name?: string;
  persisted_id?: string;
  event_published?: boolean;
  celery_task_ids?: string[];
  duration_ms?: number;
};

export function buildQuickAddTrace(
  partial: Partial<QuickAddTrace> & {
    moment_id?: string;
    moment_type_code?: string;
    action_id?: string;
  },
): QuickAddTrace {
  return {
    contract_version: "v1",
    handler_version: partial.handler_version ?? "v1",
    projection_version: partial.projection_version ?? "v1",
    ...partial,
  };
}
