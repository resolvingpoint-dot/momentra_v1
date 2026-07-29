/**
 * QuickAddRegistryValidator (web) — CI/test fail-fast for reference actions.
 * Does not run at production module load (unlike assertQuickAddRegistryComplete).
 */
import { createHash } from "crypto";
import { readFileSync } from "fs";
import { join } from "path";
import { getQuickAddAction, getQuickAddBundleByMomentType } from "./registry";
import { normalizeActionId, normalizeMomentTypeCode } from "./normalize";

export type ReferenceAction = {
  key: string;
  moment_type_code: string;
  action_id: string;
  renderer_id: string;
  endpoint: string;
  edit_endpoint: string | null;
  delete_endpoint: string | null;
  handler_id: string;
  payload_builder_id: string;
  capabilities: Record<string, boolean>;
  output_events: string[];
  affected_projections: string[];
  platforms: string[];
  contract_version?: string;
  ui_action_alias?: string;
};

export type ValidationIssue = { actionKey: string; code: string; message: string };

const FIXTURES_ROOT = join(process.cwd(), "..", "fixtures", "quick_add");

export function loadReferenceActions(fixturesRoot = FIXTURES_ROOT): ReferenceAction[] {
  const raw = JSON.parse(
    readFileSync(join(fixturesRoot, "contract_v1_reference_actions.json"), "utf8"),
  );
  return raw.reference_actions as ReferenceAction[];
}

export function canonicalJson(value: unknown): string {
  if (value === null || typeof value !== "object") {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map((v) => canonicalJson(v)).join(",")}]`;
  }
  const obj = value as Record<string, unknown>;
  const keys = Object.keys(obj).sort();
  return `{${keys.map((k) => `${JSON.stringify(k)}:${canonicalJson(obj[k])}`).join(",")}}`;
}

export function canonicalActionBlob(action: ReferenceAction): string {
  const slim = {
    key: action.key,
    moment_type_code: action.moment_type_code,
    action_id: action.action_id,
    renderer_id: action.renderer_id,
    endpoint: action.endpoint,
    edit_endpoint: action.edit_endpoint,
    delete_endpoint: action.delete_endpoint,
    handler_id: action.handler_id,
    payload_builder_id: action.payload_builder_id,
    capabilities: action.capabilities,
    output_events: action.output_events,
    affected_projections: action.affected_projections,
    platforms: action.platforms,
    contract_version: action.contract_version ?? "v1",
  };
  return canonicalJson(slim);
}

export function computeRegistryHash(actions: ReferenceAction[]): string {
  const joined = [...actions]
    .sort((a, b) => (a.key < b.key ? -1 : a.key > b.key ? 1 : 0))
    .map(canonicalActionBlob)
    .join("\n");
  return createHash("sha256").update(joined).digest("hex");
}

const WEB_PAYLOAD_BUILDERS = new Set([
  "personal.life_operations.expense",
  "personal.future_building.contribution",
  "personal.lifestyle.experience",
  "personal.relationships.connection",
  "group.experience.expense",
  "group.purchase.contributor",
  "group.living.rent",
]);

const WEB_RENDERERS = new Set([
  "personal.life_operations.expense",
  "personal.future_building.contribution",
  "personal.lifestyle.experience",
  "personal.relationships.connection",
  "experience.expense",
  "purchase.contribution",
  "living.rent",
]);

export function validateReferenceRegistry(fixturesRoot = FIXTURES_ROOT): {
  ok: boolean;
  issues: ValidationIssue[];
  registryHash: string;
} {
  const actions = loadReferenceActions(fixturesRoot);
  const issues: ValidationIssue[] = [];

  for (const action of actions) {
    const key = action.key;
    const mt = normalizeMomentTypeCode(action.moment_type_code);
    const aid = normalizeActionId(action.ui_action_alias ?? action.action_id);
    const bundle = getQuickAddBundleByMomentType(mt);
    if (!bundle) {
      issues.push({ actionKey: key, code: "bundle_missing", message: `no bundle for ${mt}` });
    } else {
      const lookupId = action.ui_action_alias ?? action.action_id;
      const registered =
        getQuickAddAction(bundle.template_id, lookupId) ||
        getQuickAddAction(bundle.template_id, aid) ||
        getQuickAddAction(bundle.template_id, action.action_id);
      // Living RENT is Action Center overlay, not always in registry bundle.
      if (!registered && !(mt === "SHARED_LIVING" && action.ui_action_alias === "RENT")) {
        issues.push({
          actionKey: key,
          code: "action_unregistered",
          message: `${lookupId} not in ${bundle.template_id}`,
        });
      }
    }

    if (!WEB_RENDERERS.has(action.renderer_id)) {
      issues.push({
        actionKey: key,
        code: "renderer_missing",
        message: action.renderer_id,
      });
    }
    if (!WEB_PAYLOAD_BUILDERS.has(action.payload_builder_id)) {
      issues.push({
        actionKey: key,
        code: "payload_builder_missing",
        message: action.payload_builder_id,
      });
    }
    if (action.capabilities.edit && !action.edit_endpoint) {
      issues.push({ actionKey: key, code: "edit_endpoint_missing", message: "edit required" });
    }
    if (action.capabilities.delete && !action.delete_endpoint) {
      issues.push({ actionKey: key, code: "delete_endpoint_missing", message: "delete required" });
    }
    if (!action.output_events?.length) {
      issues.push({ actionKey: key, code: "output_events_empty", message: "events required" });
    }
    if (!action.affected_projections?.length) {
      issues.push({ actionKey: key, code: "projections_empty", message: "projections required" });
    }
    const platforms = new Set(action.platforms ?? []);
    for (const p of ["web", "android", "ios", "backend"]) {
      if (!platforms.has(p)) {
        issues.push({ actionKey: key, code: "platforms_incomplete", message: `missing ${p}` });
      }
    }
  }

  const registryHash = computeRegistryHash(actions);
  const lock = readFileSync(join(fixturesRoot, "registry_hash.lock"), "utf8").trim();
  if (registryHash !== lock) {
    issues.push({
      actionKey: "*",
      code: "registry_hash_mismatch",
      message: `expected ${lock}, got ${registryHash}`,
    });
  }

  return { ok: issues.length === 0, issues, registryHash };
}
