"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { MomentraAnalytics } from "@/lib/analytics";
import { markOnboardingSeen } from "@/lib/auth/onboardingSession";
import styles from "./OnboardingScreen.module.css";

export type OnboardingMode = "firstRun" | "replay";

type OnboardingScreenProps = {
  mode?: OnboardingMode;
  onFinished: () => void;
  /** Overlay stacking — keep below splash (z-50) for first-run; above shell for replay. */
  overlayClassName?: string;
};

const SCENE_IDS = ["onboarding_1", "onboarding_2", "onboarding_3"] as const;

const COPY = {
  scene1: "Life is already unfolding.",
  scene2: "Keep what matters together.",
  brand: "Momentra",
  subtitle: "One place for every moment.",
  cta: "Step Inside",
} as const;

const BG = "#050816";
const PARTICLE_COUNT = 80;
const SCENE1_END = 2000;
const SCENE2_END = 5000;
const SCENE3_END = 7000;
const CTA_AT = 7200;

type Particle = {
  x: number;
  y: number;
  z: number;
  vx: number;
  vy: number;
  ox: number;
  oy: number;
  tx: number;
  ty: number;
  r: number;
  opacity: number;
};

/** Sample points along the Momentra M silhouette (viewBox-like 0–120). */
function sampleMTargets(count: number, w: number, h: number): { x: number; y: number }[] {
  const path: [number, number][] = [
    [14, 100],
    [14, 50],
    [34, 74],
    [54, 24],
    [54, 100],
    [54, 24],
    [74, 74],
    [94, 50],
    [94, 100],
  ];
  const scale = Math.min(w, h) * 0.42;
  const cx = w * 0.5;
  const cy = h * 0.38;
  const out: { x: number; y: number }[] = [];
  for (let i = 0; i < count; i++) {
    const t = (i / count) * (path.length - 1);
    const i0 = Math.floor(t);
    const i1 = Math.min(i0 + 1, path.length - 1);
    const f = t - i0;
    const x = path[i0][0] + (path[i1][0] - path[i0][0]) * f;
    const y = path[i0][1] + (path[i1][1] - path[i0][1]) * f;
    out.push({
      x: cx + ((x - 54) / 120) * scale * 2.2,
      y: cy + ((y - 62) / 120) * scale * 2.0,
    });
  }
  return out;
}

function createParticles(w: number, h: number): Particle[] {
  const targets = sampleMTargets(PARTICLE_COUNT, w, h);
  return Array.from({ length: PARTICLE_COUNT }, (_, i) => {
    const x = Math.random() * w;
    const y = Math.random() * h;
    const z = 0.4 + Math.random() * 0.6;
    return {
      x,
      y,
      z,
      vx: (Math.random() - 0.5) * 0.15,
      vy: (Math.random() - 0.5) * 0.15,
      ox: x,
      oy: y,
      tx: targets[i].x,
      ty: targets[i].y,
      r: 1.2 + Math.random() * 2.2,
      opacity: 0.25 + Math.random() * 0.55,
    };
  });
}

function sceneIndexAt(ms: number): 0 | 1 | 2 {
  if (ms < SCENE1_END) return 0;
  if (ms < SCENE2_END) return 1;
  return 2;
}

function easeInOut(t: number): number {
  return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
}

export function OnboardingScreen({
  mode = "firstRun",
  onFinished,
  overlayClassName = "z-[60]",
}: OnboardingScreenProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const startRef = useRef<number | null>(null);
  const exitingRef = useRef(false);
  const exitStartRef = useRef<number | null>(null);
  const lightRef = useRef(0);
  const lastSceneRef = useRef(-1);
  const ctaShownRef = useRef(false);
  const finishedRef = useRef(false);
  const rafRef = useRef<number>(0);
  const sizeRef = useRef({ w: 0, h: 0 });

  const [scene, setScene] = useState<0 | 1 | 2>(0);
  const [showCta, setShowCta] = useState(false);
  const [exiting, setExiting] = useState(false);
  const [reduceMotion, setReduceMotion] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduceMotion(mq.matches);
    const onChange = () => setReduceMotion(mq.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  useEffect(() => {
    void MomentraAnalytics.logScreen(SCENE_IDS[scene]);
  }, [scene]);

  const finish = useCallback(
    (reason: "skip" | "complete") => {
      if (finishedRef.current) return;
      finishedRef.current = true;
      if (mode === "firstRun") {
        markOnboardingSeen();
      }
      if (reason === "skip") {
        void MomentraAnalytics.logCustomEvent("onboarding_skip", {
          page: SCENE_IDS[lastSceneRef.current >= 0 ? lastSceneRef.current : scene],
          mode,
        });
      } else {
        void MomentraAnalytics.logCustomEvent("onboarding_complete", { mode });
      }
      onFinished();
    },
    [mode, onFinished, scene],
  );

  const beginExit = useCallback(() => {
    if (exitingRef.current) return;
    exitingRef.current = true;
    exitStartRef.current = performance.now();
    setExiting(true);
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const w = window.innerWidth;
      const h = window.innerHeight;
      sizeRef.current = { w, h };
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
      canvas.style.width = `${w}px`;
      canvas.style.height = `${h}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      particlesRef.current = createParticles(w, h);
      if (reduceMotion) {
        for (const p of particlesRef.current) {
          p.x = p.tx;
          p.y = p.ty;
        }
      }
    };

    resize();
    window.addEventListener("resize", resize);
    startRef.current = performance.now();

    if (reduceMotion) {
      setScene(2);
      setShowCta(true);
      ctaShownRef.current = true;
      lastSceneRef.current = 2;
    }

    const draw = (now: number) => {
      const { w, h } = sizeRef.current;
      const start = startRef.current ?? now;
      const elapsed = reduceMotion ? SCENE3_END + 500 : now - start;
      const particles = particlesRef.current;

      let morph = 0;
      let linkAlpha = 0;
      if (!reduceMotion) {
        if (elapsed >= SCENE2_END) {
          morph = easeInOut(Math.min(1, (elapsed - SCENE2_END) / 2000));
          linkAlpha = 1 - morph * 0.85;
        } else if (elapsed >= SCENE1_END) {
          linkAlpha = easeInOut(Math.min(1, (elapsed - SCENE1_END) / 800));
        }
      } else {
        morph = 1;
        linkAlpha = 0.15;
      }

      const si = reduceMotion ? 2 : sceneIndexAt(elapsed);
      if (si !== lastSceneRef.current) {
        lastSceneRef.current = si;
        setScene(si);
      }
      if (!reduceMotion && elapsed >= CTA_AT && !ctaShownRef.current && !exitingRef.current) {
        ctaShownRef.current = true;
        setShowCta(true);
      }

      // Exit animation
      let exitT = 0;
      if (exitingRef.current && exitStartRef.current != null) {
        exitT = Math.min(1, (now - exitStartRef.current) / 1400);
        lightRef.current = easeInOut(Math.min(1, exitT / 0.55));
        if (exitT >= 1) {
          finish("complete");
          return;
        }
      }

      ctx.fillStyle = BG;
      ctx.fillRect(0, 0, w, h);

      // Soft ambient orbs
      const orb = ctx.createRadialGradient(w * 0.7, h * 0.2, 0, w * 0.7, h * 0.2, w * 0.45);
      orb.addColorStop(0, "rgba(45, 31, 94, 0.35)");
      orb.addColorStop(1, "rgba(5, 8, 22, 0)");
      ctx.fillStyle = orb;
      ctx.fillRect(0, 0, w, h);

      const orb2 = ctx.createRadialGradient(w * 0.2, h * 0.75, 0, w * 0.2, h * 0.75, w * 0.35);
      orb2.addColorStop(0, "rgba(232, 98, 26, 0.08)");
      orb2.addColorStop(1, "rgba(5, 8, 22, 0)");
      ctx.fillStyle = orb2;
      ctx.fillRect(0, 0, w, h);

      // Update particles
      for (const p of particles) {
        if (exitingRef.current) {
          const dx = p.x - w / 2;
          const dy = p.y - h / 2;
          p.x += dx * 0.02 * (1 + exitT * 3);
          p.y += dy * 0.02 * (1 + exitT * 3);
          p.z += 0.02;
          p.opacity *= 0.985;
        } else if (morph > 0.001) {
          const mx = p.ox + (p.tx - p.ox) * morph;
          const my = p.oy + (p.ty - p.oy) * morph;
          // gentle drift under morph
          p.ox += p.vx * (1 - morph);
          p.oy += p.vy * (1 - morph);
          if (p.ox < 0 || p.ox > w) p.vx *= -1;
          if (p.oy < 0 || p.oy > h) p.vy *= -1;
          p.x = mx;
          p.y = my;
        } else {
          p.x += p.vx;
          p.y += p.vy;
          if (p.x < 0 || p.x > w) p.vx *= -1;
          if (p.y < 0 || p.y > h) p.vy *= -1;
          p.ox = p.x;
          p.oy = p.y;
        }
      }

      // Connections
      if (linkAlpha > 0.02 && !exitingRef.current) {
        const maxDist = Math.min(w, h) * 0.12;
        const maxDist2 = maxDist * maxDist;
        let edges = 0;
        ctx.lineWidth = 0.6;
        for (let i = 0; i < particles.length && edges < 90; i++) {
          for (let j = i + 1; j < particles.length && edges < 90; j++) {
            const a = particles[i];
            const b = particles[j];
            const dx = a.x - b.x;
            const dy = a.y - b.y;
            const d2 = dx * dx + dy * dy;
            if (d2 < maxDist2) {
              const alpha = (1 - Math.sqrt(d2) / maxDist) * linkAlpha * 0.45;
              ctx.strokeStyle = `rgba(180, 160, 255, ${alpha})`;
              ctx.beginPath();
              ctx.moveTo(a.x, a.y);
              ctx.lineTo(b.x, b.y);
              ctx.stroke();
              edges++;
            }
          }
        }
      }

      // Particles
      for (const p of particles) {
        const glow = 6 + p.z * 6;
        const g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, glow);
        const base = morph > 0.5 ? "232, 98, 26" : "200, 190, 255";
        const op = p.opacity * (exitingRef.current ? 1 - exitT * 0.3 : 1);
        g.addColorStop(0, `rgba(${base}, ${op})`);
        g.addColorStop(1, `rgba(${base}, 0)`);
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(p.x, p.y, glow, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = `rgba(245, 240, 255, ${op * 0.9})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r * p.z * (1 + exitT * 2), 0, Math.PI * 2);
        ctx.fill();
      }

      // Soft light wash on exit
      if (lightRef.current > 0) {
        ctx.fillStyle = `rgba(245, 240, 255, ${lightRef.current * 0.55})`;
        ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = `rgba(45, 31, 94, ${lightRef.current * 0.25})`;
        ctx.fillRect(0, 0, w, h);
      }

      rafRef.current = requestAnimationFrame(draw);
    };

    rafRef.current = requestAnimationFrame(draw);
    return () => {
      cancelAnimationFrame(rafRef.current);
      window.removeEventListener("resize", resize);
    };
  }, [finish, reduceMotion]);

  const textOpacity = (() => {
    if (reduceMotion) return { s1: 0, s2: 0, brand: 1 };
    // Approximate based on scene state for CSS overlay
    if (scene === 0) return { s1: 1, s2: 0, brand: 0 };
    if (scene === 1) return { s1: 0, s2: 1, brand: 0 };
    return { s1: 0, s2: 0, brand: 1 };
  })();

  return (
    <div
      className={`${styles.root} ${overlayClassName}`}
      role="dialog"
      aria-modal="true"
      aria-label="Welcome to Momentra"
    >
      <canvas ref={canvasRef} className={styles.canvas} aria-hidden />

      <button
        type="button"
        className={styles.skip}
        onClick={() => finish("skip")}
      >
        Skip
      </button>

      <div className={styles.copyStage}>
        <p
          className={styles.sentence}
          style={{ opacity: textOpacity.s1 }}
          aria-hidden={textOpacity.s1 < 0.5}
        >
          {COPY.scene1}
        </p>
        <p
          className={styles.sentence}
          style={{ opacity: textOpacity.s2 }}
          aria-hidden={textOpacity.s2 < 0.5}
        >
          {COPY.scene2}
        </p>
        <div
          className={styles.brandBlock}
          style={{ opacity: textOpacity.brand }}
          aria-hidden={textOpacity.brand < 0.5}
        >
          <p className={styles.brand}>{COPY.brand}</p>
          <p className={styles.subtitle}>{COPY.subtitle}</p>
        </div>
      </div>

      {(showCta || reduceMotion) && !exiting ? (
        <div className={styles.ctaWrap}>
          <button type="button" className={styles.cta} onClick={beginExit}>
            {COPY.cta}
          </button>
        </div>
      ) : null}

      {exiting ? <div className={styles.exitVeil} aria-hidden /> : null}
    </div>
  );
}
