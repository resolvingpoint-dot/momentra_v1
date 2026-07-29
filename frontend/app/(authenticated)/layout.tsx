import { OnboardingGate } from "@/components/onboarding/OnboardingGate";
import { SplashGate } from "@/components/SplashGate";

/**
 * Persistent gate stack for authenticated soft-nav targets.
 * Route group does not affect the URL; /app stays /app.
 * Splash + onboarding survive transitions among routes under this group.
 */
export default function AuthenticatedLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <SplashGate>
      <OnboardingGate>{children}</OnboardingGate>
    </SplashGate>
  );
}
