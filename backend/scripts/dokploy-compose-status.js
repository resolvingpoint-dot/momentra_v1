const fs = require("fs");
const path = require("path");
const SESSION = JSON.parse(
  fs.readFileSync(path.join(__dirname, "dokploy-session.json"), "utf8")
);
const DOKPLOY = SESSION.dokployUrl.replace(/\/$/, "");
const COOKIE_RAW = SESSION.cookies.map((c) => `${c.name}=${c.value}`).join("; ");
const composeId = fs.readFileSync(path.join(__dirname, "dokploy-compose-id.txt"), "utf8").trim();

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
  if (!res.ok) throw new Error(`${res.status} ${text.slice(0, 400)}`);
  return json;
}

(async () => {
  const one = await api("GET", `/api/compose.one?composeId=${composeId}`);
  console.log(
    JSON.stringify(
      {
        name: one.name,
        composeStatus: one.composeStatus,
        appName: one.appName,
        domains: (one.domains || []).map((d) => ({
          host: d.host,
          port: d.port,
          serviceName: d.serviceName,
        })),
      },
      null,
      2
    )
  );
  try {
    const deps = await api("GET", `/api/deployment.all?composeId=${composeId}`);
    const list = Array.isArray(deps) ? deps : deps || [];
    console.log(
      "deployments",
      (list.slice ? list.slice(0, 3) : list).map
        ? (list.slice ? list.slice(0, 3) : []).map((d) => ({
            status: d.status,
            title: d.title,
            createdAt: d.createdAt,
          }))
        : list
    );
  } catch (e) {
    console.log("deployment.all", e.message);
  }
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
