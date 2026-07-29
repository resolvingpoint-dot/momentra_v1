"use client";

import { useState } from "react";
import {
  Copy,
  Loader2,
  Mail,
  MessageCircle,
  QrCode,
  Share2,
  X,
} from "lucide-react";
import QRCode from "react-qr-code";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { SetupChoice } from "@/components/setup/shared/setupControlTypes";
import { BusinessSetupRepository } from "@/repositories/BusinessSetupRepository";
import type { BusinessSetupInviteDraft } from "@/lib/api/business";

type Props = {
  open: boolean;
  onClose: () => void;
  memberName?: string;
  currentMethod?: string;
  methods: SetupChoice[];
  onSelect: (method: string) => void;
  /** When set, selecting a method fetches a shareable invite draft and opens delivery UI. */
  momentId?: string;
  localId?: string;
  memberEmail?: string | null;
  memberPhone?: string | null;
  /** Flush draft so the member exists server-side before invite-draft. */
  onBeforeInvite?: () => Promise<boolean>;
  onEmailRequired?: () => void;
};

function WhatsAppGlyph({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.435 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
    </svg>
  );
}

function channelForMethod(method: string): string {
  const m = method.toUpperCase();
  if (m === "LINK" || m === "SHARE") return "COPY_LINK";
  if (m === "MESSAGE") return "SMS";
  return m;
}

export function SetupInviteSheet({
  open,
  onClose,
  memberName,
  currentMethod,
  methods,
  onSelect,
  momentId,
  localId,
  memberEmail,
  memberPhone,
  onBeforeInvite,
  onEmailRequired,
}: Props) {
  const { colors } = useThemeTokens();
  const [phase, setPhase] = useState<"methods" | "delivery">("methods");
  const [draft, setDraft] = useState<BusinessSetupInviteDraft | null>(null);
  const [selectedChannel, setSelectedChannel] = useState<string>("EMAIL");
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [showQr, setShowQr] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!open) return null;

  function resetAndClose() {
    setPhase("methods");
    setDraft(null);
    setStatus(null);
    setError(null);
    setBusy(null);
    setLoading(false);
    setShowQr(false);
    onClose();
  }

  async function handleMethodSelect(method: string) {
    const channel = channelForMethod(method);
    onSelect(method);

    if (channel === "EMAIL" && !(memberEmail || "").trim()) {
      onEmailRequired?.();
      setError("Email required to invite");
      return;
    }

    if (!momentId || !localId) {
      resetAndClose();
      return;
    }

    setError(null);
    setLoading(true);
    setSelectedChannel(channel);
    try {
      if (onBeforeInvite) {
        const ok = await onBeforeInvite();
        if (!ok) {
          setError("Could not save member before invite");
          setLoading(false);
          return;
        }
      }
      const next = await BusinessSetupRepository.createInviteDraft(momentId, localId, channel);
      setDraft(next);
      setPhase("delivery");
      // Auto-open the chosen channel action where possible
      if (channel === "QR") setShowQr(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create invite");
    } finally {
      setLoading(false);
    }
  }

  async function handleCopy() {
    if (!draft) return;
    setBusy("copy");
    try {
      await navigator.clipboard.writeText(draft.invite_link);
      setStatus("Invite link copied");
    } catch {
      setStatus("Could not copy link");
    } finally {
      setBusy(null);
    }
  }

  async function handleShare() {
    if (!draft) return;
    setBusy("share");
    const text = draft.whatsapp_text || draft.invite_link;
    try {
      if (typeof navigator !== "undefined" && typeof navigator.share === "function") {
        await navigator.share({
          title: memberName ? `Invite ${memberName}` : "Momentra invite",
          text,
          url: draft.invite_link,
        });
        setStatus("Shared");
      } else {
        await navigator.clipboard.writeText(draft.invite_link);
        setStatus("Link copied — share it from your apps.");
      }
    } catch (err) {
      if ((err as Error)?.name !== "AbortError") {
        setStatus("Could not open share sheet");
      }
    } finally {
      setBusy(null);
    }
  }

  function handleWhatsApp() {
    if (!draft) return;
    const text = draft.whatsapp_text || draft.invite_link;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, "_blank", "noopener,noreferrer");
    setStatus("Opened WhatsApp");
  }

  function handleSms() {
    if (!draft) return;
    const body = draft.sms_text || draft.whatsapp_text || draft.invite_link;
    const phone = (memberPhone || "").replace(/[^\d+]/g, "");
    const href = phone
      ? `sms:${phone}?&body=${encodeURIComponent(body)}`
      : `sms:?&body=${encodeURIComponent(body)}`;
    window.location.href = href;
    setStatus("Opened Messages");
  }

  function handleEmail() {
    if (!draft) return;
    const email = (memberEmail || "").trim();
    if (!email) {
      onEmailRequired?.();
      setError("Email required to invite");
      return;
    }
    const mailto = `mailto:${encodeURIComponent(email)}?subject=${encodeURIComponent(
      draft.email_subject || "You're invited",
    )}&body=${encodeURIComponent(draft.email_body || draft.invite_link)}`;
    window.location.href = mailto;
    setStatus(`Opened mail for ${email}`);
  }

  const secondaryBtn = {
    background: colors.surfaceContainer,
    color: colors.textPrimary,
  } as const;
  const primaryBtn = {
    background: colors.primaryContainer,
    color: colors.brandOnPrimary,
  } as const;

  return (
    <div className="fixed inset-0 z-[60] flex items-end justify-center sm:items-center">
      <button
        type="button"
        className="absolute inset-0 bg-black/40"
        aria-label="Close invite sheet"
        onClick={resetAndClose}
      />
      <div
        className="relative z-10 w-full max-w-md rounded-t-2xl p-4 sm:rounded-2xl"
        style={{ background: colors.background, color: colors.textPrimary }}
        role="dialog"
        aria-modal="true"
        aria-label="Invite method"
      >
        <div className="mb-3 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold">
              Invite{memberName ? ` ${memberName}` : ""}
            </p>
            <p className="text-xs opacity-60">
              {phase === "methods"
                ? "Choose how to send the invitation."
                : "Share the invite with this person."}
            </p>
          </div>
          <button
            type="button"
            onClick={resetAndClose}
            className="rounded-full p-2"
            style={{ background: colors.surfaceContainer }}
            aria-label="Close"
          >
            <X className="size-4" />
          </button>
        </div>

        {phase === "methods" ? (
          <div className="space-y-2">
            {methods.map((m) => (
              <button
                key={m.value}
                type="button"
                disabled={loading}
                onClick={() => void handleMethodSelect(m.value)}
                className="w-full rounded-xl px-4 py-3 text-left text-sm font-semibold disabled:opacity-60"
                style={{
                  background:
                    currentMethod === m.value
                      ? `color-mix(in srgb, ${colors.primary} 16%, transparent)`
                      : colors.surfaceContainer,
                }}
              >
                {loading && channelForMethod(m.value) === selectedChannel ? (
                  <span className="inline-flex items-center gap-2">
                    <Loader2 className="size-4 animate-spin" />
                    Preparing…
                  </span>
                ) : (
                  m.label
                )}
              </button>
            ))}
            {error ? (
              <p className="text-xs" style={{ color: colors.error }} role="alert">
                {error}
              </p>
            ) : null}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                className="inline-flex items-center justify-center gap-2 rounded-2xl px-4 py-3.5 text-sm font-semibold"
                style={primaryBtn}
                onClick={() => setShowQr(true)}
              >
                <QrCode className="size-5" />
                Show QR
              </button>
              <button
                type="button"
                className="inline-flex items-center justify-center gap-2 rounded-2xl px-4 py-3.5 text-sm font-semibold disabled:opacity-60"
                style={primaryBtn}
                disabled={busy === "share"}
                onClick={() => void handleShare()}
              >
                {busy === "share" ? (
                  <Loader2 className="size-5 animate-spin" />
                ) : (
                  <Share2 className="size-5" />
                )}
                Share
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
              {(
                [
                  {
                    id: "whatsapp",
                    label: "WhatsApp",
                    icon: <WhatsAppGlyph className="size-5" />,
                    onClick: handleWhatsApp,
                    highlight: selectedChannel === "WHATSAPP",
                  },
                  {
                    id: "sms",
                    label: "Message",
                    icon: <MessageCircle className="size-5" />,
                    onClick: handleSms,
                    highlight: selectedChannel === "SMS",
                  },
                  {
                    id: "email",
                    label: "Email",
                    icon: <Mail className="size-5" />,
                    onClick: handleEmail,
                    highlight: selectedChannel === "EMAIL",
                  },
                  {
                    id: "copy",
                    label: "Copy Link",
                    icon:
                      busy === "copy" ? (
                        <Loader2 className="size-5 animate-spin" />
                      ) : (
                        <Copy className="size-5" />
                      ),
                    onClick: () => void handleCopy(),
                    highlight:
                      selectedChannel === "COPY_LINK" || selectedChannel === "SHARE",
                  },
                ] as const
              ).map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className="flex flex-col items-center gap-1.5 rounded-xl px-1 py-3 text-[11px] font-medium"
                  style={{
                    ...secondaryBtn,
                    ...(item.highlight
                      ? {
                          background: `color-mix(in srgb, ${colors.primary} 16%, transparent)`,
                        }
                      : {}),
                  }}
                  onClick={item.onClick}
                >
                  {item.icon}
                  <span className="text-center leading-tight">{item.label}</span>
                </button>
              ))}
            </div>

            {status ? (
              <p className="text-sm" style={{ color: colors.textSecondary }}>
                {status}
              </p>
            ) : null}
            {error ? (
              <p className="text-xs" style={{ color: colors.error }} role="alert">
                {error}
              </p>
            ) : null}

            <button
              type="button"
              className="w-full text-sm font-medium"
              style={{ color: colors.textSecondary }}
              onClick={() => {
                setPhase("methods");
                setDraft(null);
                setStatus(null);
                setError(null);
              }}
            >
              Choose another method
            </button>
          </div>
        )}

        {showQr && draft ? (
          <div
            className="fixed inset-0 z-[80] flex items-end justify-center bg-black/45 p-4 sm:items-center"
            role="dialog"
            aria-modal
            onClick={() => setShowQr(false)}
          >
            <div
              className="w-full max-w-sm rounded-3xl p-5 shadow-xl"
              style={{ background: colors.surface, color: colors.textPrimary }}
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-lg font-semibold">
                {memberName ? `Invite ${memberName}` : "Invite"}
              </h3>
              <p className="mt-1 text-sm" style={{ color: colors.textSecondary }}>
                Code {draft.invite_code}
              </p>
              <div className="mx-auto mt-4 w-fit rounded-2xl bg-white p-4">
                <QRCode
                  value={draft.qr_payload || draft.invite_link}
                  size={200}
                  level="M"
                  bgColor="#FFFFFF"
                  fgColor="#111111"
                />
              </div>
              <button
                type="button"
                className="mt-4 w-full rounded-xl px-3 py-2.5 text-sm font-medium"
                style={{ background: colors.surfaceContainer }}
                onClick={() => void handleCopy()}
              >
                Copy link
              </button>
              <button
                type="button"
                className="mt-3 w-full text-sm font-medium"
                style={{ color: colors.textSecondary }}
                onClick={() => setShowQr(false)}
              >
                Close
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

type InviteButtonProps = {
  memberName?: string;
  method?: string;
  methods: SetupChoice[];
  onSelect: (method: string) => void;
  momentId?: string;
  localId?: string;
  memberEmail?: string | null;
  memberPhone?: string | null;
  onBeforeInvite?: () => Promise<boolean>;
  onEmailRequired?: () => void;
};

export function SetupInviteButton({
  memberName,
  method,
  methods,
  onSelect,
  momentId,
  localId,
  memberEmail,
  memberPhone,
  onBeforeInvite,
  onEmailRequired,
}: InviteButtonProps) {
  const { colors } = useThemeTokens();
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="rounded-lg px-3 py-1.5 text-xs font-semibold"
        style={{ background: colors.surfaceContainer }}
      >
        Invite
      </button>
      <SetupInviteSheet
        open={open}
        onClose={() => setOpen(false)}
        memberName={memberName}
        currentMethod={method}
        methods={methods}
        onSelect={onSelect}
        momentId={momentId}
        localId={localId}
        memberEmail={memberEmail}
        memberPhone={memberPhone}
        onBeforeInvite={onBeforeInvite}
        onEmailRequired={onEmailRequired}
      />
    </>
  );
}
