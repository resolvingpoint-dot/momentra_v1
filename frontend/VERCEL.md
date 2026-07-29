# Vercel deployment (marketing + `/app`)

This Next.js app ships **marketing (`/`)** and the **product (`/app`)** in one Vercel project.

## Prerequisites

- Vercel account linked to this Git repo
- Env vars from [`.env.example`](.env.example) set in the Vercel project
- Public API host for `NEXT_PUBLIC_API_BASE_URL` (not a local ngrok tunnel)

## Project settings

| Setting | Value |
|---|---|
| Root Directory | `web` |
| Framework | Next.js |
| Install Command | `npm ci` |
| Build Command | `npm run build` |
| Output | Default (do not set OpenNext / Workers) |

## Env vars

Set these in **Project → Settings → Environment Variables** for Production (and Preview if needed):

```
NEXT_PUBLIC_FIREBASE_API_KEY
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
NEXT_PUBLIC_FIREBASE_PROJECT_ID
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
NEXT_PUBLIC_FIREBASE_APP_ID
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID
NEXT_PUBLIC_GOOGLE_WEB_CLIENT_ID
NEXT_PUBLIC_API_BASE_URL
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
```

Optional local-only:

```
ALLOWED_DEV_ORIGINS
```

## Custom domain

1. **Project → Settings → Domains** → add `momentra.tech` (or your domain).
2. Follow Vercel’s DNS instructions (A/CNAME at your DNS host, or move nameservers to Vercel).

After deploy:

- `https://your-domain/` — marketing
- `https://your-domain/app` — product app

## Resend DNS (email)

If the domain’s DNS is managed in Vercel, add Resend’s MX/TXT/DKIM records under **Domains → DNS**, or use Resend **Auto Configure**.  
If DNS still lives on Cloudflare (or another registrar), add Resend records there — not in the Next.js app.

## Local

```bash
npm install
npm run dev
npm run build && npm start   # production-like check
```

## Note on the marketing-only repo

[`monytix0-hue/momentra_website`](https://github.com/monytix0-hue/momentra_website) was a marketing-only deploy. Point the production domain at **this** Vercel project when you are ready so `/app` works on the same host.
