# Plan: AI Task Orchestrator

## Concept
A script that picks GitHub Issues (tickets) and spawns AI coding agents (Claude Code, Codex, etc.) to work on them autonomously. Each agent works in an isolated git worktree and creates a PR when done.

## Flow
1. You create GitHub Issues with labels (`backlog`, `feature`, `bug`, `enhancement`)
2. Run `python scripts/orchestrate.py` (or eventually a cron/daemon)
3. Script picks 1-3 issues labeled `backlog`
4. For each issue:
   - Creates a git worktree branch (`feat/issue-123-description`)
   - Spawns a Claude Code (or Codex) agent in that worktree
   - Passes the issue title + body as the task prompt
   - Moves the issue label to `in-progress`
5. Agent works: reads code, makes changes, commits
6. Agent creates a PR linked to the issue
7. Script moves issue label to `in-review`
8. You review the PR, merge, issue auto-closes

## Tech Stack
- **Ticket backend**: GitHub Issues + Labels (free, no API keys needed)
- **CLI**: `gh` for issue/PR management
- **Agent runner**: Claude Code CLI (`claude --worktree`) or Codex CLI
- **Isolation**: git worktrees — each agent gets its own copy of the repo
- **Orchestrator**: Python script in `scripts/orchestrate.py`

## Key Design Decisions
- **Model selection**: flag to choose Claude Code vs Codex per ticket
- **Context**: auto-inject relevant CLAUDE.md + file paths from issue body
- **Parallelism**: run N agents concurrently (each in own worktree)
- **Safety**: agents can only push to feature branches, never main
- **Monitoring**: log agent output, detect stalls/failures

## Phase 1 — Manual (local machine)
- `orchestrate.py --pick 3` picks 3 backlog issues
- Spawns agents sequentially or in parallel
- Creates PRs
- You review and merge

## Phase 2 — Scheduled (VPS or CI)
- GitHub Action on schedule (every hour, check for new backlog issues)
- Or cron on VPS running the orchestrator
- Slack/email notification when PR is ready for review

## Phase 3 — Multi-model
- Route different ticket types to different models
- Bug fixes → Claude Code (good at reading existing code)
- New features → Codex (good at greenfield generation)
- Config based: label `use:codex` or `use:claude`

## First Steps
1. Set up GitHub Projects board for the screener repo (Backlog, In Progress, In Review, Done)
2. Create a few test issues
3. Build `orchestrate.py` — picks issues via `gh`, spawns Claude Code
4. Test with one simple ticket
