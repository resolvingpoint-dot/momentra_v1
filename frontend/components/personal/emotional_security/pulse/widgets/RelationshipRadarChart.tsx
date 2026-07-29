"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { PersonalEmotionalSecurityRadarAxis } from "@/lib/api/personalDomainTypes";

type RelationshipRadarChartProps = {
  bondIndex: number;
  axes: PersonalEmotionalSecurityRadarAxis[];
};

function pentagonPoints(cx: number, cy: number, r: number, scores: number[]): string {
  const n = scores.length || 5;
  const pts: string[] = [];
  for (let i = 0; i < n; i++) {
    const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
    const scale = (scores[i] ?? 50) / 100;
    const x = cx + Math.cos(angle) * r * scale;
    const y = cy + Math.sin(angle) * r * scale;
    pts.push(`${x},${y}`);
  }
  return pts.join(" ");
}

function labelPosition(cx: number, cy: number, r: number, index: number, total: number) {
  const angle = (Math.PI * 2 * index) / total - Math.PI / 2;
  return { x: cx + Math.cos(angle) * (r + 18), y: cy + Math.sin(angle) * (r + 18) };
}

export function RelationshipRadarChart({ bondIndex, axes }: RelationshipRadarChartProps) {
  const { colors } = useThemeTokens();
  const cx = 100;
  const cy = 100;
  const r = 70;
  const scores = axes.map((a) => a.score);
  const displayAxes = axes.length >= 5 ? axes.slice(0, 5) : axes;

  return (
    <div className="relative mx-auto h-72 w-full max-w-sm">
      <svg viewBox="0 0 200 200" className="h-full w-full overflow-visible" aria-hidden>
        <circle cx={cx} cy={cy} r={50} fill="none" stroke="rgba(108, 78, 242, 0.1)" strokeWidth={0.5} />
        <circle cx={cx} cy={cy} r={80} fill="none" stroke="rgba(108, 78, 242, 0.05)" strokeWidth={0.5} />
        <polygon
          points={pentagonPoints(cx, cy, r, scores.length ? scores : [bondIndex, bondIndex, bondIndex, bondIndex, bondIndex])}
          fill="rgba(108, 78, 242, 0.15)"
          stroke={colors.brandPrimary}
          strokeWidth={2.5}
        />
        {displayAxes.map((axis, i) => {
          const angle = (Math.PI * 2 * i) / displayAxes.length - Math.PI / 2;
          const nx = cx + Math.cos(angle) * r;
          const ny = cy + Math.sin(angle) * r;
          const label = labelPosition(cx, cy, r, i, displayAxes.length);
          return (
            <g key={axis.axis_id}>
              <circle cx={nx} cy={ny} r={5} fill={colors.brandPrimary} opacity={0.85} />
              <text
                x={label.x}
                y={label.y}
                textAnchor="middle"
                dominantBaseline="middle"
                fill={colors.textSecondary}
                fontSize={9}
                fontWeight={800}
                style={{ textTransform: "uppercase", letterSpacing: "0.08em" }}
              >
                {axis.label}
              </text>
            </g>
          );
        })}
        <circle cx={cx} cy={cy} r={14} fill={colors.primaryContainer ?? colors.brandPrimary} />
        <text x={cx} y={cy + 4} textAnchor="middle" fill="#fff" fontSize={12} fontWeight={700}>
          {bondIndex}
        </text>
      </svg>
    </div>
  );
}
