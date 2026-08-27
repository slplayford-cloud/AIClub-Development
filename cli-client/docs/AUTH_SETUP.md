# Auth setup — Google sign-in (one-time, officers only)

Members sign in with their `@nd.edu` Google account. No passwords, no emails, no
SMTP. This document is the one-time setup an officer does in Google Cloud and the
Supabase dashboard. Members never see any of this — they just run `aiclub login`.

## How the login works (context)

```
aiclub login
  → opens browser to Google  (restricted to @nd.edu via the `hd` hint)
  → Google → Supabase (/auth/v1/callback)
  → Supabase → http://localhost:8765/?code=...   (CLI's local server catches this)
  → CLI exchanges the code for a session (PKCE) and caches it
```

Domain enforcement is server-side: a Postgres trigger on `auth.users` rejects any
non-`@nd.edu` account (see `supabase/001_members.sql`).

## Step 1 — Run the database SQL

Supabase dashboard → **SQL Editor** → **New query** → paste all of
`supabase/001_members.sql` → **Run**. (Safe to re-run.)

## Step 2 — Create Google OAuth credentials

1. Go to <https://console.cloud.google.com> → create/select a project.
2. **APIs & Services → OAuth consent screen**: choose **Internal** (limits to your
   Google Workspace / nd.edu) if available, otherwise **External**. Fill in the app
   name and support email.
3. **APIs & Services → Credentials → Create Credentials → OAuth client ID**:
   - Application type: **Web application**
   - **Authorized redirect URI**: your Supabase callback —
     `https://jvmwnlioqpvievgalieu.supabase.co/auth/v1/callback`
   - Create, then copy the **Client ID** and **Client secret**.

## Step 3 — Enable Google in Supabase

Supabase dashboard → **Authentication → Sign In / Providers → Google**:
- Toggle **Enable**.
- Paste the **Client ID** and **Client secret** from Step 2.
- Save.

## Step 4 — Allow the CLI's localhost redirect

Supabase dashboard → **Authentication → URL Configuration → Redirect URLs** →
**Add URL**:

```
http://localhost:8765
```

(This is the fixed port the CLI listens on. Must match exactly.)

## Step 5 — Test

```bash
uv run aiclub login      # pick your @nd.edu account in the browser
uv run aiclub whoami     # should show your email + name + "member since"
uv run aiclub logout
```

Confirm in the dashboard: **Authentication → Users** has your account, and
**Table Editor → members** has your row (with `full_name` from your Google profile).

## Notes / troubleshooting

- **"redirect_to is not allowed"** → Step 4 URL doesn't exactly match `http://localhost:8765`.
- **Non-nd.edu account rejected** → expected; the domain trigger blocked it. The
  browser will show a sign-in error and the CLI reports it.
- **Port 8765 in use** → a previous login didn't finish; wait a moment and retry.
- The Client **secret** lives only in the Supabase dashboard — it is never shipped
  in the CLI.
