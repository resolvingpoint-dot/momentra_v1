"use client";

import { type ReactNode, useEffect, useMemo } from "react";
import { useBootstrapStore } from "@/hooks/useBootstrap";
import {
  syncContextFromBootstrap,
  wireContextStoreToBootstrap,
} from "@/stores/contextStore";

function BootstrapSkeleton() {
  return (
    <div className="auth-screen flex min-h-dvh flex-col bg-[#14121b] px-6 py-10">
      <div className="mx-auto w-full max-w-md space-y-4">
        <div className="h-8 w-40 rounded bg-[#2a2a2a] momentra-bootstrap-shimmer" />
        <div className="h-4 w-56 rounded bg-[#2a2a2a] momentra-bootstrap-shimmer" />
        <div className="mt-8 grid grid-cols-2 gap-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-24 rounded-2xl bg-[#1e1e1e] momentra-bootstrap-shimmer" />
          ))}
        </div>
      </div>
      <style>{`
        @keyframes momentraBootstrapShimmer {
          0%, 100% { opacity: 0.45; }
          50% { opacity: 0.85; }
        }
        .momentra-bootstrap-shimmer {
          animation: momentraBootstrapShimmer 1000ms ease-in-out infinite;
        }
        @media (prefers-reduced-motion: reduce) {
          .momentra-bootstrap-shimmer { animation: none; opacity: 0.6; }
        }
      `}</style>
    </div>
  );
}

function BootstrapError({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <div className="auth-screen flex min-h-dvh flex-col items-center justify-center gap-4 p-6 text-center">
      <p className="max-w-sm text-sm opacity-90">{message}</p>
      <button
        type="button"
        onClick={onRetry}
        className="btn-celebrate px-4 py-2 text-sm font-semibold"
      >
        Retry
      </button>
    </div>
  );
}

export function BootstrapGate({ children }: { children: ReactNode }) {
  const { data, isLoading, isRefreshing, error, hasLoadedOnce, loadBootstrap } =
    useBootstrapStore();

  useEffect(() => {
    void loadBootstrap().catch(() => {
      // Errors surface via bootstrap snapshot (error + retry UI).
    });
    // Ownership model: no continuous bootstrap→context subscription.
    return wireContextStoreToBootstrap();
  }, [loadBootstrap]);

  const bootstrapVersions = useMemo(
    () =>
      data
        ? {
            reference_data_version: data.reference_data_version,
            template_version: data.template_version,
            ui_schema_version: data.ui_schema_version,
            quick_add_version: data.quick_add_version,
            setup_version: data.setup_version,
            metadata_version: data.metadata_version,
          }
        : null,
    [
      data?.reference_data_version,
      data?.template_version,
      data?.ui_schema_version,
      data?.quick_add_version,
      data?.setup_version,
      data?.metadata_version,
    ],
  );

  useEffect(() => {
    if (!bootstrapVersions) return;
    void import("@/lib/reference_data/referenceDataStore").then(({ ensureReferenceDataForBootstrap }) =>
      ensureReferenceDataForBootstrap(bootstrapVersions),
    );
  }, [bootstrapVersions]);

  useEffect(() => {
    if (!data || isRefreshing) return;
    // Hydrate shell context once from bootstrap prefs; after that context is client-owned.
    syncContextFromBootstrap();
  }, [data, isRefreshing]);

  if (!data && error) {
    return (
      <BootstrapError
        message={error}
        onRetry={() => void loadBootstrap({ force: true })}
      />
    );
  }

  if (!hasLoadedOnce && (isLoading || !data)) {
    return <BootstrapSkeleton />;
  }

  return <>{children}</>;
}
