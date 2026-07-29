"use client";

type Life360MarkProps = {
  size?: number;
  className?: string;
};

/**
 * Top-bar Life 360 mark: stable core + 360° ring + slowly orbiting signal dots.
 * Meaning: full-circle life intelligence (you at the center, signals around).
 */
export function Life360Mark({ size = 24, className }: Life360MarkProps) {
  return (
    <span
      className={className}
      style={{ width: size, height: size, display: "inline-flex" }}
      aria-hidden
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="overflow-visible text-[#f2ca50]"
      >
        {/* Static 360° track */}
        <circle
          cx="12"
          cy="12"
          r="8.25"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeOpacity="0.55"
          fill="none"
        />
        {/* Soft arc accents (life domains) */}
        <path
          d="M12 3.75 A8.25 8.25 0 0 1 20.25 12"
          stroke="currentColor"
          strokeWidth="1.75"
          strokeLinecap="round"
          fill="none"
          strokeOpacity="0.9"
        />
        <path
          d="M12 20.25 A8.25 8.25 0 0 1 3.75 12"
          stroke="currentColor"
          strokeWidth="1.75"
          strokeLinecap="round"
          fill="none"
          strokeOpacity="0.9"
        />
        {/* Orbiting satellites */}
        <g
          className="motion-safe:animate-life360-mark-spin motion-reduce:animate-none"
          style={{ transformOrigin: "12px 12px" }}
        >
          <circle cx="12" cy="3.75" r="1.65" fill="currentColor" />
          <circle cx="19.1" cy="16.9" r="1.35" fill="currentColor" fillOpacity="0.85" />
          <circle cx="4.9" cy="16.9" r="1.35" fill="currentColor" fillOpacity="0.85" />
        </g>
        {/* Core — you / life alignment */}
        <circle cx="12" cy="12" r="2.75" fill="currentColor" />
      </svg>
    </span>
  );
}
