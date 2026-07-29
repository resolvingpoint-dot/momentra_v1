"use client";

import { useMemo, useState, type ReactNode } from "react";
import {
  Bell,
  Check,
  Home,
  Pencil,
  Plus,
  Search,
  Settings,
  Trash2,
  Users,
} from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { BusinessWorkspaceSummary } from "@/lib/api/business";

type CompanySwitcherProps = {
  open: boolean;
  onClose: () => void;
  workspaces: BusinessWorkspaceSummary[];
  selectedId: string | null;
  onSelect: (workspaceId: string) => void;
  onNotifications: () => void;
  onCompanySettings: () => void;
  onOpenHome: (workspaceId: string) => void;
  onEditCompany: (workspaceId: string) => void;
  onDeleteCompany: (workspaceId: string) => void;
  onCreate: () => void;
  onJoin: () => void;
};

export function CompanySwitcher({
  open,
  onClose,
  workspaces,
  selectedId,
  onSelect,
  onNotifications,
  onCompanySettings,
  onOpenHome,
  onEditCompany,
  onDeleteCompany,
  onCreate,
  onJoin,
}: CompanySwitcherProps) {
  const tokens = useThemeTokens();
  const { colors, radius } = tokens;
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return workspaces;
    return workspaces.filter(
      (ws) =>
        ws.name.toLowerCase().includes(q) ||
        (ws.role || "").toLowerCase().includes(q),
    );
  }, [workspaces, query]);

  if (!open) return null;

  const divider = {
    borderTop: `1px solid color-mix(in srgb, ${colors.border} 40%, transparent)`,
  };

  return (
    <div
      className="fixed inset-0 z-[80] font-[family-name:var(--font-plus-jakarta)]"
      role="dialog"
      aria-label="Switch company"
      data-momentra-context="business"
    >
      <button
        type="button"
        className="absolute inset-0"
        style={{ background: "rgba(11, 16, 32, 0.72)" }}
        aria-label="Close company switcher"
        onClick={onClose}
      />
      <div
        className="absolute left-3 right-3 top-16 mx-auto max-w-sm overflow-hidden shadow-xl"
        style={{
          background: colors.surfaceElevated,
          border: `1px solid color-mix(in srgb, ${colors.border} 50%, transparent)`,
          borderRadius: radius.xl,
          color: colors.textPrimary,
        }}
      >
        <div
          className="flex items-center gap-2 px-3 py-3"
          style={{
            borderBottom: `1px solid color-mix(in srgb, ${colors.border} 40%, transparent)`,
          }}
        >
          <label
            className="flex min-w-0 flex-1 items-center gap-2 px-2.5 py-2"
            style={{
              background: colors.surfaceContainer,
              borderRadius: radius.md,
              border: `1px solid color-mix(in srgb, ${colors.border} 45%, transparent)`,
            }}
          >
            <Search
              className="h-4 w-4 shrink-0"
              strokeWidth={2.5}
              style={{ color: colors.textSecondary }}
              aria-hidden
            />
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search companies"
              className="min-w-0 flex-1 bg-transparent text-sm outline-none"
              style={{ color: colors.textPrimary }}
              aria-label="Search companies"
            />
          </label>
          <button
            type="button"
            className="shrink-0 rounded-full p-2.5"
            style={{ color: colors.brandPrimary }}
            aria-label="Notifications"
            onClick={() => {
              onClose();
              onNotifications();
            }}
          >
            <Bell className="h-5 w-5" strokeWidth={2.5} />
          </button>
        </div>

        <ul className="max-h-64 overflow-y-auto py-1">
          {filtered.map((ws) => {
            const selected = ws.id === selectedId;
            const isOwner = (ws.role || "").toUpperCase() === "OWNER";
            return (
              <li key={ws.id}>
                <div
                  className="flex w-full items-center gap-2 px-3 py-2.5"
                  style={{
                    background: selected
                      ? colors.primaryContainer
                      : "transparent",
                  }}
                >
                  <button
                    type="button"
                    className="flex min-w-0 flex-1 items-center gap-3 text-left"
                    onClick={() => {
                      onSelect(ws.id);
                      onClose();
                    }}
                  >
                    <span
                      className="flex h-8 w-8 shrink-0 items-center justify-center text-sm font-semibold"
                      style={{
                        background: colors.surfaceContainer,
                        color: colors.onPrimaryContainer,
                        borderRadius: radius.md,
                      }}
                    >
                      {(ws.name || "?").slice(0, 1).toUpperCase()}
                    </span>
                    <span className="min-w-0 flex-1">
                      <span
                        className="block truncate text-[15px] font-semibold"
                        style={{ color: colors.textPrimary }}
                      >
                        {ws.name}
                      </span>
                      <span
                        className="block text-xs"
                        style={{ color: colors.textSecondary }}
                      >
                        {ws.role}
                      </span>
                    </span>
                    {selected ? (
                      <Check
                        className="h-4 w-4 shrink-0"
                        style={{ color: colors.brandPrimary }}
                        strokeWidth={2.5}
                      />
                    ) : null}
                  </button>
                  <div className="flex shrink-0 items-center gap-0.5">
                    <IconBtn
                      label={`Home ${ws.name}`}
                      color={colors.brandPrimary}
                      onClick={() => {
                        onClose();
                        onOpenHome(ws.id);
                      }}
                    >
                      <Home className="h-4 w-4" strokeWidth={2.5} />
                    </IconBtn>
                    <IconBtn
                      label={`Edit ${ws.name}`}
                      color={colors.brandPrimary}
                      onClick={() => {
                        onClose();
                        onEditCompany(ws.id);
                      }}
                    >
                      <Pencil className="h-4 w-4" strokeWidth={2.5} />
                    </IconBtn>
                    <IconBtn
                      label={`Delete ${ws.name}`}
                      color={isOwner ? colors.error : colors.textSubtle}
                      disabled={!isOwner}
                      onClick={() => {
                        if (!isOwner) return;
                        onClose();
                        onDeleteCompany(ws.id);
                      }}
                    >
                      <Trash2 className="h-4 w-4" strokeWidth={2.5} />
                    </IconBtn>
                  </div>
                </div>
              </li>
            );
          })}
          {filtered.length === 0 ? (
            <li
              className="px-4 py-6 text-center text-sm"
              style={{ color: colors.textSecondary }}
            >
              {workspaces.length === 0 ? "No companies yet" : "No matches"}
            </li>
          ) : null}
        </ul>

        <div className="py-1" style={divider}>
          <p
            className="px-4 pb-1 pt-2 text-[10px] font-semibold uppercase tracking-[0.12em]"
            style={{ color: colors.textSecondary }}
          >
            Quick actions
          </p>
          <button
            type="button"
            className="flex w-full items-center gap-3 px-4 py-3 text-left text-[15px] font-semibold disabled:opacity-50"
            style={{ color: colors.textPrimary }}
            disabled={!selectedId}
            onClick={() => {
              onClose();
              onCompanySettings();
            }}
          >
            <Settings
              className="h-4 w-4"
              strokeWidth={2.5}
              style={{ color: colors.brandPrimary }}
            />
            Company Settings
          </button>
          <button
            type="button"
            className="flex w-full items-center gap-3 px-4 py-3 text-left text-[15px] font-semibold"
            style={{ color: colors.textPrimary }}
            onClick={() => {
              onClose();
              onCreate();
            }}
          >
            <Plus
              className="h-4 w-4"
              strokeWidth={2.5}
              style={{ color: colors.brandPrimary }}
            />
            Create Company
          </button>
          <button
            type="button"
            className="flex w-full items-center gap-3 px-4 py-3 text-left text-[15px] font-semibold"
            style={{ color: colors.textPrimary }}
            onClick={() => {
              onClose();
              onJoin();
            }}
          >
            <Users
              className="h-4 w-4"
              strokeWidth={2.5}
              style={{ color: colors.brandPrimary }}
            />
            Join Company
          </button>
        </div>
      </div>
    </div>
  );
}

function IconBtn({
  label,
  color,
  disabled,
  onClick,
  children,
}: {
  label: string;
  color: string;
  disabled?: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      className="rounded-md p-1.5 disabled:opacity-35"
      style={{ color }}
      aria-label={label}
      disabled={disabled}
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
    >
      {children}
    </button>
  );
}
