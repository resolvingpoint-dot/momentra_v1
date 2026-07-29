"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalFutureBuildingAxisScores } from "@/lib/api/personalDomainTypes";

const AXIS_ORDER = [
  { key: "learning" as const, label: "Learning", angle: -90 },
  { key: "execution" as const, label: "Execution", angle: -18 },
  { key: "milestones" as const, label: "Milestones", angle: 54 },
  { key: "opportunities" as const, label: "Opportunities", angle: 126 },
  { key: "confidence" as const, label: "Confidence", angle: 198 },
];

type FbAxisRadarProps = {
  scores: PersonalFutureBuildingAxisScores;
};

function polarToXY(angleDeg: number, radius: number, cx: number, cy: number) {
  const rad = (angleDeg * Math.PI) / 180;
  return { x: cx + radius * Math.cos(rad), y: cy + radius * Math.sin(rad) };
}

export function FbAxisRadar({ scores }: FbAxisRadarProps) {
  const { colors } = useThemeTokens();
  const cx = 50;
  const cy = 50;
  const points = AXIS_ORDER.map(({ key, angle }) => {
    const r = 8 + (scores[key] / 100) * 32;
    const { x, y } = polarToXY(angle, r, cx, cy);
    return `${x},${y}`;
  }).join(" ");

  return (
    <div className="relative mx-auto h-56 w-full max-w-sm">
      <svg viewBox="0 0 100 100" className="h-full w-full">
        {[10, 25, 40].map((r) => (
          <circle key={r} cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={0.5} />
        ))}
        {AXIS_ORDER.map(({ angle }) => {
          const outer = polarToXY(angle, 42, cx, cy);
          return <line key={angle} x1={cx} y1={cy} x2={outer.x} y2={outer.y} stroke="rgba(255,255,255,0.06)" strokeWidth={0.5} />;
        })}
        <polygon points={points} fill={`${colors.brandPrimary}33`} stroke={colors.brandPrimary} strokeWidth={1.5} />
      </svg>
      {AXIS_ORDER.map(({ label, angle }) => {
        const { x, y } = polarToXY(angle, 48, cx, cy);
        return (
          <span
            key={label}
            className="absolute -translate-x-1/2 -translate-y-1/2 text-center uppercase"
            style={{
              left: `${x}%`,
              top: `${y}%`,
              ...personalTypography.labelSm,
              fontSize: 8,
              fontWeight: 700,
              opacity: 0.6,
              letterSpacing: "0.08em",
            }}
          >
            {label}
          </span>
        );
      })}
    </div>
  );
}
