"use client";

import type { ReactNode } from "react";
import type { SetupChoice, SetupControlType } from "@/components/setup/shared/setupControlTypes";
import { SetupChoiceCards } from "@/components/setup/shared/SetupChoiceCards";
import { SetupChoiceChips } from "@/components/setup/shared/SetupChoiceChips";
import { SetupMultiCards } from "@/components/setup/shared/SetupMultiCards";
import { SetupMoneyField } from "@/components/setup/shared/SetupMoneyField";
import { SetupPercentField } from "@/components/setup/shared/SetupPercentField";
import { SetupTextInput } from "@/components/setup/shared/SetupTextInput";
import { SetupSearchPicker } from "@/components/setup/shared/SetupSearchPicker";
import { SetupToggleReveal } from "@/components/setup/shared/SetupToggleReveal";
import { SuggestedChipsPicker } from "@/components/setup/shared/SuggestedChipsPicker";
import type { CurrencyReference } from "@/lib/reference_data/types";

export type SetupFieldRenderProps = {
  control: SetupControlType;
  label: string;
  helper?: string;
  optionalLabel?: string;
  error?: string | null;
  disabled?: boolean;
  explainer?: { title: string; body: string } | null;
  /** Single-select / text value */
  value?: string;
  onChange?: (value: string) => void;
  options?: SetupChoice[];
  /** Multi-select */
  values?: string[];
  onChangeValues?: (values: string[]) => void;
  /** Money */
  amountMinor?: number | null;
  currencyCode?: string;
  currencies?: CurrencyReference[];
  onChangeAmount?: (amountMinor: number | null) => void;
  /** Percent */
  percent?: number | null;
  onChangePercent?: (value: number | null) => void;
  /** Text */
  placeholder?: string;
  maxLength?: number;
  examples?: string[];
  multiline?: boolean;
  /** Suggested picker */
  suggested?: string[];
  viewAllLabel?: string;
  /** Toggle */
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
  children?: ReactNode;
};

/**
 * Registry-based field renderer — controlType → shared control.
 * Template screens pass catalog `control` + value handlers; no Business branching here.
 */
export function SetupFieldRenderer(props: SetupFieldRenderProps): ReactNode {
  const {
    control,
    label,
    helper,
    optionalLabel,
    error,
    disabled,
    explainer,
    value = "",
    onChange,
    options = [],
    values = [],
    onChangeValues,
    amountMinor = null,
    currencyCode = "",
    currencies,
    onChangeAmount,
    percent = null,
    onChangePercent,
    placeholder,
    maxLength,
    examples,
    multiline,
    suggested,
    viewAllLabel,
    checked = false,
    onCheckedChange,
    children,
  } = props;

  switch (control) {
    case "choice_cards":
    case "cards":
      return (
        <SetupChoiceCards
          label={label}
          helper={helper}
          optionalLabel={optionalLabel}
          error={error}
          value={value}
          options={options}
          onChange={onChange ?? (() => undefined)}
          disabled={disabled}
          explainer={explainer}
        />
      );
    case "choice_chips":
    case "chips":
    case "radio":
      return (
        <SetupChoiceChips
          label={label}
          helper={helper}
          optionalLabel={optionalLabel}
          error={error}
          value={value}
          options={options}
          onChange={onChange ?? (() => undefined)}
          disabled={disabled}
          explainer={explainer}
        />
      );
    case "multi_cards":
    case "multi_select":
      return (
        <SetupMultiCards
          label={label}
          helper={helper}
          optionalLabel={optionalLabel}
          error={error}
          values={values}
          options={options}
          onChange={onChangeValues ?? (() => undefined)}
          disabled={disabled}
        />
      );
    case "money":
      return (
        <SetupMoneyField
          label={label}
          helper={helper}
          optionalLabel={optionalLabel}
          error={error}
          amountMinor={amountMinor}
          currencyCode={currencyCode}
          currencies={currencies}
          onChange={onChangeAmount ?? (() => undefined)}
          disabled={disabled}
          explainer={explainer}
        />
      );
    case "percentage":
      return (
        <SetupPercentField
          label={label}
          helper={helper}
          optionalLabel={optionalLabel}
          error={error}
          value={percent}
          onChange={onChangePercent ?? (() => undefined)}
          disabled={disabled}
        />
      );
    case "text":
    case "textarea":
      return (
        <SetupTextInput
          label={label}
          helper={helper}
          optionalLabel={optionalLabel}
          error={error}
          value={value}
          onChange={onChange ?? (() => undefined)}
          placeholder={placeholder}
          disabled={disabled}
          multiline={multiline || control === "textarea"}
          maxLength={maxLength}
          examples={examples}
          explainer={explainer}
        />
      );
    case "picker":
    case "search_picker":
      return (
        <SetupSearchPicker
          label={label}
          helper={helper}
          optionalLabel={optionalLabel}
          error={error}
          value={value}
          options={options}
          onChange={onChange ?? (() => undefined)}
          disabled={disabled}
        />
      );
    case "suggested_picker":
      return (
        <SuggestedChipsPicker
          label={label}
          helper={helper}
          optionalLabel={optionalLabel}
          error={error}
          value={value}
          options={options}
          suggested={suggested}
          onChange={onChange ?? (() => undefined)}
          disabled={disabled}
          viewAllLabel={viewAllLabel}
        />
      );
    case "toggle":
      return (
        <SetupToggleReveal
          label={label}
          checked={checked}
          onChange={onCheckedChange ?? (() => undefined)}
          disabled={disabled}
        >
          {children}
        </SetupToggleReveal>
      );
    case "date":
      return (
        <SetupTextInput
          label={label}
          helper={helper}
          optionalLabel={optionalLabel}
          error={error}
          value={value}
          onChange={onChange ?? (() => undefined)}
          placeholder={placeholder}
          disabled={disabled}
          type="date"
          explainer={explainer}
        />
      );
    case "invite":
    case "multi_chips":
      // Invite sheets stay template-owned; multi_chips uses multi_cards path above when mapped.
      return null;
    default:
      return null;
  }
}
