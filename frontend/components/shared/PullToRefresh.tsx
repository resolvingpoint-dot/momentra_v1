"use client";

import { useCallback, useRef, useState, type ReactNode } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

type PullToRefreshProps = {
  onRefresh: () => Promise<void> | void;
  children: ReactNode;
  className?: string;
  disabled?: boolean;
};

const THRESHOLD = 72;

export function PullToRefresh({ onRefresh, children, className = "", disabled = false }: PullToRefreshProps) {
  const tokens = useThemeTokens();
  const startY = useRef(0);
  const pulling = useRef(false);
  const [offset, setOffset] = useState(0);
  const [refreshing, setRefreshing] = useState(false);

  const onTouchStart = useCallback((e: React.TouchEvent) => {
    if (disabled || refreshing) return;
    const el = e.currentTarget as HTMLElement;
    if (el.scrollTop > 0) return;
    startY.current = e.touches[0]?.clientY ?? 0;
    pulling.current = true;
  }, [disabled, refreshing]);

  const onTouchMove = useCallback((e: React.TouchEvent) => {
    if (!pulling.current || disabled || refreshing) return;
    const dy = (e.touches[0]?.clientY ?? 0) - startY.current;
    if (dy > 0) setOffset(Math.min(dy * 0.45, THRESHOLD + 16));
  }, [disabled, refreshing]);

  const onTouchEnd = useCallback(async () => {
    if (!pulling.current || disabled) return;
    pulling.current = false;
    if (offset >= THRESHOLD && !refreshing) {
      setRefreshing(true);
      try {
        await onRefresh();
      } finally {
        setRefreshing(false);
      }
    }
    setOffset(0);
  }, [disabled, offset, onRefresh, refreshing]);

  return (
    <div
      className={`relative min-h-0 flex-1 overflow-y-auto ${className}`}
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={() => void onTouchEnd()}
    >
      <div
        className="pointer-events-none absolute inset-x-0 top-0 flex justify-center transition-opacity"
        style={{
          height: offset,
          opacity: offset > 8 ? 1 : 0,
          color: tokens.colors.brandPrimary,
        }}
        aria-hidden
      >
        <span className="mt-2 text-xs font-semibold">{refreshing ? "Refreshing…" : "Pull to refresh"}</span>
      </div>
      <div style={{ transform: offset ? `translateY(${offset}px)` : undefined, transition: pulling.current ? undefined : "transform 200ms ease-out" }}>
        {children}
      </div>
    </div>
  );
}
