import type { AppContext } from "@/lib/appContext";
import type { BottomNavTabId } from "@/lib/bottomNavTabs";

export type ScreenOverlay =
  | "create"
  | "life_ops_setup"
  | "quick_add"
  | "settings"
  | "life360"
  | "invite_scan"
  | "life_ops_activity"
  | "life_ops_edit_activity"
  | "master_expense"
  | null;

export function tabToAnalyticsSlug(tab: BottomNavTabId): string {
  return tab === "add" ? "create" : tab;
}

export function resolveScreenName(
  context: AppContext,
  tab: BottomNavTabId,
  overlay: ScreenOverlay,
  previousTab: BottomNavTabId = "pulse",
): string {
  if (overlay === "settings") return "settings";
  if (overlay === "life360") return "life360";
  if (overlay === "invite_scan") return "invite_scan";
  if (overlay === "create") return `${context}_create_overlay`;
  if (overlay === "life_ops_setup") return `${context}_life_ops_setup`;
  if (overlay === "quick_add") return `${context}_quick_add`;
  if (overlay === "life_ops_activity") return `${context}_life_ops_activity`;
  if (overlay === "life_ops_edit_activity") return `${context}_life_ops_edit_activity`;
  if (overlay === "master_expense") return `${context}_master_expense`;
  const visibleTab = tab === "add" ? previousTab : tab;
  return `${context}_${tabToAnalyticsSlug(visibleTab)}`;
}

/** Map Next.js pathname → Firebase screen_view name. Returns null to skip. */
export function resolveWebRouteScreen(pathname: string | null): string | null {
  if (!pathname) return null;
  const path = pathname.replace(/\/+$/, "") || "/";

  if (path === "/") return "marketing_home";
  if (path === "/about") return "marketing_about";
  if (path === "/personal") return "marketing_personal";
  if (path === "/group") return "marketing_group";
  if (path === "/business") return "marketing_business";
  if (path === "/contact") return "marketing_contact";
  if (path === "/how-moments-work") return "marketing_how_moments_work";
  if (path === "/privacy") return "marketing_privacy";
  if (path === "/terms") return "marketing_terms";
  if (path === "/data-policy") return "marketing_data_policy";
  if (path === "/cookies") return "marketing_cookies";
  if (path === "/book") return "book";
  if (path.startsWith("/invite")) return "invite";
  if (path === "/app" || path.startsWith("/app/")) return "app";
  if (path === "/debug/events") return "debug_events";
  if (path === "/debug/registry") return "debug_registry";
  return `web_${path.slice(1).replace(/\//g, "_") || "unknown"}`;
}
