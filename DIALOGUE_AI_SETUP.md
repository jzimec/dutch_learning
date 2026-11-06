# Dialogue AI judging (Supabase + OpenAI)

The GitHub Pages app continues to host all learning screens. Only the Dialogue "检查回答" action calls the server.

## Setup (one-time)

1. In your Supabase project, create an Edge Function named `dialogue-check` from `supabase/functions/dialogue-check/index.ts`, then deploy it.
2. Under Supabase **Edge Functions > Secrets**, set:
   - `OPENAI_API_KEY`: your OpenAI API key (secret; never commit it).
   - `DIALOGUE_AI_ACCESS_TOKEN`: generate a long random token (32+ characters). This is a *separate* access token used to prevent unrestricted paid API calls. Never commit it.
   - Optional: `OPENAI_MODEL` (default `gpt-4o-mini`).
3. Deploy with JWT verification **off** for this function, matching `supabase/config.toml`. The function enforces the independent long access token. Do not deploy it publicly with the token check disabled.
4. In public GitHub file `dialogue-ai-config.js`, set your function URL:
   `https://YOUR_PROJECT_REF.supabase.co/functions/v1/dialogue-check`.
   This URL is public configuration (not a secret).
5. Open Dialogue and press "检查回答". The first check will ask for the **Dialogue AI access token**. It is stored in this tab's sessionStorage only. Do not give this token to others.
6. Try a free sentence using the target word. AI will assess grammar, task match, and naturalness and return Chinese explanations and a Dutch correction when needed.

Notes:
- No API key or private token is stored in the GitHub repository.
- Edge Functions incur usage; OpenAI API calls can cost money.
- This per-session access token is suitable for the owner's personal/hobby use, not for selling a public service. Before allowing broad access, add proper account authentication, per-user quotas and server-side rate limits.
- Until backend setup is complete, Dialogue keeps its existing **offline** checker and clearly labels it as offline.
- Voice mode evaluates the transcribed Dutch sentence, **not** pronunciation quality.
