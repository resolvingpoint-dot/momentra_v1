import { describe, expect, it } from "vitest";
import { resolveWebRouteScreen } from "@/lib/analyticsScreens";

/** Shared screen_view names used across web / Android / iOS for shell overlays. */
export const SHARED_SHELL_SCREENS = ["settings", "life360", "invite_scan"] as const;

describe("resolveWebRouteScreen", () => {
  it("maps marketing and book routes", () => {
    expect(resolveWebRouteScreen("/")).toBe("marketing_home");
    expect(resolveWebRouteScreen("/about")).toBe("marketing_about");
    expect(resolveWebRouteScreen("/personal")).toBe("marketing_personal");
    expect(resolveWebRouteScreen("/group")).toBe("marketing_group");
    expect(resolveWebRouteScreen("/business")).toBe("marketing_business");
    expect(resolveWebRouteScreen("/contact")).toBe("marketing_contact");
    expect(resolveWebRouteScreen("/how-moments-work")).toBe(
      "marketing_how_moments_work",
    );
    expect(resolveWebRouteScreen("/privacy")).toBe("marketing_privacy");
    expect(resolveWebRouteScreen("/terms")).toBe("marketing_terms");
    expect(resolveWebRouteScreen("/data-policy")).toBe("marketing_data_policy");
    expect(resolveWebRouteScreen("/cookies")).toBe("marketing_cookies");
    expect(resolveWebRouteScreen("/book")).toBe("book");
  });

  it("maps invite, app entry, and debug", () => {
    expect(resolveWebRouteScreen("/invite/abc")).toBe("invite");
    expect(resolveWebRouteScreen("/app")).toBe("app");
    expect(resolveWebRouteScreen("/app/")).toBe("app");
    expect(resolveWebRouteScreen("/debug/events")).toBe("debug_events");
    expect(resolveWebRouteScreen("/debug/registry")).toBe("debug_registry");
  });

  it("shares shell overlay names with native platforms", () => {
    expect(SHARED_SHELL_SCREENS).toEqual([
      "settings",
      "life360",
      "invite_scan",
    ]);
  });
});
