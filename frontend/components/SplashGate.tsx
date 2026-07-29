"use client";

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { useAuth } from "@/components/auth/AuthProvider";
import { hasStoredSession } from "@/lib/auth/tokens";
import { markSplashSeen, shouldSkipSplash } from "@/lib/auth/splashSession";
import { SplashScreen } from "./SplashScreen";

const SPLASH_FAILSAFE_MS = 4500;
const RETURNING_SESSION_FAILSAFE_MS = 1200;

export function SplashGate({ children }: { children: React.ReactNode }) {
  const { isRestoring } = useAuth();
  const hadSessionOnMount = useRef(false);
  const dismissedRef = useRef(false);
  // SSR-safe: true on first paint (matches server). Skip/dismiss before browser paint
  // via useLayoutEffect so remounts with sessionStorage do not flash a blank brand shell.
  const [showSplash, setShowSplash] = useState(true);
  const [fadeOut, setFadeOut] = useState(false);
  const [animationDone, setAnimationDone] = useState(false);
  const [gateReady, setGateReady] = useState(false);

  const dismissSplash = useCallback(() => {
    if (dismissedRef.current) return;
    dismissedRef.current = true;
    markSplashSeen();
    setFadeOut(true);
    window.setTimeout(() => setShowSplash(false), 300);
  }, []);

  useLayoutEffect(() => {
    hadSessionOnMount.current = hasStoredSession();
    // Skip overlay before paint when already seen this session OR a stored auth
    // session exists. Returning users otherwise sit on a blank brand canvas while
    // the splash wordmark animates in (~1s) or while restore hangs.
    if (shouldSkipSplash() || hadSessionOnMount.current) {
      dismissedRef.current = true;
      setShowSplash(false);
      setFadeOut(false);
      markSplashSeen();
    }
    setGateReady(true);
  }, []);

  const handleAnimationFinish = useCallback(() => {
    setAnimationDone(true);
  }, []);

  useEffect(() => {
    if (!gateReady || !showSplash || dismissedRef.current) return;

    // Returning session: dismiss as soon as restore settles — do not wait on mark animation
    // (animation leaves a blank brand canvas for ~1s before wordmark appears).
    if (hadSessionOnMount.current) {
      if (!isRestoring) {
        dismissSplash();
      }
      return;
    }

    if (animationDone) {
      dismissSplash();
    }
  }, [animationDone, dismissSplash, gateReady, isRestoring, showSplash]);

  // Returning-session failsafe: never leave a blank indigo shell while restore hangs.
  useEffect(() => {
    if (!gateReady || !showSplash || dismissedRef.current) return;
    if (!hadSessionOnMount.current) return;
    const t = window.setTimeout(() => dismissSplash(), RETURNING_SESSION_FAILSAFE_MS);
    return () => window.clearTimeout(t);
  }, [dismissSplash, gateReady, showSplash]);

  // Cold-launch failsafe.
  useEffect(() => {
    if (!gateReady || !showSplash || dismissedRef.current) return;
    if (hadSessionOnMount.current) return;
    const t = window.setTimeout(() => dismissSplash(), SPLASH_FAILSAFE_MS);
    return () => window.clearTimeout(t);
  }, [dismissSplash, gateReady, showSplash]);

  return (
    <>
      {children}
      {showSplash ? (
        <div
          className="fixed inset-0 z-50 min-h-screen h-screen transition-opacity duration-300"
          style={{ opacity: fadeOut ? 0 : 1 }}
        >
          <SplashScreen onFinish={handleAnimationFinish} />
        </div>
      ) : null}
    </>
  );
}
