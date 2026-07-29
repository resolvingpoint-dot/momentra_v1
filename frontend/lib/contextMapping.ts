import type { AppContext } from "@/lib/appContext";
import type { BackendContextKey } from "@/lib/api/bootstrapTypes";

const BACKEND_TO_APP: Record<BackendContextKey, AppContext | null> = {
  MY_MONEY: "personal",
  GROUP: "group",
  BUSINESS: "business",
  CIRCLE: "circle",
};

const APP_TO_BACKEND: Record<AppContext, BackendContextKey> = {
  personal: "MY_MONEY",
  group: "GROUP",
  business: "BUSINESS",
  circle: "CIRCLE",
};

export function backendContextToApp(key: string): AppContext {
  const mapped = BACKEND_TO_APP[key as BackendContextKey];
  return mapped ?? "personal";
}

export function appContextToBackend(context: AppContext): BackendContextKey {
  return APP_TO_BACKEND[context];
}

export function isBackendContextKey(value: string): value is BackendContextKey {
  return value === "MY_MONEY" || value === "GROUP" || value === "BUSINESS" || value === "CIRCLE";
}
