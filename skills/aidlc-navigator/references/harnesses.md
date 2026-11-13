# Harnesses: the same AI-DLC in seven tools

The methodology (phases, stages, agents, scopes, gates) is identical in every
harness. What differs is the shell: how questions render, whether there is a
status line, and how strongly hooks can enforce the workflow. Written against
AI-DLC 2.11.2. `R/` means `references/aidlc-workflows/`.

## Quick table

| Harness | Configure | Open | Invoke | Key prerequisites | Guide |
|---|---|---|---|---|---|
| Claude Code | `aidlc config --harness claude` | `claude` (from a terminal, in the project) | `/aidlc` | Signed in; trust the folder at first start | `R/docs/guide/01-getting-started.md` |
| Kiro IDE / Kiro CLI v3 | `aidlc config --harness kiro-ide` | Kiro IDE: choose **aidlc** in the chat agent picker. CLI: `kiro-cli` | `/aidlc` | Kiro IDE 1.1.70+ or Kiro CLI 2.24.1+; **Opus 4.8 (paid Kiro plan)**; trust the folder; reload the window | `R/docs/guide/harnesses/kiro-ide.md` |
| Kiro CLI (V2) | `aidlc config --harness kiro` | `kiro-cli chat` | `/aidlc` | Kiro CLI 2.6+, `kiro-cli login` | `R/docs/guide/harnesses/kiro-cli.md` |
| Codex CLI | `aidlc config --harness codex` | `codex` | **`$aidlc`** | 0.145.0+; **the project must be a git repo**; trust the project hooks; provider from `~/.codex/config.toml` | `R/docs/guide/harnesses/codex-cli.md` |
| Cursor | `aidlc config --harness cursor` | Cursor IDE, or `agent` (CLI) | `/aidlc` | Git repo recommended; trust the folder; a paid plan for named models | `R/docs/guide/harnesses/cursor.md` |
| opencode | `aidlc config --harness opencode` | `opencode` | `/aidlc` | 1.17+; provider and model from the global opencode config | `R/docs/guide/harnesses/opencode.md` |
| GitHub Copilot | `aidlc config --harness copilot` | Copilot CLI or VS Code chat | `/aidlc` | CLI 1.0.74+ / VS Code 1.130+; folder trust (CLI `trustedFolders`; VS Code workspace trust and **Chat: Use Hooks** on); `aidlc` on the host's PATH | `R/docs/guide/harnesses/copilot.md` |

Kiro note: `kiro-ide` is the right choice for both Kiro IDE and Kiro CLI on
its v3 engine (Kiro CLI 2.24.1+). `kiro` is the older Kiro CLI V2 surface. On
Kiro IDE, setup recommends turning Kiro's own *Workflows* feature off, because
while it is on, AI-DLC's reviews and helpers do not run.

## How strongly each harness enforces the workflow

A weaker row means AI-DLC relies more on the agent following instructions, and
a failure is easier to miss.

| Harness | Questions | Can AI-DLC refuse an agent's action? | Holds the turn at the end? | Status line |
|---|---|---|---|---|
| Claude Code | Native picker | Yes, every check | Yes | Yes (`/aidlc --statusline on`) |
| Codex CLI | Picker, numbered prose fallback | Yes, every check | Yes | Yes (project-wide setting) |
| GitHub Copilot | Numbered prose (type the answer) | Yes (verified live on the CLI) | Yes | No |
| Cursor | Numbered prose | Yes | No (reminder arrives as a follow-up); headless `agent -p` can't pass gates | No |
| Kiro CLI | Numbered prose | Yes | Yes when interactive | No |
| Kiro IDE | Numbered prose | Partly | No (relies on instructions) | No |
| opencode | Numbered prose | Yes | No (reminder sent as a new prompt) | No |

Without a status line, use `/aidlc --status` and the progress line at each gate.

**What "holds the turn: No" means in practice** (auditors ask this): when the
AI finishes a reply, the tool cannot force it to keep going until the current
step is reported. The run may pause mid-step, and the user resumes with
`/aidlc`. It does **not** let the AI approve anything for the user. Approvals
still require a human turn, which a hook records on every message the user
types (on Kiro IDE too), and the engine refuses an approval without one. What
remains is a liveness risk (a stalled run), not an approval risk. For regulated
teams, the backstop is a required PR review before merge.

**Kiro-specific caution:** Kiro IDE keeps agent memories outside the project
(`~/.kiro/memories/memories.db`) and can load them into every workspace. An old
memory can suggest unsafe workarounds (running a hook command by hand, setting
`AIDLC_SKIP_HUMAN_PRESENCE_GUARD=1`, turning summary confirmation off). Tell
Kiro users to refuse such suggestions. See
`R/docs/guide/harnesses/kiro-ide.md`.

Source: `R/docs/guide/facilitator-guide.md` ("How strongly each harness
enforces the workflow").

## Recommending a harness

- **The user already has a preferred tool → use it.** AI-DLC is built so
  teams keep their tool, and the methodology is the same everywhere.
- **No preference, or strict enforcement matters (regulated work,
  workshops):** Claude Code or Codex CLI enforce every check, hold the turn,
  and have a status line.
- **AWS / Kiro shops:** Kiro (`kiro-ide`) with Opus 4.8 on a paid plan.
- **Mixed team:** supported. Records live in the neutral `aidlc/` folder, and
  several harnesses can be configured in one project (each has its own engine
  folder).

## Where AI-DLC's onboarding lives in each harness

| Harness | Onboarding file the harness loads |
|---|---|
| Claude Code | `.claude/CLAUDE.md` |
| Kiro CLI / Kiro IDE | `.kiro/steering/aidlc-onboarding.md` |
| Codex CLI | `.codex/onboarding.md` |
| Cursor | `.cursor/rules/aidlc-onboarding.mdc` |
| opencode | `.aidlc/onboarding.md` |
| GitHub Copilot | root `AGENTS.md` |

## Model provider per harness

Provider setup belongs to the harness. AI-DLC keeps whatever the user already
uses. `aidlc config providers` can write Amazon Bedrock settings where the
harness supports it (Claude Code: env in the personal
`.claude/settings.local.json`). Credential detection is offline only: it never
calls AWS, so Bedrock model access and IAM permission remain pending actions that
`aidlc config providers --check` reports until the user marks them done with
`aidlc config providers --mark-done bedrock-model-access --yes`. Kiro needs no provider answer, because model access comes with Kiro.
Codex and opencode take the provider from their own global config.
