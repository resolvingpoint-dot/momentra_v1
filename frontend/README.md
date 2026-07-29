This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Momentra API

Web uses the shared backend at `/api/v1` (not a separate `backend_v1`).

1. Start the API: `cd ../backend && ./run-dev.sh` (port **8002**)
2. Copy `web/.env.example` → `.env.local` and set Firebase + `NEXT_PUBLIC_API_BASE_URL=https://api.mallaapp.org`
3. Auth: Firebase sign-in → `POST api/v1/auth/firebase/exchange` → backend JWTs

See [`docs/API_INTEGRATION.md`](../docs/API_INTEGRATION.md) for client rollout and DTO porting from `ios/` / `apk/`.

## Empty-screen assets

Download Personal, Group, and Business design images into `public/` (and native copy targets):

```bash
# from web/
npm run bundle-empty-assets
# or
node scripts/bundle-context-empty-assets.mjs

# from repo root
node scripts/bundle-context-empty-assets.mjs
```

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

Marketing (`/`) and the product app (`/app`) deploy together as one Next.js project.

1. Import this repo in [Vercel](https://vercel.com/new)
2. Set **Root Directory** to `web`
3. Copy env vars from [`.env.example`](.env.example) into the Vercel project
4. Deploy — details in [`VERCEL.md`](./VERCEL.md)

```bash
npm run build && npm start   # local production check
```
