/**
 * Shared setup control types — context-agnostic.
 * Catalogs (Business / Group / Personal) supply concrete choices.
 */

export type SetupChoice = {
  value: string;
  label: string;
  description?: string;
  icon?: string;
};

export type SetupControlType =
  | "choice_cards"
  | "choice_chips"
  | "multi_cards"
  | "multi_chips"
  | "money"
  | "percentage"
  | "invite"
  | "date"
  | "text"
  | "textarea"
  | "picker"
  | "suggested_picker"
  | "toggle"
  | "radio"
  | "chips"
  | "cards"
  | "search_picker"
  | "multi_select";
