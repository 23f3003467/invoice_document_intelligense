# Document Intelligence — Next.js Frontend

Talks to the FastAPI backend from the earlier `docintel` project. Run both at once.

## Structure

```
app/
  layout.tsx     root layout, imports globals.css
  page.tsx       the whole UI: upload, result view, history table
  api.ts         typed fetch calls to the FastAPI backend
  types.ts       TypeScript types mirroring the backend's Pydantic models
  globals.css    styling
.env.local       API base URL (points at your local backend)
```

## Setup

You'll need Node.js 18+ installed.

```bash
npm install
```

`.env.local` already points at `http://127.0.0.1:8000` — change it if your
backend runs somewhere else.

## Run

**Terminal 1 — backend** (from your `docintel` project folder):
```bash
uvicorn main:app --reload
```

**Terminal 2 — frontend** (from this folder):
```bash
npm run dev
```

Open **http://localhost:3000**.

## Why a separate `api.ts` / `types.ts`

Keeping the fetch calls and types out of `page.tsx` is a habit worth building
early: as soon as you add a second page (e.g. a `/documents/[id]` review page),
you reuse these instead of copy-pasting fetch logic. It also means if the
backend's response shape changes, you fix it in one place.

## Where to take it from here

- Add a `/documents/[id]` page so a flagged document can be reviewed/corrected
- Add loading skeletons instead of the plain "Processing…" text
- Move the CORS `allow_origins` on the backend from `"*"` to `"http://localhost:3000"`
  once you're not testing from multiple origins anymore
- Deploy: frontend to Vercel, backend to Railway/Render/Fly — two separate deploys,
  linked by `NEXT_PUBLIC_API_BASE`
