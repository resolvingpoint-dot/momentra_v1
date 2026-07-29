"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/components/auth/AuthProvider";
import { LoginScreen } from "@/components/auth/LoginScreen";
import { MomentraAppShell } from "@/components/MomentraAppShell";
import { HomeShell } from "@/components/home/HomeShell";
import { AppContextProvider } from "@/components/theme/AppContextProvider";
import { BootstrapGate } from "@/components/shell/BootstrapGate";
import { MomentraAnalytics } from "@/lib/analytics";
import { markShellPaint } from "@/lib/telemetry/performanceTelemetry";

const RESTORE_ESCAPE_MS = 12_000;

export function AuthGate({ children: _children }: { children: React.ReactNode }) {
  const { user, isRestoring, clearSessionAndShowLogin } = useAuth();
  const [showRestoreEscape, setShowRestoreEscape] = useState(false);

  useEffect(() => {
    if (isRestoring) {
      void MomentraAnalytics.logScreen("auth_restore");
    } else if (!user) {
      void MomentraAnalytics.logScreen("login");
    }
  }, [isRestoring, user]);

  useEffect(() => {
    if (!isRestoring) {
      setShowRestoreEscape(false);
      return;
    }
    const timer = window.setTimeout(() => setShowRestoreEscape(true), RESTORE_ESCAPE_MS);
    return () => window.clearTimeout(timer);
  }, [isRestoring]);

  useEffect(() => {
    if (user) markShellPaint();
  }, [user]);

  // Paint shell from disk when tokens + cached user exist; validate /me in background.
  if (isRestoring && !user) {
    return (
      <div className="auth-screen flex min-h-dvh flex-col items-center justify-center gap-4 px-6 text-center">
        <Loader2 className="size-8 animate-spin opacity-80" aria-hidden />
        <p className="text-sm opacity-90">Restoring session…</p>
        {showRestoreEscape ? (
          <button
            type="button"
            onClick={clearSessionAndShowLogin}
            className="btn-ghost-on-dark mt-2 text-sm"
          >
            Continue to sign in
          </button>
        ) : null}
      </div>
    );
  }

  if (!user) {
    return <LoginScreen />;
  }

  return (
    <div className="flex min-h-dvh flex-1 flex-col">
      <BootstrapGate>
        <AppContextProvider>
          <MomentraAppShell>
            {(context) => <HomeShell context={context} />}
          </MomentraAppShell>
        </AppContextProvider>
      </BootstrapGate>
    </div>
  );
}
