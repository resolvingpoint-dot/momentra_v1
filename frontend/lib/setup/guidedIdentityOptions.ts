/**
 * Shared identity option lists for guided setup pickers (all contexts).
 * Keep out of Business/Group-specific modules so contexts do not cross-import.
 */

export type SetupIdentityChoice = { value: string; label: string };

export const GUIDED_CURRENCY_OPTIONS: SetupIdentityChoice[] = [
  { value: "INR", label: "₹ INR — Indian Rupee" },
  { value: "USD", label: "$ USD — US Dollar" },
  { value: "EUR", label: "€ EUR — Euro" },
  { value: "GBP", label: "£ GBP — British Pound" },
  { value: "AED", label: "AED — UAE Dirham" },
  { value: "AUD", label: "A$ AUD — Australian Dollar" },
  { value: "CAD", label: "C$ CAD — Canadian Dollar" },
  { value: "SGD", label: "S$ SGD — Singapore Dollar" },
  { value: "JPY", label: "¥ JPY — Japanese Yen" },
  { value: "CHF", label: "CHF — Swiss Franc" },
];

export const GUIDED_CURRENCY_SUGGESTED = ["INR", "USD", "EUR", "GBP"] as const;
