/**
 * Deploy Momentra api+worker+beat+redis as a Dokploy Compose app using a browser session.
 */
const fs = require("fs");
const path = require("path");

const SESSION = JSON.parse(
  fs.readFileSync(path.join(__dirname, "dokploy-session.json"), "utf8")
);
const DOKPLOY = SESSION.dokployUrl.replace(/\/$/, "");
const COOKIE = SESSION.cookies
  .map((c) => `${c.name}=${decodeURIComponent(c.value)}`)
  .join("; ");
// better-auth may expect the raw cookie value as stored (URL-encoded). Prefer original.
const COOKIE_RAW = SESSION.cookies.map((c) => `${c.name}=${c.value}`).join("; ");

const COMPOSE_NAME = "momentra-stack";
const DOMAIN = "api.mallaapp.org";
const COMPOSE_FILE = fs.readFileSync(
  path.join(__dirname, "..", "docker-compose.yml"),
  "utf8"
);

async function api(method, apiPath, body) {
  const headers = {
    accept: "application/json",
    cookie: COOKIE_RAW,
  };
  if (body !== undefined) {
    headers["content-type"] = "application/json";
  }
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
  if (!res.ok) {
    const err = new Error(`${method} ${apiPath} -> ${res.status}: ${text.slice(0, 500)}`);
    err.status = res.status;
    err.body = json;
    throw err;
  }
  return json;
}

function buildEnvFromLocal() {
  const envPath = path.join(__dirname, "..", ".env");
  if (!fs.existsSync(envPath)) return null;
  const lines = fs
    .readFileSync(envPath, "utf8")
    .split(/\r?\n/)
    .filter((line) => {
      if (!line.trim() || line.trim().startsWith("#")) return false;
      if (/^\s*REDIS_URL\s*=/.test(line)) return false;
      if (/^\s*CELERY_BROKER_URL\s*=/.test(line)) return false;
      if (/^\s*CELERY_RESULT_BACKEND\s*=/.test(line)) return false;
      if (/^\s*ALLOW_TEST_AUTH\s*=/.test(line)) return false;
      return true;
    });
  // Force production-safe defaults for compose
  const forced = [
    "DEBUG=false",
    "# REDIS forced in docker-compose.yml to redis://redis:6379/0",
  ];
  return [...forced, ...lines].join("\n") + "\n";
}

(async () => {
  console.log("Dokploy", DOKPLOY);
  const projects = await api("GET", "/api/project.all");
  const project = projects.find((p) => p.name === "momentra") || projects[0];
  const env = project.environments[0];
  const environmentId = env.environmentId;
  console.log("project", project.name, "environmentId", environmentId);

  // Prefer copying env from existing Dockerfile application if present
  let envBody = buildEnvFromLocal();
  const backendApp = (env.applications || []).find(
    (a) => a.name === "backend" || a.name.includes("backend")
  );
  if (backendApp) {
    try {
      const one = await api(
        "GET",
        `/api/application.one?applicationId=${backendApp.applicationId}`
      );
      if (one.env && String(one.env).trim()) {
        console.log("Copying env from application", backendApp.name);
        const cleaned = String(one.env)
          .split(/\r?\n/)
          .filter(
            (line) =>
              !/^\s*REDIS_URL\s*=/.test(line) &&
              !/^\s*CELERY_BROKER_URL\s*=/.test(line) &&
              !/^\s*CELERY_RESULT_BACKEND\s*=/.test(line) &&
              !/^\s*ALLOW_TEST_AUTH\s*=/.test(line)
          )
          .join("\n");
        envBody = cleaned + "\n";
      }
      console.log("Existing app status", one.applicationStatus, "appName", one.appName);
    } catch (e) {
      console.warn("Could not read application.one:", e.message);
    }
  }

  let composeId = null;
  for (const c of env.compose || []) {
    if (c.name === COMPOSE_NAME) composeId = c.composeId;
  }
  // refresh compose list via project.all again after create
  if (!composeId) {
    console.log("Creating compose", COMPOSE_NAME);
    const created = await api("POST", "/api/compose.create", {
      name: COMPOSE_NAME,
      environmentId,
      composeType: "docker-compose",
      appName: "momentra-stack",
    });
    composeId = created.composeId || created.id;
    if (!composeId) {
      // re-list
      const again = await api("GET", "/api/project.all");
      const env2 = again.find((p) => p.projectId === project.projectId).environments[0];
      const hit = (env2.compose || []).find((c) => c.name === COMPOSE_NAME);
      composeId = hit && hit.composeId;
    }
  }
  if (!composeId) throw new Error("No composeId after create");
  console.log("composeId", composeId);

  console.log("Updating compose file (raw)");
  await api("POST", "/api/compose.update", {
    composeId,
    name: COMPOSE_NAME,
    composeType: "docker-compose",
    sourceType: "raw",
    composeFile: COMPOSE_FILE,
    composePath: "./docker-compose.yml",
  });

  if (envBody) {
    console.log("Saving environment (" + envBody.split("\n").length + " lines)");
    await api("POST", "/api/compose.saveEnvironment", {
      composeId,
      env: envBody,
    });
  } else {
    console.warn("No env body — set Environment in Dokploy UI");
  }

  // Domain
  try {
    const one = await api("GET", `/api/compose.one?composeId=${composeId}`);
    const domains = one.domains || [];
    const has = domains.some((d) => d.host === DOMAIN);
    if (!has) {
      console.log("Creating domain", DOMAIN, "-> api:8000");
      await api("POST", "/api/domain.create", {
        host: DOMAIN,
        path: "/",
        port: 8000,
        https: false,
        composeId,
        serviceName: "api",
      });
    } else {
      console.log("Domain already present", DOMAIN);
    }
  } catch (e) {
    console.warn("Domain step:", e.message);
  }

  // Stop old single-container app so Host doesn't conflict (best-effort)
  if (backendApp) {
    try {
      console.log("Stopping old Dockerfile application", backendApp.applicationId);
      await api("POST", "/api/application.stop", {
        applicationId: backendApp.applicationId,
      });
    } catch (e) {
      console.warn("Stop old app:", e.message);
    }
  }

  console.log("Deploying compose...");
  await api("POST", "/api/compose.deploy", { composeId });
  console.log("Deploy triggered.");
  fs.writeFileSync(
    path.join(__dirname, "dokploy-compose-id.txt"),
    composeId + "\n"
  );
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
