/**
 * Headed Dokploy login helper.
 * 1) Browser opens to Dokploy
 * 2) Log in manually
 * 3) Script captures cookies + tries project.all, writes dokploy-session.json
 */
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const DOKPLOY_URL = process.env.DOKPLOY_URL || "http://192.168.68.108:3000";
const OUT = path.join(__dirname, "dokploy-session.json");

(async () => {
  const browser = await chromium.launch({ headless: false, channel: "chrome" }).catch(() =>
    chromium.launch({ headless: false })
  );
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto(DOKPLOY_URL, { waitUntil: "domcontentloaded" });
  console.log("Log in to Dokploy in the opened window. Waiting up to 10 minutes...");

  const deadline = Date.now() + 10 * 60 * 1000;
  let authed = false;
  while (Date.now() < deadline) {
    const cookies = await context.cookies();
    const hasSession = cookies.some(
      (c) => /token|session|auth|jwt/i.test(c.name) && c.value && c.value.length > 20
    );
    // Probe API with page cookies
    const probe = await page.evaluate(async (base) => {
      try {
        const r = await fetch(`${base}/api/project.all`, {
          credentials: "include",
          headers: { accept: "application/json" },
        });
        const text = await r.text();
        return { status: r.status, text: text.slice(0, 500) };
      } catch (e) {
        return { status: 0, text: String(e) };
      }
    }, DOKPLOY_URL);

    if (probe.status === 200) {
      console.log("Authenticated via session cookies.");
      const storage = await context.storageState();
      fs.writeFileSync(
        OUT,
        JSON.stringify({ dokployUrl: DOKPLOY_URL, cookies, storage, probe }, null, 2)
      );
      console.log("Wrote", OUT);
      authed = true;
      break;
    }
    if (hasSession) {
      console.log("Session cookie present, API still", probe.status, probe.text.slice(0, 80));
    }
    await page.waitForTimeout(3000);
  }

  if (!authed) {
    console.error("Timed out waiting for Dokploy login.");
    await browser.close();
    process.exit(1);
  }
  await browser.close();
  process.exit(0);
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
