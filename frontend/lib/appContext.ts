export type AppContext = "personal" | "group" | "business" | "circle";

export const DEFAULT_APP_CONTEXT: AppContext = "personal";

export const APP_CONTEXTS: readonly AppContext[] = [
  "personal",
  "group",
  "business",
  "circle",
] as const;

export function isAppContext(value: string): value is AppContext {
  return APP_CONTEXTS.includes(value as AppContext);
}
