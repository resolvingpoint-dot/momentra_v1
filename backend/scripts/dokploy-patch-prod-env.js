/**
 * Patch momentra-stack Dokploy env for production security and redeploy.
 */
const fs = require("fs");
const path = require("path");

const SESSION = JSON.parse(
  fs.readFileSync(path.join(__dirname, "dokploy-session.json"), "utf8")
);
const DOKPLOY = SESSION.dokployUrl.replace(/\/$/, "");
const COOKIE_RAW = SESSION.cookies.map((c) => `${c.name}=${c.value}`).join("; ");
const composeId = fs
  .readFileSync(path.join(__dirname, "dokploy-compose-id.txt"), "utf8")
  .trim();

async function api(method, apiPath, body) {
  const headers = { accept: "application/json", cookie: COOKIE_RAW };
  if (body !== undefined) headers["content-type"] = "application/json";
  const res = await fetch(`${DOKPLOY}${apiPath}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  let json;
  try {
    json = JSON.parse(text);
  } catch {
    json = text;
  }
  if (!res.ok) throw new Error(`${method} ${apiPath} -> ${res.status}: ${text.slice(0, 800)}`);
  return json;
}

function parseEnv(raw) {
  const map = new Map();
  const order = [];
  for (const line of String(raw || "").split(/\r?\n/)) {
    if (!line.trim() || line.trim().startsWith("#")) {
      order.push({ type: "raw", line });
      continue;
    }
    const i = line.indexOf("=");
    if (i < 0) {
      order.push({ type: "raw", line });
      continue;
    }
    const key = line.slice(0, i).trim();
    const value = line.slice(i + 1);
    map.set(key, value);
    order.push({ type: "kv", key });
  }
  return { map, order };
}

function serializeEnv(map, order) {
  const seen = new Set();
  const lines = [];
  for (const item of order) {
    if (item.type === "raw") {
      lines.push(item.line);
      continue;
    }
    if (!map.has(item.key)) continue;
    lines.push(`${item.key}=${map.get(item.key)}`);
    seen.add(item.key);
  }
  for (const [key, value] of map.entries()) {
    if (seen.has(key)) continue;
    lines.push(`${key}=${value}`);
  }
  return lines.join("\n").replace(/\n*$/, "\n");
}

function set(map, key, value) {
  map.set(key, value);
}

(async () => {
  console.log("composeId", composeId);
  const one = await api("GET", `/api/compose.one?composeId=${composeId}`);
  console.log("name", one.name, "appName", one.appName, "status", one.composeStatus);

  const { map, order } = parseEnv(one.env || "");
  console.log("env keys before", [...map.keys()].sort().join(", "));

  // Production hardening
  set(map, "MOMENTRA_ENV", "production");
  set(map, "DEBUG", "false");
  map.delete("ALLOW_TEST_AUTH");

  // Ensure Supabase URL for storage derivation
  if (!map.get("SUPABASE_URL") && !map.get("STORAGE_PUBLIC_BASE_URL")) {
    // Prefer local .env SUPABASE_URL if Dokploy lacks both
    const localEnv = fs.readFileSync(path.join(__dirname, "..", ".env"), "utf8");
    const m = localEnv.match(/^SUPABASE_URL=(.+)$/m);
    if (m) set(map, "SUPABASE_URL", m[1].trim());
  }

  if (!map.get("STORAGE_PUBLIC_BASE_URL")) {
    const supabase = (map.get("SUPABASE_URL") || "").trim().replace(/\/$/, "");
    if (supabase.startsWith("https://")) {
      set(
        map,
        "STORAGE_PUBLIC_BASE_URL",
        `${supabase}/storage/v1/object/public/momentra`
      );
    }
  }

  // Ensure session secret ≥64 (keep existing long secret if present)
  const currentSecret =
    (map.get("APP_SESSION_SECRET") || map.get("JWT_SECRET") || "").trim();
  if (currentSecret.length < 48) {
    const crypto = require("crypto");
    const neu = crypto.randomBytes(48).toString("base64url");
    set(map, "APP_SESSION_SECRET", neu);
    console.log("Generated new APP_SESSION_SECRET len", neu.length);
  } else if (currentSecret.length < 64) {
    const crypto = require("crypto");
    const neu = crypto.randomBytes(48).toString("base64url");
    set(map, "APP_SESSION_SECRET", neu);
    console.log(
      "Rotated short secret to APP_SESSION_SECRET len",
      neu.length,
      "(old JWT_SECRET left in place)"
    );
  } else if (!map.get("APP_SESSION_SECRET") && map.get("JWT_SECRET")) {
    // promote existing long enough JWT if somehow ≥48
    set(map, "APP_SESSION_SECRET", map.get("JWT_SECRET"));
  }

  // CORS production allowlist (keep localhost only if already there; ensure www)
  const cors = (map.get("CORS_ORIGINS_STR") || "").trim();
  if (!cors || cors.includes("*")) {
    set(
      map,
      "CORS_ORIGINS_STR",
      "https://www.momentra.tech,https://momentra.tech"
    );
  } else {
    const parts = cors.split(",").map((s) => s.trim()).filter(Boolean);
    for (const need of ["https://www.momentra.tech", "https://momentra.tech"]) {
      if (!parts.includes(need)) parts.unshift(need);
    }
    set(map, "CORS_ORIGINS_STR", parts.join(","));
  }

  const envBody = serializeEnv(map, order);
  console.log("env keys after", [...map.keys()].sort().join(", "));
  console.log(
    "DEBUG=",
    map.get("DEBUG"),
    "MOMENTRA_ENV=",
    map.get("MOMENTRA_ENV"),
    "ALLOW_TEST_AUTH=",
    map.has("ALLOW_TEST_AUTH") ? map.get("ALLOW_TEST_AUTH") : "(removed)",
    "STORAGE set=",
    Boolean(map.get("STORAGE_PUBLIC_BASE_URL")),
    "SUPABASE set=",
    Boolean(map.get("SUPABASE_URL")),
    "APP_SESSION_SECRET len=",
    (map.get("APP_SESSION_SECRET") || "").length
  );

  await api("POST", "/api/compose.saveEnvironment", {
    composeId,
    env: envBody,
  });
  console.log("Environment saved.");

  await api("POST", "/api/compose.deploy", { composeId });
  console.log("Deploy triggered.");
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
