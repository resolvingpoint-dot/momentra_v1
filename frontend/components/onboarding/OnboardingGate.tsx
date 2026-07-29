"use client";

import { useCallback, useEffect, useState } from "react";
import { OnboardingScreen } from "@/components/onboarding/OnboardingScreen";
import { hasStoredSession } from "@/lib/auth/tokens";
import {
  markOnboardingSeen,
  shouldSkipOnboarding,
} from "@/lib/auth/onboardingSession";

function shouldShowOnboardingOnMount(): boolean {
  if (typeof window === "undefined") return false;
  if (hasStoredSession()) return false;
  return !shouldSkipOnboarding();
}

export function OnboardingGate({ children }: { children: React.ReactNode }) {
  // Hydration-safe: false until mount
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setShowOnboarding(shouldShowOnboardingOnMount());
    setReady(true);
  }, []);

  const handleFinished = useCallback(() => {
    markOnboardingSeen();
    setShowOnboarding(false);
  }, []);

  return (
    <>
      {children}
      {ready && showOnboarding ? (
        <OnboardingScreen
          mode="firstRun"
          overlayClassName="z-40"
          onFinished={handleFinished}
        />
      ) : null}
    </>
  );
}
