"use client";

import { useEffect, useState } from "react";
import { brandTokens } from "@/lib/brandTokens";

interface SplashScreenProps {
  onFinish: () => void;
}

const DOT_POINTS: [number, number][] = [
  [14, 100],
  [14, 62],
  [34, 74],
  [54, 32],
  [54, 100],
];

export function SplashScreen({ onFinish }: SplashScreenProps) {
  const [orb1, setOrb1] = useState(false);
  const [orb2, setOrb2] = useState(false);
  const [dots, setDots] = useState([false, false, false, false, false]);
  const [ghost, setGhost] = useState(false);
  const [peak, setPeak] = useState(false);
  const [arc, setArc] = useState(false);
  const [spark, setSpark] = useState(false);
  const [sparkPulse, setSparkPulse] = useState(false);
  const [word, setWord] = useState(false);
  const [fdot, setFdot] = useState(false);
  const [tag, setTag] = useState(false);

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = [];

    timers.push(setTimeout(() => setOrb1(true), 100));
    timers.push(setTimeout(() => setOrb2(true), 300));

    [280, 440, 600, 760, 920].forEach((delay, i) => {
      timers.push(setTimeout(() => {
        setDots((prev) => {
          const next = [...prev];
          next[i] = true;
          return next;
        });
      }, delay));
    });

    timers.push(setTimeout(() => setGhost(true), 1080));
    timers.push(setTimeout(() => setPeak(true), 1400));
    timers.push(setTimeout(() => setArc(true), 1920));
    timers.push(setTimeout(() => {
      setSpark(true);
      timers.push(setTimeout(() => setSparkPulse(true), 370));
    }, 2130));
    timers.push(setTimeout(() => setWord(true), 2330));
    timers.push(setTimeout(() => setFdot(true), 2570));
    timers.push(setTimeout(() => setTag(true), 2720));
    timers.push(setTimeout(() => onFinish(), 3300));

    return () => timers.forEach(clearTimeout);
  }, [onFinish]);

  return (
    <div
      className="relative flex min-h-screen h-screen flex-col items-center justify-center overflow-hidden"
      style={{ backgroundColor: brandTokens.brand }}
    >
      <div
        className="pointer-events-none absolute rounded-full transition-opacity duration-700"
        style={{
          width: 260,
          height: 260,
          top: -80,
          right: -60,
          backgroundColor: brandTokens.cta,
          opacity: orb1 ? 0.18 : 0,
        }}
      />
      <div
        className="pointer-events-none absolute rounded-full transition-opacity duration-700"
        style={{
          width: 200,
          height: 200,
          bottom: -60,
          left: -60,
          backgroundColor: brandTokens.progress,
          opacity: orb2 ? 0.12 : 0,
        }}
      />

      <div className="flex flex-col items-center">
        <svg
          width={120}
          height={120}
          viewBox="0 0 120 120"
          className="block"
          aria-hidden
        >
          <defs>
            <linearGradient id="splash-emb" x1="0" y1="1" x2="1" y2="0">
              <stop offset="0%" stopColor={brandTokens.cta} />
              <stop offset="100%" stopColor={brandTokens.progress} />
            </linearGradient>
          </defs>

          <path
            d="M14,100 L14,50 L34,74 L54,24 L54,100"
            fill="none"
            stroke={brandTokens.textOnDark}
            strokeWidth={8}
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{
              opacity: ghost ? 0.15 : 0,
              transition: "opacity 0.3s ease-out",
            }}
          />

          {DOT_POINTS.map(([cx, cy], i) => (
            <circle
              key={i}
              cx={cx}
              cy={cy}
              r={6}
              fill={brandTokens.textOnDark}
              style={{
                opacity: dots[i] ? 1 : 0,
                transform: dots[i] ? "scale(1)" : "scale(0)",
                transformOrigin: `${cx}px ${cy}px`,
                transition: "opacity 0.2s, transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1)",
              }}
            />
          ))}

          <path
            d="M54,100 L54,32 L74,74 L94,32 L96,100"
            fill="none"
            stroke="url(#splash-emb)"
            strokeWidth={8}
            strokeLinecap="round"
            strokeLinejoin="round"
            pathLength={340}
            strokeDasharray={340}
            strokeDashoffset={peak ? 0 : 340}
            style={{
              transition: "stroke-dashoffset 0.52s ease-in-out",
            }}
          />

          <path
            d="M94,32 Q98,20 104,16"
            fill="none"
            stroke={brandTokens.progress}
            strokeWidth={2.5}
            strokeLinecap="round"
            style={{
              opacity: arc ? 0.7 : 0,
              transition: "opacity 0.2s ease-out",
            }}
          />

          <circle
            cx={105}
            cy={18}
            r={spark ? (sparkPulse ? 12 : 10) : 0}
            fill={brandTokens.progress}
            style={{
              opacity: spark ? 1 : 0,
              transition: sparkPulse
                ? "r 0.9s ease-in-out infinite alternate, opacity 0.08s"
                : "r 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.08s",
            }}
          />
          <circle
            cx={105}
            cy={18}
            r={spark ? (sparkPulse ? 6.6 : 5.5) : 0}
            fill={brandTokens.cta}
            style={{
              opacity: spark ? 1 : 0,
              transition: sparkPulse
                ? "r 0.9s ease-in-out infinite alternate, opacity 0.08s"
                : "r 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.08s",
            }}
          />
        </svg>

        <div className="h-5" />

        <div
          className="flex flex-col items-center gap-[5px] transition-all duration-[440ms] ease-out"
          style={{
            opacity: word ? 1 : 0,
            transform: word ? "translateY(0)" : "translateY(12px)",
          }}
        >
          <div className="relative flex items-start">
            <span
              className="text-[32px] font-medium tracking-[-0.5px]"
              style={{ color: brandTokens.textOnDark }}
            >
              momentr
            </span>
            <span className="relative">
              <span
                className="text-[32px] font-medium tracking-[-0.5px]"
                style={{ color: brandTokens.cta }}
              >
                a
              </span>
              <span
                className="absolute -top-2.5 left-0.5 block h-[7px] w-[7px] rounded-full transition-all duration-200"
                style={{
                  backgroundColor: brandTokens.progress,
                  opacity: fdot ? 1 : 0,
                  transform: fdot ? "scale(1)" : "scale(0)",
                }}
              />
            </span>
          </div>
          <p
            className="text-[9px] font-normal tracking-[3px] transition-opacity duration-500"
            style={{
              color: brandTokens.textOnDark,
              opacity: tag ? 0.38 : 0,
            }}
          >
            TOGETHER · FORWARD
          </p>
        </div>
      </div>
    </div>
  );
}
