"use client";

import { useState, type CSSProperties } from "react";
import { X } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { acceptBusinessWorkspaceInvite } from "@/lib/api/client";
import { extractCompanyInviteToken } from "@/lib/invite/inviteToken";

type JoinCompanySheetProps = {
  open: boolean;
  onClose: () => void;
  onJoined: (workspaceId: string) => void;
};

export function JoinCompanySheet({
  open,
  onClose,
  onJoined,
}: JoinCompanySheetProps) {
  const tokens = useThemeTokens();
  const { colors, radius } = tokens;
  const [paste, setPaste] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!open) return null;

  const fieldStyle: CSSProperties = {
    width: "100%",
    borderRadius: radius.input,
    border: `1px solid color-mix(in srgb, ${colors.border} 55%, transparent)`,
    background: colors.surfaceContainer,
    color: colors.textPrimary,
    padding: "10px 12px",
    fontFamily: "inherit",
  };

  async function join() {
    const token = extractCompanyInviteToken(paste);
    if (!token) {
      setError("Paste a company invite link or token.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const ws = await acceptBusinessWorkspaceInvite(token);
      setPaste("");
      onJoined(ws.id);
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not join company");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-[90] flex items-end justify-center font-[family-name:var(--font-plus-jakarta)] sm:items-center"
      role="dialog"
      aria-label="Join company"
      data-momentra-context="business"
    >
      <button
        type="button"
        className="absolute inset-0"
        style={{ background: "rgba(11, 16, 32, 0.72)" }}
        aria-label="Close join company"
        onClick={onClose}
      />
      <div
        className="relative z-10 w-full max-w-md overflow-hidden shadow-2xl sm:rounded-2xl"
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
          <h2 className="text-lg font-semibold">Join Company</h2>
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
        <div className="space-y-3 px-4 py-4">
          <p className="text-sm" style={{ color: colors.textSecondary }}>
            Paste a company invite link or token. QR codes from Company Settings
            encode the same link.
          </p>
          <textarea
            style={{ ...fieldStyle, minHeight: 88, resize: "vertical" }}
            placeholder="https://momentra.tech/company-invite/… or token"
            value={paste}
            onChange={(e) => setPaste(e.target.value)}
            disabled={busy}
          />
          {error ? (
            <p className="text-sm" style={{ color: colors.error }}>
              {error}
            </p>
          ) : null}
          <button
            type="button"
            disabled={busy || !paste.trim()}
            onClick={() => void join()}
            className="w-full py-2.5 text-sm font-semibold disabled:opacity-50"
            style={{
              background: colors.brandPrimary,
              color: colors.brandOnPrimary,
              borderRadius: radius.button,
            }}
          >
            {busy ? "Joining…" : "Join company"}
          </button>
        </div>
      </div>
    </div>
  );
}
