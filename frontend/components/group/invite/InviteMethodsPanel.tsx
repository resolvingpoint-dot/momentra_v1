"use client";

import { useCallback, useState } from "react";
import {
  Copy,
  Loader2,
  Mail,
  MessageCircle,
  QrCode,
  RefreshCw,
  Share2,
} from "lucide-react";
import QRCode from "react-qr-code";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { InviteDraft } from "@/lib/api/group";
import {
  createEmailInvite,
  recordInviteChannel,
  refreshInviteDraft,
} from "@/lib/api/group";

type InviteMethodsPanelProps = {
  momentId: string;
  draft: InviteDraft;
  onDraftChange: (draft: InviteDraft) => void;
  /** Prefill for email send / mailto */
  defaultEmail?: string | null;
  /** Prefill SMS recipient */
  defaultPhone?: string | null;
  className?: string;
};

function WhatsAppGlyph({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.435 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
    </svg>
  );
}

export function InviteQrModal({
  draft,
  open,
  onClose,
  onRefresh,
  refreshing,
}: {
  draft: InviteDraft;
  open: boolean;
  onClose: () => void;
  onRefresh: () => void;
  refreshing?: boolean;
}) {
  const { colors } = useThemeTokens();
  const [copied, setCopied] = useState<"link" | "code" | null>(null);

  if (!open) return null;

  async function copy(kind: "link" | "code") {
    const text = kind === "code" ? draft.invite_code : draft.invite_link;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(kind);
      window.setTimeout(() => setCopied(null), 1800);
    } catch {
      /* ignore */
    }
  }

  const expiry = draft.expires_at
    ? new Date(draft.expires_at).toLocaleString(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
      })
    : null;

  return (
    <div
      className="fixed inset-0 z-[80] flex items-end justify-center bg-black/45 p-4 sm:items-center"
      role="dialog"
      aria-modal
      aria-labelledby="invite-qr-title"
      onClick={onClose}
    >
      <div
        className="w-full max-w-sm rounded-3xl p-5 shadow-xl"
        style={{ background: colors.surface, color: colors.textPrimary }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 id="invite-qr-title" className="text-lg font-semibold">
          {draft.experience_name || "Invite"}
        </h3>
        <p className="mt-1 text-sm" style={{ color: colors.textSecondary }}>
          Code {draft.invite_code}
          {expiry ? ` · Expires ${expiry}` : null}
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

        <div className="mt-4 grid grid-cols-2 gap-2">
          <button
            type="button"
            className="rounded-xl px-3 py-2.5 text-sm font-medium"
            style={{ background: colors.surfaceContainer }}
            onClick={() => void copy("code")}
          >
            {copied === "code" ? "Copied code" : "Copy code"}
          </button>
          <button
            type="button"
            className="rounded-xl px-3 py-2.5 text-sm font-medium"
            style={{ background: colors.surfaceContainer }}
            onClick={() => void copy("link")}
          >
            {copied === "link" ? "Copied link" : "Copy link"}
          </button>
        </div>

        <button
          type="button"
          className="mt-2 flex w-full items-center justify-center gap-2 rounded-xl px-3 py-2.5 text-sm font-medium"
          style={{ background: colors.surfaceContainer }}
          disabled={refreshing}
          onClick={onRefresh}
        >
          {refreshing ? <Loader2 className="size-4 animate-spin" /> : <RefreshCw className="size-4" />}
          Refresh link
        </button>

        <button
          type="button"
          className="mt-3 w-full text-sm font-medium"
          style={{ color: colors.textSecondary }}
          onClick={onClose}
        >
          Close
        </button>
      </div>
    </div>
  );
}

export function InviteMethodsPanel({
  momentId,
  draft,
  onDraftChange,
  defaultEmail,
  defaultPhone,
  className,
}: InviteMethodsPanelProps) {
  const { colors } = useThemeTokens();
  const [showQr, setShowQr] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const track = useCallback(
    async (channel: string) => {
      try {
        await recordInviteChannel(momentId, channel, {
          inviteId: draft.invite_id,
          participantId: draft.participant_id,
        });
      } catch {
        /* non-blocking */
      }
    },
    [momentId, draft.invite_id, draft.participant_id],
  );

  async function handleShare() {
    setBusy("share");
    setStatus(null);
    const text = draft.whatsapp_text || draft.invite_link;
    try {
      if (typeof navigator !== "undefined" && typeof navigator.share === "function") {
        await navigator.share({
          title: draft.experience_name || "Momentra invite",
          text,
          url: draft.invite_link,
        });
        await track("share");
      } else {
        await navigator.clipboard.writeText(draft.invite_link);
        setStatus("Link copied — share it from your apps.");
        await track("copy");
      }
    } catch (err) {
      if ((err as Error)?.name !== "AbortError") {
        setStatus("Could not open share sheet");
      }
    } finally {
      setBusy(null);
    }
  }

  async function handleCopy() {
    setBusy("copy");
    try {
      await navigator.clipboard.writeText(draft.invite_link);
      setStatus("Invite link copied");
      await track("copy");
    } catch {
      setStatus("Could not copy link");
    } finally {
      setBusy(null);
    }
  }

  function handleWhatsApp() {
    const text = draft.whatsapp_text || draft.invite_link;
    void track("whatsapp");
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, "_blank", "noopener,noreferrer");
  }

  function handleSms() {
    const body = draft.sms_text || draft.whatsapp_text || draft.invite_link;
    const phone = (defaultPhone || "").replace(/[^\d+]/g, "");
    void track("sms");
    const href = phone
      ? `sms:${phone}?&body=${encodeURIComponent(body)}`
      : `sms:?&body=${encodeURIComponent(body)}`;
    window.location.href = href;
  }

  async function handleEmail() {
    setBusy("email");
    setStatus(null);
    const email =
      defaultEmail?.trim() ||
      window.prompt("Invite email address")?.trim() ||
      "";
    if (!email) {
      setBusy(null);
      return;
    }
    try {
      const result = await createEmailInvite(momentId, email, draft.participant_id);
      await track("email");
      if (result.sent) {
        setStatus(`Invite sent to ${result.invitee_email}`);
      } else {
        const mailto = `mailto:${encodeURIComponent(email)}?subject=${encodeURIComponent(
          result.email_subject || draft.email_subject,
        )}&body=${encodeURIComponent(result.email_body || draft.email_body)}`;
        window.location.href = mailto;
        setStatus(
          result.send_error
            ? `Opened mail app (${result.send_error})`
            : "Opened mail app with invite",
        );
      }
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Email invite failed");
    } finally {
      setBusy(null);
    }
  }

  async function handleRefresh() {
    setRefreshing(true);
    try {
      const next = await refreshInviteDraft(momentId, draft.participant_id);
      onDraftChange(next);
      setStatus("Invite link refreshed");
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Could not refresh");
    } finally {
      setRefreshing(false);
    }
  }

  const primaryBtn = {
    background: colors.primaryContainer,
    color: colors.brandOnPrimary,
  } as const;
  const secondaryBtn = {
    background: colors.surfaceContainer,
    color: colors.textPrimary,
  } as const;

  return (
    <div className={className ?? "space-y-4"}>
      <div className="grid grid-cols-2 gap-3">
        <button
          type="button"
          className="inline-flex items-center justify-center gap-2 rounded-2xl px-4 py-3.5 text-sm font-semibold"
          style={primaryBtn}
          onClick={() => {
            void track("qr");
            setShowQr(true);
          }}
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
          {busy === "share" ? <Loader2 className="size-5 animate-spin" /> : <Share2 className="size-5" />}
          Share Invite
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
            },
            {
              id: "sms",
              label: "Message",
              icon: <MessageCircle className="size-5" />,
              onClick: handleSms,
            },
            {
              id: "email",
              label: "Email",
              icon: busy === "email" ? <Loader2 className="size-5 animate-spin" /> : <Mail className="size-5" />,
              onClick: () => void handleEmail(),
            },
            {
              id: "copy",
              label: "Copy Link",
              icon: busy === "copy" ? <Loader2 className="size-5 animate-spin" /> : <Copy className="size-5" />,
              onClick: () => void handleCopy(),
            },
          ] as const
        ).map((item) => (
          <button
            key={item.id}
            type="button"
            className="flex flex-col items-center gap-1.5 rounded-xl px-1 py-3 text-[11px] font-medium"
            style={secondaryBtn}
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

      <InviteQrModal
        draft={draft}
        open={showQr}
        onClose={() => setShowQr(false)}
        onRefresh={() => void handleRefresh()}
        refreshing={refreshing}
      />
    </div>
  );
}
