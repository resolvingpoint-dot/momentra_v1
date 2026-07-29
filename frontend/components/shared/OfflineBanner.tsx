"use client";

import { useEffect, useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

type OfflineBannerProps = {
  /** Show when stale cache is displayed while offline or fetch failed */
  visible: boolean;
  message?: string;
};

export function OfflineBanner({ visible, message = "Offline — showing saved data" }: OfflineBannerProps) {
  const tokens = useThemeTokens();
  const [online, setOnline] = useState(true);

  useEffect(() => {
    const update = () => setOnline(navigator.onLine);
    update();
    window.addEventListener("online", update);
    window.addEventListener("offline", update);
    return () => {
      window.removeEventListener("online", update);
      window.removeEventListener("offline", update);
    };
  }, []);

  if (!visible || online) return null;

  return (
    <div
      role="status"
      className="sticky top-0 z-20 px-4 py-2 text-center text-xs font-semibold"
      style={{
        background: `${tokens.colors.brandPrimary}22`,
        color: tokens.colors.brandPrimary,
        borderBottom: `1px solid ${tokens.colors.brandPrimary}33`,
      }}
    >
      {message}
    </div>
  );
}
