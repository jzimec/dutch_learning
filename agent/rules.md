# Dutch Learning autonomous development rules

- Work only on the designated development branch. Never push directly to `main` or auto-merge.
- Make minimal scoped changes. Do not change unrelated modules, layout, vocabulary, stories, or translations.
- Read source before editing; never replace an unreadable/oversized file with guessed content.
- Do not bypass Supabase Row Level Security (RLS, 行级安全策略), approval checks, or authentication.
- Never log or commit service-role keys, API secrets, user passwords, or private learning records.
- Verify syntax and run relevant tests before claiming a task complete. If tests cannot run, mark `unverified`.
- Each run must publish an auditable GitHub Actions summary with completed tasks, commits, tests, blockers and next steps.
- Stop and mark blocked on repeated failures; do not loop indefinitely.
- Human review is required for database migrations, credential changes, production deployment and merging to main.
- Tasks are tracked in `agent/tasks.json`; automation does not silently change priorities or declare tasks done.
