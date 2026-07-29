"use client";

import { useEffect, useState } from "react";
import { BUSINESS_LIFE_EMPTY_COPY } from "@/lib/business/businessLifeEmptyCopy";

const GLOW_CYCLE_MS = 4000;
const BREATHE_CYCLE_MS = 4000;

function glowOpacity(timeMs: number): number {
  const progress = (timeMs % GLOW_CYCLE_MS) / GLOW_CYCLE_MS;
  const factor = progress < 0.5 ? progress * 2 : (1 - progress) * 2;
  return 0.12 + 0.08 * factor;
}

function breatheScale(timeMs: number): number {
  const progress = (timeMs % BREATHE_CYCLE_MS) / BREATHE_CYCLE_MS;
  const factor = progress < 0.5 ? progress * 2 : (1 - progress) * 2;
  return 1 + 0.02 * factor;
}

export function BusinessLifeHeroVisual() {
  const [timeMs, setTimeMs] = useState(0);
  const { heroImage } = BUSINESS_LIFE_EMPTY_COPY.hero;

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

  const glow = glowOpacity(timeMs);
  const scale = breatheScale(timeMs);

  return (
    <div className="relative mx-auto aspect-square w-full max-h-[340px]">
      <div
        className="pointer-events-none absolute inset-0 rounded-2xl"
        style={{
          background: `radial-gradient(circle at 50% 50%, rgba(109, 93, 252, ${glow}) 0%, rgba(13, 20, 29, 0) 70%)`,
        }}
      />
      <div
        className="relative size-full overflow-hidden rounded-2xl shadow-lg"
        style={{ transform: `scale(${scale})`, transition: "transform 0.1s linear" }}
      >
        <img
          src={heroImage}
          alt="Business Life orbital hub"
          className="size-full object-cover"
        />
      </div>
    </div>
  );
}
