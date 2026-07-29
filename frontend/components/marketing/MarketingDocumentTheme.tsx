"use client";

import { useEffect } from "react";

/** Applies brand-dark html/body while marketing is mounted; restores product light theme on leave. */
export function MarketingDocumentTheme({
  children,
}: {
  children: React.ReactNode;
}) {
  useEffect(() => {
    const root = document.documentElement;
    root.classList.add("marketing-active");
    return () => {
      root.classList.remove("marketing-active");
    };
  }, []);

  return <div className="marketing-root">{children}</div>;
}
