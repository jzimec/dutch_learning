#!/usr/bin/env bash
set -euo pipefail
# GitHub issue comments are durable across ephemeral Actions runners.
# This script is called only by a workflow with issues:write.
: "${GH_TOKEN:?GH_TOKEN required}"
: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY required}"
report="agent-supervisor-report.md"
test -s "$report"
title="Dutch Learning | Agent execution history"
number=$(gh issue list --repo "$GITHUB_REPOSITORY" --state open --limit 100 --json number,title --jq ".[] | select(.title == \"$title\") | .number" | head -n 1)
if [[ -z "$number" ]]; then
  url=$(gh issue create --repo "$GITHUB_REPOSITORY" --title "$title" --body "Automated supervisor history. Each comment is an immutable run snapshot; task completion still requires evidence.")
  number="${url##*/}"
fi
{
  printf '### Supervisor run %s\n\n' "${GITHUB_RUN_ID:-manual}"
  printf 'Workflow: %s\n\n' "${GITHUB_SERVER_URL:-https://github.com}/$GITHUB_REPOSITORY/actions/runs/${GITHUB_RUN_ID:-0}"
  cat "$report"
} > agent-issue-comment.md
gh issue comment "$number" --repo "$GITHUB_REPOSITORY" --body-file agent-issue-comment.md
echo "Appended supervisor report to issue #$number"
