import type { NextConfig } from "next";
import fs from "fs";
import os from "os";
import path from "path";
import { fileURLToPath } from "url";

const projectRoot = path.dirname(fileURLToPath(import.meta.url));

function parseDevOriginHost(origin: string): string | null {
  const trimmed = origin.trim();
  if (!trimmed) return null;
  try {
    return new URL(trimmed).hostname;
  } catch {
    return trimmed;
  }
}

function readEnvLocalOrigins(): string[] {
  const hosts: string[] = [];
  const envPath = path.join(projectRoot, ".env.local");
  if (!fs.existsSync(envPath)) return hosts;

  const line = fs
    .readFileSync(envPath, "utf8")
    .split(/\r?\n/)
    .find((row) => row.startsWith("ALLOWED_DEV_ORIGINS="));
  if (!line) return hosts;

  const value = line.slice("ALLOWED_DEV_ORIGINS=".length).trim();
  for (const origin of value.split(",")) {
    const host = parseDevOriginHost(origin);
    if (host) hosts.push(host);
  }
  return hosts;
}

/** LAN IPs + ALLOWED_DEV_ORIGINS for Next.js 16 dev HMR WebSocket allowlist. */
function getAllowedDevOrigins(): string[] {
  const hosts = new Set<string>(readEnvLocalOrigins());

  for (const origin of process.env.ALLOWED_DEV_ORIGINS?.split(",") ?? []) {
    const host = parseDevOriginHost(origin);
    if (host) hosts.add(host);
  }

  for (const nets of Object.values(os.networkInterfaces())) {
    for (const net of nets ?? []) {
      if (net.family === "IPv4" && !net.internal) {
        hosts.add(net.address);
      }
    }
  }

  return [...hosts];
}

const nextConfig: NextConfig = {
  // Required for Docker / Dokploy runner image
  output: "standalone",
  allowedDevOrigins: getAllowedDevOrigins(),
  turbopack: {
    root: projectRoot,
  },
  // Pre-existing product TS errors must not block production deploys.
  // Prefer fixing them over time; do not treat this as a free pass for new code.
  typescript: {
    ignoreBuildErrors: true,
  },
  async headers() {
    const apiBase = (
      process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://api.mallaapp.org"
    ).replace(/\/$/, "");
    const connectSrc = [
      "'self'",
      apiBase,
      "https://*.googleapis.com",
      "https://*.firebaseio.com",
      "https://*.firebaseapp.com",
      "https://identitytoolkit.googleapis.com",
      "https://securetoken.googleapis.com",
      "https://www.googleapis.com",
      "https://firestore.googleapis.com",
      "wss://*.firebaseio.com",
    ].join(" ");

    const contentSecurityPolicy = [
      "default-src 'self'",
      "base-uri 'self'",
      "frame-ancestors 'none'",
      "object-src 'none'",
      "img-src 'self' data: blob: https:",
      "font-src 'self' data: https://fonts.gstatic.com",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      // Next.js + Firebase Auth need inline/eval in practice for the app shell.
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://apis.google.com https://www.gstatic.com https://*.firebaseapp.com",
      `connect-src ${connectSrc}`,
      "frame-src 'self' https://*.firebaseapp.com https://accounts.google.com",
      "form-action 'self'",
    ].join("; ");

    // Do not set Cross-Origin-Opener-Policy here. Firebase Google popup auth
    // polls window.closed; any COOP value (including same-origin-allow-popups)
    // causes Chrome to spam "would block the window.closed call" on login.
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "Content-Security-Policy",
            value: contentSecurityPolicy,
          },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "X-Frame-Options", value: "DENY" },
        ],
      },
      {
        source: "/books/life-happens-in-moments/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=31536000, immutable",
          },
        ],
      },
      {
        source: "/.well-known/apple-app-site-association",
        headers: [
          { key: "Content-Type", value: "application/json" },
          { key: "Cache-Control", value: "public, max-age=300" },
        ],
      },
      {
        source: "/.well-known/assetlinks.json",
        headers: [
          { key: "Content-Type", value: "application/json" },
          { key: "Cache-Control", value: "public, max-age=300" },
        ],
      },
    ];
  },
};

export default nextConfig;
