/** Shared identity option lists for Business setup (Team Ops chip pattern). */

export type SetupChoice = { value: string; label: string };

export const SETUP_CURRENCY_FALLBACK: SetupChoice[] = [
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

export const SETUP_TIMEZONE_FALLBACK: SetupChoice[] = [
  { value: "Asia/Kolkata", label: "India (IST)" },
  { value: "Asia/Dubai", label: "Dubai (GST)" },
  { value: "Asia/Singapore", label: "Singapore" },
  { value: "Europe/London", label: "London" },
  { value: "America/New_York", label: "New York" },
  { value: "America/Los_Angeles", label: "Los Angeles" },
  { value: "UTC", label: "UTC" },
];

export const SETUP_LOCALE_FALLBACK: SetupChoice[] = [
  { value: "en-IN", label: "English (India)" },
  { value: "en-US", label: "English (US)" },
  { value: "en-GB", label: "English (UK)" },
  { value: "hi-IN", label: "Hindi (India)" },
  { value: "ar-AE", label: "Arabic (UAE)" },
];

export const SETUP_COUNTRY_FALLBACK: SetupChoice[] = [
  { value: "IN", label: "India" },
  { value: "US", label: "United States" },
  { value: "GB", label: "United Kingdom" },
  { value: "AE", label: "UAE" },
  { value: "SG", label: "Singapore" },
  { value: "AU", label: "Australia" },
  { value: "CA", label: "Canada" },
];

/** Financial year start month (MM). */
export const SETUP_FY_START_OPTIONS: SetupChoice[] = [
  { value: "01", label: "Jan" },
  { value: "02", label: "Feb" },
  { value: "03", label: "Mar" },
  { value: "04", label: "Apr" },
  { value: "05", label: "May" },
  { value: "06", label: "Jun" },
  { value: "07", label: "Jul" },
  { value: "08", label: "Aug" },
  { value: "09", label: "Sep" },
  { value: "10", label: "Oct" },
  { value: "11", label: "Nov" },
  { value: "12", label: "Dec" },
];

export function enumChoices(values: string[]): SetupChoice[] {
  return values.map((value) => ({
    value,
    label: value.replaceAll("_", " "),
  }));
}

/** Prefer curated Team Ops–length lists; enrich labels from reference when present. */
export function curatedChoices(
  fallback: SetupChoice[],
  items?: Array<{ code: string; label?: string; symbol?: string }>,
): SetupChoice[] {
  if (!items?.length) return fallback;
  const byCode = new Map(items.map((item) => [item.code, item]));
  return fallback.map(({ value, label }) => {
    const hit = byCode.get(value);
    if (!hit) return { value, label };
    if (hit.symbol) return { value, label: `${hit.symbol} ${value}` };
    if (hit.label) return { value, label: hit.label };
    return { value, label };
  });
}
