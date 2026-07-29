"use client";

/** Character counter for text fields. Prefer SetupField `counter` / SetupTextInput maxLength. */
export function CharacterCounter({
  current,
  max,
}: {
  current: number;
  max: number;
}) {
  return (
    <p className="text-[11px] opacity-50" aria-live="polite">
      {current} / {max} characters
    </p>
  );
}
