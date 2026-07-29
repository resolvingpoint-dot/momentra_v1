"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/components/auth/AuthProvider";
import { acceptInvite } from "@/lib/api/group";
import { extractInviteToken } from "@/lib/invite/inviteToken";
import {
  stashInviteJoinedResult,
  stashPendingInvite,
} from "@/lib/invite/pendingInvite";
import { MomentraAnalytics } from "@/lib/analytics";

export default function InviteTokenPage() {
  const params = useParams<{ token: string }>();
  const router = useRouter();
  const { user, isRestoring } = useAuth();
  const [status, setStatus] = useState("Opening invite…");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isRestoring) return;

    const raw = typeof params.token === "string" ? params.token : "";
    const decoded = (() => {
      try {
        return decodeURIComponent(raw);
      } catch {
        return raw;
      }
    })();
    const token = extractInviteToken(decoded) ?? extractInviteToken(raw);
    if (!token) {
      setError("This invite link is invalid.");
      setStatus("");
      return;
    }

    if (!user) {
      stashPendingInvite(token);
      setStatus("Sign in to join…");
      router.replace("/app");
      return;
    }

    let cancelled = false;
    void (async () => {
      setStatus("Joining…");
      setError(null);
      try {
        void MomentraAnalytics.logCustomEvent("invite_deep_link_open", { source: "web_route" });
        const result = await acceptInvite(token);
        if (cancelled) return;
        void MomentraAnalytics.logCustomEvent("invite_accept_success", {
          already_member: Boolean(result.already_member),
        });
        stashInviteJoinedResult(result);
        setStatus(
          result.already_member
            ? `Already a member of ${result.moment_name}`
            : `Joined ${result.moment_name}`,
        );
        router.replace("/app");
      } catch (err) {
        if (cancelled) return;
        void MomentraAnalytics.logCustomEvent("invite_accept_failed");
        setError(err instanceof Error ? err.message : "Could not accept invite");
        setStatus("");
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [isRestoring, user, params.token, router]);

  return (
    <div className="flex min-h-dvh flex-col items-center justify-center gap-3 bg-[#0c0c0e] px-6 text-center text-white">
      {!error ? <Loader2 className="size-8 animate-spin opacity-80" aria-hidden /> : null}
      {status ? <p className="text-sm opacity-90">{status}</p> : null}
      {error ? (
        <>
          <p className="text-sm text-red-300">{error}</p>
          <button
            type="button"
            className="mt-2 text-sm underline opacity-80"
            onClick={() => router.replace("/app")}
          >
            Go to Momentra
          </button>
        </>
      ) : null}
    </div>
  );
}
