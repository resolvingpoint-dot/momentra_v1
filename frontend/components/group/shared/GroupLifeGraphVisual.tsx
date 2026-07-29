"use client";

import { useEffect, useMemo, useState, type ReactNode } from "react";
import { Network, TrendingUp } from "lucide-react";
import type { GroupLifeSatelliteScore } from "@/lib/api/groupLife";
import {
  GROUP_LIFE_DIMENSIONS,
  GROUP_LIFE_GRAPH_CENTER,
  GROUP_LIFE_HERO,
  GROUP_LIFE_MOTION,
} from "@/lib/group/groupLifeCopy";

type GroupLifeGraphVisualProps = {
  className?: string;
  lifeScore?: number;
  deltaMonth?: number | null;
  satelliteScores?: GroupLifeSatelliteScore[];
};

function pulseFactor(timeMs: number, delayMs: number): { opacity: number; scale: number } {
  const cycle = GROUP_LIFE_MOTION.nodePulseDurationMs;
  const progress = ((timeMs + delayMs) % cycle) / cycle;
  const factor = progress < 0.5 ? progress * 2 : (1 - progress) * 2;
  return { opacity: 1 - 0.4 * factor, scale: 1 - 0.05 * factor };
}

function hubPulseFactor(timeMs: number): number {
  const cycle = GROUP_LIFE_MOTION.nodePulseDurationMs;
  const progress = (timeMs % cycle) / cycle;
  const factor = progress < 0.5 ? progress * 2 : (1 - progress) * 2;
  return 1 + 0.06 * factor;
}

export function GroupLifeGraphVisual({
  className,
  lifeScore,
  deltaMonth,
  satelliteScores,
}: GroupLifeGraphVisualProps) {
  const { x: cx, y: cy } = GROUP_LIFE_GRAPH_CENTER;
  const [timeMs, setTimeMs] = useState(0);
  const isActive = lifeScore != null;

  const scoreByCode = useMemo(() => {
    const map = new Map<string, number>();
    for (const s of satelliteScores ?? []) {
      if (s.score != null) map.set(s.moment_type_code, s.score);
    }
    return map;
  }, [satelliteScores]);

  useEffect(() => {
    let frameId = 0;
    const start = performance.now();
    const tick = (now: number) => {
      setTimeMs(now - start);
      frameId = requestAnimationFrame(tick);
    };
    frameId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frameId);
  }, []);

  const dashOffset = -((timeMs / GROUP_LIFE_MOTION.particleLineDurationMs) * 100) % 100;
  const hubScale = isActive ? 1 : hubPulseFactor(timeMs);

  return (
    <div className={className ?? "relative size-full"}>
      <svg
        className="absolute inset-0 size-full"
        viewBox="0 0 400 400"
        preserveAspectRatio="xMidYMid meet"
        aria-hidden
      >
        {isActive ? (
          <>
            <defs>
              <radialGradient id="groupLifeHeroGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#ff7a3d" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#ff7a3d" stopOpacity={0} />
              </radialGradient>
            </defs>
            <circle cx={cx} cy={cy} r={160} fill="url(#groupLifeHeroGlow)" />
            <polygon
              fill="rgba(255,122,61,0.12)"
              stroke="#ff7a3d"
              strokeWidth={2}
              points={`${cx},${cy - 68} ${cx + 70},${cy - 18} ${cx + 44},${cy + 55} ${cx - 40},${cy + 50} ${cx - 60},${cy - 10}`}
            />
          </>
        ) : null}
        <g opacity={isActive ? 0.35 : 0.2}>
          {GROUP_LIFE_DIMENSIONS.map((node) => (
            <line
              key={`line-${node.code}`}
              x1={cx}
              y1={cy}
              x2={node.graphX}
              y2={node.graphY}
              stroke={node.accent}
              strokeWidth={1.5}
              strokeDasharray="4 4"
              strokeDashoffset={dashOffset}
            />
          ))}
        </g>
        {GROUP_LIFE_DIMENSIONS.map((node) => {
          const pulse = isActive ? { opacity: 1, scale: 1 } : pulseFactor(timeMs, node.pulseDelayMs);
          const score = scoreByCode.get(node.code);
          return (
            <g
              key={`node-${node.code}`}
              transform={`translate(${node.graphX} ${node.graphY}) scale(${pulse.scale}) translate(${-node.graphX} ${-node.graphY})`}
              opacity={pulse.opacity}
            >
              {isActive ? (
                <circle cx={node.graphX} cy={node.graphY} r={4} fill={node.accent} />
              ) : (
                <circle
                  cx={node.graphX}
                  cy={node.graphY}
                  r={12}
                  fill="none"
                  stroke={node.accent}
                  strokeWidth={2}
                />
              )}
            </g>
          );
        })}
      </svg>

      {isActive ? (
        <>
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
            <span className="text-5xl font-extrabold text-white">{lifeScore}</span>
            <span className="text-[10px] font-bold uppercase tracking-[0.3em] text-[#ff7a3d]">
              Health Score
            </span>
            {deltaMonth != null ? (
              <div className="mt-2 flex items-center gap-1 text-xs font-bold text-emerald-400">
                <TrendingUp className="size-3.5" />
                +{deltaMonth} this month
              </div>
            ) : null}
          </div>
          {GROUP_LIFE_DIMENSIONS.map((node) => {
            const score = scoreByCode.get(node.code);
            if (score == null) return null;
            const left = `${(node.graphX / 400) * 100}%`;
            const top = `${(node.graphY / 400) * 100}%`;
            return (
              <div
                key={`label-${node.code}`}
                className="pointer-events-none absolute flex -translate-x-1/2 -translate-y-1/2 flex-col items-center text-[10px] font-bold uppercase tracking-widest"
                style={{ left, top, color: node.accent }}
              >
                <span>{node.shortTitle}</span>
                <span className="text-lg">{score}</span>
              </div>
            );
          })}
        </>
      ) : (
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <div
            className="mb-3 flex size-20 items-center justify-center rounded-full border border-violet-500/30"
            style={{
              background: "rgba(255, 255, 255, 0.05)",
              backdropFilter: "blur(20px)",
              boxShadow: GROUP_LIFE_HERO.hubShadow,
              transform: `scale(${hubScale})`,
            }}
          >
            <Network className="size-10 text-violet-400" strokeWidth={1.5} />
          </div>
          <p className="text-sm font-bold uppercase tracking-[0.2em] text-violet-300">Group Life</p>
          <p className="mt-1 text-[10px] uppercase tracking-widest text-[#DFC0B4]/60">
            Status: Inactive
          </p>
        </div>
      )}
    </div>
  );
}

export function GroupLifeHeroSection({ children }: { children: ReactNode }) {
  return (
    <section className="relative flex h-[max(40vh,350px)] w-full flex-col items-center justify-center overflow-hidden px-6 pt-4">
      <div
        className="pointer-events-none absolute inset-0 -z-10 bg-gradient-to-b from-violet-500/5 to-transparent"
        style={{
          boxShadow: GROUP_LIFE_HERO.glowShadow,
        }}
      />
      <div className="relative mx-auto flex h-full w-full max-w-md items-center justify-center">
        <div className="relative aspect-square h-full max-h-[384px] w-full max-w-[384px]">
          {children}
        </div>
      </div>
    </section>
  );
}
