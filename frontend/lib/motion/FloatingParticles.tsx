"use client";

import { useMemo } from "react";
import { MOTION_DURATION_S } from "./tokens";
import { useReducedMotion } from "./useReducedMotion";

type FloatingParticlesProps = {
  /** 0–1 density multiplier; Memory uses higher than PersonalLife */
  density?: number;
  className?: string;
  color?: string;
};

type Particle = {
  id: number;
  left: string;
  top: string;
  size: number;
  duration: number;
  delay: number;
};

function seededParticles(count: number): Particle[] {
  const out: Particle[] = [];
  for (let i = 0; i < count; i += 1) {
    const t = (i + 1) * 0.6180339887;
    out.push({
      id: i,
      left: `${((t * 37) % 1) * 100}%`,
      top: `${((t * 53) % 1) * 100}%`,
      size: 2 + (i % 3),
      duration: MOTION_DURATION_S.orbLoop * (0.12 + (i % 5) * 0.02),
      delay: (i % 8) * 0.15,
    });
  }
  return out;
}

export function FloatingParticles({ density = 1, className = "", color }: FloatingParticlesProps) {
  const reducedMotion = useReducedMotion();
  const particles = useMemo(() => seededParticles(Math.round(12 * density)), [density]);

  if (reducedMotion) return null;

  return (
    <div
      className={`pointer-events-none absolute inset-0 overflow-hidden ${className}`}
      aria-hidden
      style={color ? ({ ["--particle-color" as string]: color } as React.CSSProperties) : undefined}
    >
      <style>{`
        @keyframes momentraParticleFloat {
          0%, 100% { transform: translate(0, 0); opacity: 0.35; }
          50% { transform: translate(6px, -12px); opacity: 0.75; }
        }
      `}</style>
      {particles.map((p) => (
        <span
          key={p.id}
          className="absolute rounded-full bg-[var(--particle-color,rgba(147,130,255,0.5))]"
          style={{
            left: p.left,
            top: p.top,
            width: p.size,
            height: p.size,
            animation: `momentraParticleFloat ${p.duration}s ease-in-out ${p.delay}s infinite`,
          }}
        />
      ))}
    </div>
  );
}
