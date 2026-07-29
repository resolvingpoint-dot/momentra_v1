"use client";

import { TEAM_OPS_ACTION_META, TEAM_OPS_ACTION_TYPES } from "@/lib/business/teamOpsActionRegistry";
import type { BusinessActivityFilters, ActivitySort } from "@/lib/business/activityFilters";
import { TEAM_OPS } from "../shared/teamOpsTheme";

type Props = {
  filters: BusinessActivityFilters;
  onChange: (next: BusinessActivityFilters) => void;
  memberOptions?: Array<{ id: string; label: string }>;
  /** Override action chips (e.g. Business Operations). Defaults to Team Ops. */
  actionTypes?: readonly string[];
  actionMeta?: Record<string, { label: string }>;
};

export function TeamOperationsActivityFilters({
  filters,
  onChange,
  memberOptions = [],
  actionTypes = TEAM_OPS_ACTION_TYPES,
  actionMeta = TEAM_OPS_ACTION_META,
}: Props) {
  return (
    <div className="flex flex-col gap-3" role="search" aria-label="Activity filters">
      <label className="block text-xs" style={{ color: TEAM_OPS.onVariant }}>
        Search
        <input
          type="search"
          className="mt-1 w-full rounded-xl px-3 py-2 text-sm outline-none focus-visible:ring-2"
          style={{
            background: TEAM_OPS.surface,
            color: TEAM_OPS.onSurface,
            border: `1px solid ${TEAM_OPS.outline}55`,
          }}
          value={filters.search ?? ""}
          onChange={(e) => onChange({ ...filters, search: e.target.value })}
          placeholder="Search title or type"
        />
      </label>

      <fieldset>
        <legend className="mb-2 text-xs" style={{ color: TEAM_OPS.onVariant }}>
          Action type
        </legend>
        <div className="flex flex-wrap gap-2">
          {actionTypes.map((type) => {
            const active = filters.actionTypes?.includes(type);
            return (
              <button
                key={type}
                type="button"
                aria-pressed={Boolean(active)}
                className="rounded-full px-3 py-1 text-[11px] font-semibold focus-visible:outline focus-visible:outline-2"
                style={{
                  background: active ? TEAM_OPS.primaryContainer : TEAM_OPS.surfaceLow,
                  color: active ? "#0d0096" : TEAM_OPS.onVariant,
                  border: `1px solid ${TEAM_OPS.outline}33`,
                  minHeight: 32,
                }}
                onClick={() => {
                  const cur = new Set(filters.actionTypes ?? []);
                  if (cur.has(type)) cur.delete(type);
                  else cur.add(type);
                  onChange({ ...filters, actionTypes: [...cur] });
                }}
              >
                {actionMeta[type]?.label ?? type}
              </button>
            );
          })}
        </div>
      </fieldset>

      <div className="grid grid-cols-2 gap-2">
        <label className="text-xs" style={{ color: TEAM_OPS.onVariant }}>
          From
          <input
            type="date"
            className="mt-1 w-full rounded-xl px-2 py-2 text-sm"
            style={{ background: TEAM_OPS.surface, color: TEAM_OPS.onSurface }}
            value={filters.dateFrom?.slice(0, 10) ?? ""}
            onChange={(e) =>
              onChange({ ...filters, dateFrom: e.target.value ? `${e.target.value}T00:00:00` : null })
            }
          />
        </label>
        <label className="text-xs" style={{ color: TEAM_OPS.onVariant }}>
          To
          <input
            type="date"
            className="mt-1 w-full rounded-xl px-2 py-2 text-sm"
            style={{ background: TEAM_OPS.surface, color: TEAM_OPS.onSurface }}
            value={filters.dateTo?.slice(0, 10) ?? ""}
            onChange={(e) =>
              onChange({ ...filters, dateTo: e.target.value ? `${e.target.value}T23:59:59` : null })
            }
          />
        </label>
      </div>

      <div className="flex flex-wrap gap-2">
        <label className="text-xs" style={{ color: TEAM_OPS.onVariant }}>
          Sort
          <select
            className="mt-1 block rounded-xl px-2 py-2 text-sm"
            style={{ background: TEAM_OPS.surface, color: TEAM_OPS.onSurface }}
            value={filters.sort ?? "newest"}
            onChange={(e) => onChange({ ...filters, sort: e.target.value as ActivitySort })}
          >
            <option value="newest">Newest</option>
            <option value="oldest">Oldest</option>
          </select>
        </label>
        <label className="text-xs" style={{ color: TEAM_OPS.onVariant }}>
          Status
          <select
            className="mt-1 block rounded-xl px-2 py-2 text-sm"
            style={{ background: TEAM_OPS.surface, color: TEAM_OPS.onSurface }}
            value={filters.status ?? "all"}
            onChange={(e) =>
              onChange({
                ...filters,
                status: e.target.value as BusinessActivityFilters["status"],
              })
            }
          >
            <option value="all">All</option>
            <option value="active">Active</option>
            <option value="voided">Archived</option>
          </select>
        </label>
        {memberOptions.length > 0 ? (
          <label className="text-xs" style={{ color: TEAM_OPS.onVariant }}>
            Member
            <select
              className="mt-1 block rounded-xl px-2 py-2 text-sm"
              style={{ background: TEAM_OPS.surface, color: TEAM_OPS.onSurface }}
              value={filters.memberId ?? ""}
              onChange={(e) => onChange({ ...filters, memberId: e.target.value || null })}
            >
              <option value="">Anyone</option>
              {memberOptions.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.label}
                </option>
              ))}
            </select>
          </label>
        ) : null}
      </div>
    </div>
  );
}
