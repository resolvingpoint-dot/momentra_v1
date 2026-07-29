"use client";

import { useEffect, useState } from "react";
import { Copy, Loader2, X } from "lucide-react";
import QRCode from "react-qr-code";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { GroupSetupInviteSection } from "@/components/group/setup/shared/GroupSetupInviteSection";
import { BusinessSetupRepository } from "@/repositories/BusinessSetupRepository";

type MomentInviteSheetProps = {
  open: boolean;
  onClose: () => void;
  momentId: string | null;
  momentLabel?: string;
  variant: "group" | "business";
};

/**
 * Switcher invite surface — Group uses invite-draft panel;
 * Business mints a LINK invite for the first setup member when available.
 */
export function MomentInviteSheet({
  open,
  onClose,
  momentId,
  momentLabel,
  variant,
}: MomentInviteSheetProps) {
  const { colors, radius } = useThemeTokens();
  const [bizLink, setBizLink] = useState<string | null>(null);
  const [bizError, setBizError] = useState<string | null>(null);
  const [bizLoading, setBizLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!open || variant !== "business" || !momentId) {
      setBizLink(null);
      setBizError(null);
      setBizLoading(false);
      return;
    }
    let cancelled = false;
    setBizLoading(true);
    setBizError(null);
    void (async () => {
      try {
        const state = await BusinessSetupRepository.getSetupState(momentId);
        const members = (state.answers?.members as Array<{ local_id?: string }> | undefined) ?? [];
        const localId = members.find((m) => m.local_id)?.local_id;
        if (!localId) {
          if (!cancelled) {
            setBizError("Add a teammate in moment setup first, then invite from here.");
            setBizLoading(false);
          }
          return;
        }
        const draft = await BusinessSetupRepository.createInviteDraft(
          momentId,
          localId,
          "LINK",
        );
        if (!cancelled) {
          setBizLink(draft.invite_link || draft.qr_payload || null);
          setBizLoading(false);
        }
      } catch (e) {
        if (!cancelled) {
          setBizError(e instanceof Error ? e.message : "Could not load invite");
          setBizLoading(false);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [open, variant, momentId]);

  if (!open || !momentId) return null;

  return (
    <div
      className="fixed inset-0 z-[90] flex items-end justify-center font-[family-name:var(--font-plus-jakarta)] sm:items-center"
      role="dialog"
      aria-label="Invite to moment"
    >
      <button
        type="button"
        className="absolute inset-0"
        style={{ background: "rgba(11, 16, 32, 0.72)" }}
        aria-label="Close invite"
        onClick={onClose}
      />
      <div
        className="relative z-10 max-h-[85dvh] w-full max-w-md overflow-y-auto shadow-2xl sm:rounded-2xl"
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
            <h2 className="text-lg font-semibold">Invite</h2>
            {momentLabel ? (
              <p className="text-sm" style={{ color: colors.textSecondary }}>
                {momentLabel}
              </p>
            ) : null}
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
        <div className="px-4 py-4">
          {variant === "group" ? (
            <GroupSetupInviteSection momentId={momentId} />
          ) : bizLoading ? (
            <div
              className="flex items-center gap-2 text-sm"
              style={{ color: colors.textSecondary }}
            >
              <Loader2 className="size-4 animate-spin" aria-hidden />
              Preparing invite…
            </div>
          ) : bizError ? (
            <p className="text-sm" style={{ color: colors.error }}>
              {bizError}
            </p>
          ) : bizLink ? (
            <div className="space-y-3">
              <p className="break-all text-xs" style={{ color: colors.textSecondary }}>
                {bizLink}
              </p>
              <button
                type="button"
                className="flex w-full items-center justify-center gap-2 py-2.5 text-sm font-semibold"
                style={{
                  border: `1px solid color-mix(in srgb, ${colors.border} 55%, transparent)`,
                  borderRadius: radius.button,
                  color: colors.textPrimary,
                }}
                onClick={() => {
                  void navigator.clipboard.writeText(bizLink).then(() => {
                    setCopied(true);
                    window.setTimeout(() => setCopied(false), 1600);
                  });
                }}
              >
                <Copy className="h-4 w-4" strokeWidth={2.5} />
                {copied ? "Copied" : "Copy link"}
              </button>
              <div
                className="mx-auto flex items-center justify-center p-3"
                style={{ background: "#fff", borderRadius: radius.md, width: "fit-content" }}
              >
                <QRCode value={bizLink} size={148} />
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
