"use client";

import { useEffect, useState, type CSSProperties } from "react";
import { Check, Copy, X } from "lucide-react";
import QRCode from "react-qr-code";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { businessCardStyle } from "@/components/business/empty/shared/emptyStyles";
import type { BusinessWorkspaceSummary } from "@/lib/api/business";
import { BusinessRepository } from "@/repositories/BusinessRepository";

type Section = "general" | "members" | "roles" | "security";

type CompanySettingsSheetProps = {
  open: boolean;
  onClose: () => void;
  workspace: BusinessWorkspaceSummary | null;
  onUpdated: () => void;
};

const SECTIONS: { id: Section; label: string }[] = [
  { id: "general", label: "General" },
  { id: "members", label: "Members" },
  { id: "roles", label: "Roles" },
  { id: "security", label: "Security" },
];

const COMING_SOON = ["Departments", "Billing", "Integrations", "Audit"];

export function CompanySettingsSheet({
  open,
  onClose,
  workspace,
  onUpdated,
}: CompanySettingsSheetProps) {
  const tokens = useThemeTokens();
  const { colors, radius } = tokens;
  const [section, setSection] = useState<Section>("general");
  const [name, setName] = useState("");
  const [industry, setIndustry] = useState("");
  const [currency, setCurrency] = useState("INR");
  const [timezone, setTimezone] = useState("Asia/Kolkata");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [members, setMembers] = useState<
    Array<{ member_id: string; user_id: string; role: string; status: string }>
  >([]);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("MEMBER");
  const [lastInviteLink, setLastInviteLink] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!open || !workspace) return;
    setName(workspace.name);
    setIndustry(workspace.industry ?? "");
    setCurrency(workspace.currency ?? "INR");
    setTimezone(workspace.timezone ?? "Asia/Kolkata");
    setSection("general");
    setError(null);
    setLastInviteLink(null);
    setCopied(false);
    void BusinessRepository.listWorkspaceMembers(workspace.id)
      .then((res) => setMembers(res.members ?? []))
      .catch(() => setMembers([]));
  }, [open, workspace]);

  if (!open || !workspace) return null;

  const fieldStyle: CSSProperties = {
    width: "100%",
    borderRadius: radius.input,
    border: `1px solid color-mix(in srgb, ${colors.border} 55%, transparent)`,
    background: colors.surfaceContainer,
    color: colors.textPrimary,
    padding: "10px 12px",
    fontFamily: "inherit",
  };

  async function saveGeneral() {
    setSaving(true);
    setError(null);
    try {
      await BusinessRepository.updateWorkspace(workspace!.id, {
        name,
        industry: industry || null,
        currency_code: currency,
        timezone,
      });
      onUpdated();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not save");
    } finally {
      setSaving(false);
    }
  }

  async function sendInvite() {
    setSaving(true);
    setError(null);
    setCopied(false);
    try {
      const result = await BusinessRepository.inviteWorkspaceMember(workspace!.id, {
        email: inviteEmail,
        role: inviteRole,
      });
      const link =
        (typeof result.invite_link === "string" && result.invite_link) ||
        (typeof result.qr_payload === "string" && result.qr_payload) ||
        (typeof result.token === "string" && result.token
          ? `${window.location.origin}/company-invite/${result.token}`
          : null);
      setLastInviteLink(link);
      setInviteEmail("");
      const res = await BusinessRepository.listWorkspaceMembers(workspace!.id);
      setMembers(res.members ?? []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not invite");
    } finally {
      setSaving(false);
    }
  }

  async function copyInviteLink() {
    if (!lastInviteLink) return;
    try {
      await navigator.clipboard.writeText(lastInviteLink);
      setCopied(true);
    } catch {
      setError("Could not copy link");
    }
  }

  async function archiveWorkspace() {
    if (!confirm(`Archive ${workspace!.name}? This hides the company for all members.`)) {
      return;
    }
    setSaving(true);
    try {
      await BusinessRepository.updateWorkspace(workspace!.id, { status: "ARCHIVED" });
      onUpdated();
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not archive");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-[85] flex items-end justify-center font-[family-name:var(--font-plus-jakarta)] sm:items-center"
      data-momentra-context="business"
    >
      <button
        type="button"
        className="absolute inset-0"
        style={{ background: "rgba(11, 16, 32, 0.72)" }}
        aria-label="Close company settings"
        onClick={onClose}
      />
      <div
        className="relative z-10 flex max-h-[90dvh] w-full max-w-lg flex-col overflow-hidden shadow-2xl sm:rounded-2xl"
        style={{
          background: colors.surfaceElevated,
          color: colors.textPrimary,
          borderRadius: `${radius.xl}px ${radius.xl}px 0 0`,
          border: `1px solid color-mix(in srgb, ${colors.border} 45%, transparent)`,
        }}
      >
        <div
          className="flex items-center justify-between px-4 py-3"
          style={{
            borderBottom: `1px solid color-mix(in srgb, ${colors.border} 40%, transparent)`,
          }}
        >
          <div>
            <h2 className="text-lg font-semibold" style={{ color: colors.textPrimary }}>
              Company Settings
            </h2>
            <p className="text-sm" style={{ color: colors.textSecondary }}>
              {workspace.name}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-2"
            style={{ color: colors.textSecondary }}
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div
          className="flex gap-1 overflow-x-auto px-3 py-2"
          style={{
            borderBottom: `1px solid color-mix(in srgb, ${colors.border} 40%, transparent)`,
          }}
        >
          {SECTIONS.map((s) => {
            const active = section === s.id;
            return (
              <button
                key={s.id}
                type="button"
                onClick={() => setSection(s.id)}
                className="shrink-0 px-3 py-1.5 text-sm font-semibold"
                style={{
                  borderRadius: radius.pill,
                  background: active ? colors.brandPrimary : colors.surfaceContainer,
                  color: active ? colors.brandOnPrimary : colors.textSecondary,
                }}
              >
                {s.label}
              </button>
            );
          })}
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-4">
          {error ? (
            <p
              className="mb-3 px-3 py-2 text-sm"
              style={{
                background: "color-mix(in srgb, #f87171 18%, transparent)",
                color: colors.error,
                borderRadius: radius.md,
              }}
            >
              {error}
            </p>
          ) : null}

          {section === "general" ? (
            <div className="space-y-3">
              <label className="block text-sm">
                <span className="mb-1 block" style={{ color: colors.textSecondary }}>
                  Company name
                </span>
                <input style={fieldStyle} value={name} onChange={(e) => setName(e.target.value)} />
              </label>
              <label className="block text-sm">
                <span className="mb-1 block" style={{ color: colors.textSecondary }}>
                  Industry
                </span>
                <input
                  style={fieldStyle}
                  value={industry}
                  onChange={(e) => setIndustry(e.target.value)}
                  placeholder="Optional"
                />
              </label>
              <label className="block text-sm">
                <span className="mb-1 block" style={{ color: colors.textSecondary }}>
                  Currency
                </span>
                <input
                  style={fieldStyle}
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value.toUpperCase())}
                  maxLength={3}
                />
              </label>
              <label className="block text-sm">
                <span className="mb-1 block" style={{ color: colors.textSecondary }}>
                  Timezone
                </span>
                <input
                  style={fieldStyle}
                  value={timezone}
                  onChange={(e) => setTimezone(e.target.value)}
                />
              </label>
              <button
                type="button"
                disabled={saving}
                onClick={() => void saveGeneral()}
                className="w-full py-2.5 text-sm font-semibold disabled:opacity-50"
                style={{
                  background: colors.brandPrimary,
                  color: colors.brandOnPrimary,
                  borderRadius: radius.button,
                }}
              >
                {saving ? "Saving…" : "Save"}
              </button>
              {workspace.role === "OWNER" ? (
                <button
                  type="button"
                  disabled={saving}
                  onClick={() => void archiveWorkspace()}
                  className="w-full py-2.5 text-sm font-semibold"
                  style={{
                    border: `1px solid color-mix(in srgb, ${colors.error} 45%, transparent)`,
                    color: colors.error,
                    borderRadius: radius.button,
                  }}
                >
                  Archive workspace
                </button>
              ) : null}
            </div>
          ) : null}

          {section === "members" ? (
            <div className="space-y-4">
              <ul className="space-y-2">
                {members.map((m) => (
                  <li
                    key={m.member_id}
                    className="flex items-center justify-between px-3 py-2 text-sm"
                    style={{
                      ...businessCardStyle(tokens),
                      borderRadius: radius.md,
                    }}
                  >
                    <span
                      className="truncate font-mono text-xs"
                      style={{ color: colors.textSecondary }}
                    >
                      {m.user_id.slice(0, 8)}…
                    </span>
                    <span className="font-semibold" style={{ color: colors.textPrimary }}>
                      {m.role}
                    </span>
                  </li>
                ))}
              </ul>
              {(workspace.role === "OWNER" || workspace.role === "MANAGER") && (
                <div
                  className="space-y-2 pt-3"
                  style={{
                    borderTop: `1px solid color-mix(in srgb, ${colors.border} 40%, transparent)`,
                  }}
                >
                  <p className="text-sm font-semibold" style={{ color: colors.textPrimary }}>
                    Invite member
                  </p>
                  <input
                    style={fieldStyle}
                    placeholder="email@company.com"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                  />
                  <select
                    style={fieldStyle}
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value)}
                  >
                    <option value="MEMBER">Member</option>
                    <option value="MANAGER">Manager</option>
                  </select>
                  <button
                    type="button"
                    disabled={saving || !inviteEmail.includes("@")}
                    onClick={() => void sendInvite()}
                    className="w-full py-2.5 text-sm font-semibold disabled:opacity-50"
                    style={{
                      background: colors.brandPrimary,
                      color: colors.brandOnPrimary,
                      borderRadius: radius.button,
                    }}
                  >
                    Send invite
                  </button>
                  {lastInviteLink ? (
                    <div
                      className="space-y-3 pt-3"
                      style={{
                        borderTop: `1px solid color-mix(in srgb, ${colors.border} 40%, transparent)`,
                      }}
                    >
                      <p
                        className="text-sm font-semibold"
                        style={{ color: colors.textPrimary }}
                      >
                        Invite link ready
                      </p>
                      <p
                        className="break-all text-xs"
                        style={{ color: colors.textSecondary }}
                      >
                        {lastInviteLink}
                      </p>
                      <button
                        type="button"
                        onClick={() => void copyInviteLink()}
                        className="flex w-full items-center justify-center gap-2 py-2.5 text-sm font-semibold"
                        style={{
                          border: `1px solid color-mix(in srgb, ${colors.border} 55%, transparent)`,
                          color: colors.textPrimary,
                          borderRadius: radius.button,
                        }}
                      >
                        {copied ? (
                          <Check className="h-4 w-4" strokeWidth={2.5} />
                        ) : (
                          <Copy className="h-4 w-4" strokeWidth={2.5} />
                        )}
                        {copied ? "Copied" : "Copy link"}
                      </button>
                      <div
                        className="mx-auto flex items-center justify-center p-3"
                        style={{
                          background: "#fff",
                          borderRadius: radius.md,
                          width: "fit-content",
                        }}
                      >
                        <QRCode value={lastInviteLink} size={148} />
                      </div>
                    </div>
                  ) : null}
                </div>
              )}
            </div>
          ) : null}

          {section === "roles" ? (
            <div className="space-y-3 text-sm" style={{ color: colors.textSecondary }}>
              <p>
                Workspace roles inherit into Moments. Moment membership can tighten access
                further.
              </p>
              <ul className="space-y-2">
                {[
                  ["Owner", "full admin, archive"],
                  ["Manager", "invite, edit profile"],
                  ["Member", "create and work moments"],
                ].map(([title, desc]) => (
                  <li
                    key={title}
                    className="px-3 py-2"
                    style={{
                      ...businessCardStyle(tokens),
                      borderRadius: radius.md,
                    }}
                  >
                    <strong style={{ color: colors.textPrimary }}>{title}</strong> — {desc}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {section === "security" ? (
            <div className="space-y-2 text-sm" style={{ color: colors.textSecondary }}>
              <p>Only Owners and Managers can invite people to this company.</p>
              <p>Archive requires Owner. Audit log arrives in a later phase.</p>
            </div>
          ) : null}

          <div
            className="mt-6 pt-4"
            style={{
              borderTop: `1px solid color-mix(in srgb, ${colors.border} 40%, transparent)`,
            }}
          >
            <p
              className="mb-2 text-xs font-semibold uppercase tracking-[0.1em]"
              style={{ color: colors.textSubtle }}
            >
              Coming soon
            </p>
            <ul className="grid grid-cols-2 gap-2">
              {COMING_SOON.map((label) => (
                <li
                  key={label}
                  className="px-3 py-2 text-sm"
                  style={{
                    border: `1px dashed color-mix(in srgb, ${colors.border} 55%, transparent)`,
                    color: colors.textSubtle,
                    borderRadius: radius.md,
                  }}
                >
                  {label}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
