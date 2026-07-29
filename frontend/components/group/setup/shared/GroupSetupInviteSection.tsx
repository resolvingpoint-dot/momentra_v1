"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { glassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { InviteMethodsPanel } from "@/components/group/invite/InviteMethodsPanel";
import type { InviteDraft } from "@/lib/api/group";
import { GroupRepository } from "@/repositories/GroupRepository";

type Props = {
  momentId: string;
  title?: string;
  helper?: string;
};

/**
 * Shared Group setup invite panel — reused by Experience / Purchase / Living guided screens.
 * Do not duplicate invite fetch + channel UI in template screens.
 */
export function GroupSetupInviteSection({
  momentId,
  title = "Invite participants",
  helper = "Share a QR code or invite link — WhatsApp, Messages, and email are shortcuts.",
}: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const [draft, setDraft] = useState<InviteDraft | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setLoadError(null);
    void GroupRepository.getInviteDraft(momentId)
      .then((result) => {
        if (!cancelled) {
          setDraft(result);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setLoadError(err instanceof Error ? err.message : "Failed to load invite");
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [momentId]);

  return (
    <section className="rounded-2xl p-5" style={glassCardStyle(tokens)}>
      <h3 className="mb-1 text-base font-semibold">{title}</h3>
      <p className="mb-4 text-sm opacity-70" style={{ color: colors.textSecondary }}>
        {helper}
      </p>
      {loading ? (
        <div className="flex items-center gap-2 text-sm opacity-70">
          <Loader2 className="size-4 animate-spin" aria-hidden />
          Loading invite…
        </div>
      ) : null}
      {loadError ? (
        <p className="text-sm" style={{ color: colors.error }} role="alert">
          {loadError}
        </p>
      ) : null}
      {draft ? (
        <InviteMethodsPanel momentId={momentId} draft={draft} onDraftChange={setDraft} />
      ) : null}
    </section>
  );
}
