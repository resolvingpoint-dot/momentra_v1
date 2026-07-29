"use client";

import { useId } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { SetupField } from "@/components/setup/shared/SetupField";
import { GuidedSetupExplainer } from "@/components/setup/GuidedSetupExplainer";

type Props = {
  label: string;
  helper?: string;
  optionalLabel?: string;
  error?: string | null;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  multiline?: boolean;
  inputMode?: React.HTMLAttributes<HTMLInputElement>["inputMode"];
  id?: string;
  maxLength?: number;
  explainer?: { title: string; body: string } | null;
  examples?: string[];
  type?: "text" | "date";
};

export function SetupTextInput({
  label,
  helper,
  optionalLabel,
  error,
  value,
  onChange,
  placeholder,
  disabled,
  multiline,
  inputMode,
  id,
  maxLength,
  explainer,
  examples,
  type = "text",
}: Props) {
  const { colors } = useThemeTokens();
  const autoId = useId();
  const fieldId = id ?? autoId;
  const style = {
    borderColor: error
      ? colors.error
      : `color-mix(in srgb, ${colors.border} 40%, transparent)`,
    background: colors.background,
  } as const;

  const counter =
    typeof maxLength === "number"
      ? `${value.length} / ${maxLength} characters`
      : null;

  const exampleHint =
    examples && examples.length > 0
      ? `Examples: ${examples.join(" · ")}`
      : undefined;
  const combinedHelper = [helper, exampleHint].filter(Boolean).join(" ");

  return (
    <SetupField
      label={label}
      helper={combinedHelper || undefined}
      optionalLabel={optionalLabel}
      error={error}
      htmlFor={fieldId}
      counter={counter}
      explainer={
        explainer ? (
          <GuidedSetupExplainer title={explainer.title} body={explainer.body} />
        ) : undefined
      }
    >
      {multiline ? (
        <textarea
          id={fieldId}
          disabled={disabled}
          value={value}
          placeholder={placeholder}
          maxLength={maxLength}
          onChange={(e) => onChange(e.target.value)}
          rows={3}
          className="w-full rounded-xl border px-3 py-2.5 text-sm outline-none disabled:opacity-50"
          style={style}
          aria-describedby={counter ? `${fieldId}-count` : undefined}
        />
      ) : (
        <input
          id={fieldId}
          type={type}
          disabled={disabled}
          value={value}
          placeholder={placeholder}
          inputMode={inputMode}
          maxLength={maxLength}
          onChange={(e) => onChange(e.target.value)}
          className="min-h-11 w-full rounded-xl border px-3 py-2.5 text-sm outline-none disabled:opacity-50"
          style={style}
          aria-describedby={counter ? `${fieldId}-count` : undefined}
        />
      )}
      {counter ? (
        <span id={`${fieldId}-count`} className="sr-only">
          {counter}
        </span>
      ) : null}
    </SetupField>
  );
}
