/**
 * Playwright Goa Trip web coverage — deferred until auth harness + selectors exist.
 *
 * Product gaps:
 * - No Playwright config in web/ yet
 * - No test auth injection on the Next.js app
 * - Money UI is /app overlays without data-testid
 * - Settlement UI only on experience Pulse
 *
 * When ready: add @playwright/test, playwright.config.ts, and enable this suite.
 */
import { test } from "@playwright/test";

test.describe("Goa Trip web", () => {
  test.skip(true, "Playwright greenfield — see docs/testing/MY_MONEY_GROUP_ACCEPTANCE_ASSESSMENT.md");

  test("login and context switcher", async () => {
    // placeholder
  });
});
