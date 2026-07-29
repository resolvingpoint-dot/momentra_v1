"use client";

import { usePersonalDomainTokens, useDomainGradient } from "@/lib/personal/personalDomainPalette";
import { MOTION_DURATION_S } from "@/lib/motion/tokens";

export function PersonalAtmosphericOrbs() {
  const tokens = usePersonalDomainTokens();
  const { colors } = tokens;
  const [from, to] = useDomainGradient();

  return (
    <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden" aria-hidden>
      <style>{`
        @keyframes orbDriftA {
          0%, 100% { transform: translate(0, 0); opacity: 0.55; }
          50% { transform: translate(12px, -18px); opacity: 0.75; }
        }
        @keyframes orbDriftB {
          0%, 100% { transform: translate(0, 0); opacity: 0.4; }
          50% { transform: translate(-16px, 10px); opacity: 0.6; }
        }
        @media (prefers-reduced-motion: reduce) {
          .momentra-orb { animation: none !important; }
        }
      `}</style>
      <div
        className="momentra-orb absolute -left-24 -top-24 size-96 rounded-full blur-[100px]"
        style={{
          background: `radial-gradient(circle at 30% 30%, ${from}, ${to})`,
          animation: `orbDriftA ${MOTION_DURATION_S.orbLoop}s ease-in-out infinite`,
        }}
      />
      <div
        className="momentra-orb absolute -right-32 top-1/2 size-80 rounded-full blur-[120px]"
        style={{
          background: `${colors.primaryContainer}1a`,
          animation: `orbDriftB ${MOTION_DURATION_S.orbLoop * 1.1}s ease-in-out infinite`,
        }}
      />
      <div
        className="momentra-orb absolute -bottom-32 left-1/3 size-64 rounded-full blur-[80px]"
        style={{
          background: `${colors.brandTertiary}0d`,
          animation: `orbDriftA ${MOTION_DURATION_S.orbLoop * 0.9}s ease-in-out infinite reverse`,
        }}
      />
    </div>
  );
}
