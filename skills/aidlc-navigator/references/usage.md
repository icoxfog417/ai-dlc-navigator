# Using AI-DLC: from install to a confident first week

Summary for the navigator, written against AI-DLC 2.11.2. `R/` means
`references/aidlc-workflows/`. Walk the user through one step at a time.

## Contents

1. Before you start
2. Install
3. Configure a project
4. What setup writes, and what to commit
5. Check it with `aidlc doctor`
6. Start a workflow
7. During a run: what you will see
8. Everyday commands
9. Sessions: resume, park, new chat, model changes
10. The five-run learning path (recommended for newcomers)
11. "It's stuck": what is really happening
12. Updating
13. Bigger work and teams

---

## 1. Before you start

- A harness (coding tool) installed and signed in: Claude Code, Kiro IDE /
  Kiro CLI, Codex CLI (0.145.0+), Cursor, opencode (1.17+), or GitHub Copilot
  (CLI 1.0.74+ / VS Code 1.130+).
- **Git**: needed for Codex CLI (it only finds project hooks in a git repo)
  and recommended for Cursor. Recommended for everyone, because the `aidlc/`
  records travel by git. If the project isn't a git repo yet, run `git init`
  in it first.
- Nothing else. The native installer brings everything, so Bun and Node.js are
  not needed.
- A capable reasoning model. The recommendation is **Claude Opus 4.8** (see
  `settings.md` §3).

## 2. Install (the user runs this; don't run it yourself)

macOS, Linux, or WSL:

```bash
curl -fsSL https://github.com/awslabs/aidlc-workflows/releases/latest/download/install.sh | sh
```

Windows PowerShell (a normal window, **not** "Run as administrator"):

```powershell
irm https://github.com/awslabs/aidlc-workflows/releases/latest/download/install.ps1 | iex
```

- It installs the native `aidlc` command plus every harness runtime ("all
  harness runtimes" means support for every AI coding tool AI-DLC works with), verified
  by SHA-256 (plus signed provenance when a recent GitHub CLI is present).
- If `aidlc` is not found afterwards: on macOS/Linux, run the `export PATH=...`
  line the installer printed and add it to the shell startup file. On Windows,
  quit and reopen the terminal or IDE completely (a new tab is not enough).
- Check: `aidlc version` → `aidlc X.Y.Z (runtime X.Y.Z)`.
- To download and inspect the script before running it, see
  `R/docs/guide/harnesses/README.md` ("Install first").
- Alternatives (pinning, offline, mirrors, the copy channel without the native
  binary): `R/docs/guide/18-install-and-lifecycle.md`.

## 3. Configure a project

From the project root (AI-DLC does **not** search upward for a git root; the
`aidlc/` folder is created in this folder). For a newcomer, the project root is
the folder the current conversation is open in (see SKILL.md, "Where to run AI-DLC"):

```bash
cd /path/to/your-project
aidlc config            # interactive wizard
# or: aidlc config --harness claude   (kiro-ide, kiro, codex, cursor, opencode, copilot)
```

Nothing is written before the user answers. The wizard first shows what it
detected (harness, git repo, AWS credentials, PATH) and offers:

1. **Yes, use recommended defaults**: MCP servers on, all plugins, current
   model provider preserved, `balanced` effort preset.
2. **No, customize step by step**: six steps (harness → model provider →
   effort preset → plugins → MCP → where to record the preset).
3. **Exit**, with nothing written.

For first-timers, choice 1 is right almost always. `settings.md` explains each
customize step and when to deviate. On Claude Code it then asks about the
status line (recommended: **Yes**).

Preview without writing: `aidlc config --harness <name> --dry-run` (the
navigator may run this; add `--project-dir <root>` when the folder isn't set up
yet or the command runs from another directory). Non-interactive or CI:
`aidlc config --harness claude --mcp defaults --yes`.

## 4. What setup writes, and what to commit (Claude Code example)

| Path | What | Commit? |
|---|---|---|
| `.claude/` | The engine for this harness: `/aidlc` skill, agents, stages, hooks, settings | Yes |
| `aidlc/` | AI-DLC's records: rules (`spaces/default/memory/`), and later every intent | Yes |
| `.gitignore` | AI-DLC adds its own marked block | Yes |
| `.mcp.json` | MCP servers, if chosen | Yes (never put secrets in it) |
| `aidlc.settings.json` | The model effort preset | Yes |
| `aidlc.settings.local.json`, `.claude/settings.local.json` | Personal choices (status line, Bedrock env) | No (git-ignored) |

Other harnesses use their own engine folder (`.kiro/`, `.codex/`, `.cursor/`,
`.aidlc/` + `.opencode/`, `.aidlc/` + `.github/`). The records are always in
`aidlc/`.

```bash
git add .claude aidlc .gitignore .mcp.json aidlc.settings.json && git commit -m "Set up AI-DLC"
```

Re-running `aidlc config` later refreshes the files from the installed release
and keeps the user's edits.

## 5. Check it with `aidlc doctor` (safe for the navigator to run)

```bash
aidlc doctor            # or /aidlc --doctor inside the harness
aidlc doctor --verbose  # every check
```

- `fail` rows are real problems, and each comes with a `fix:` line.
- On a brand-new project, these **warnings are expected**: hooks have not run
  yet (it clears after the first chat), uncommitted records under `aidlc/`
  (it clears after committing), and on Linux a "Runtime hook PATH" warning that
  matters only if the harness is started from a desktop icon rather than a
  terminal.

## 6. Start a workflow

Open the harness **in the project folder** (restart it if it was already open
during setup; in Claude Code, a new conversation is enough):

| Harness | Open | Invoke |
|---|---|---|
| Claude Code | `claude` (answer **Yes, I trust this folder** for your own project) | `/aidlc` |
| Kiro IDE / Kiro CLI v3 | Kiro IDE: choose **aidlc** in the chat agent picker. CLI: `kiro-cli` | `/aidlc` |
| Kiro CLI (V2) | `kiro-cli chat` | `/aidlc` |
| Codex CLI | `codex` (trust the project hooks) | `$aidlc` |
| Cursor | Cursor IDE, or `agent` | `/aidlc` |
| opencode | `opencode` | `/aidlc` |
| GitHub Copilot | Copilot CLI or VS Code chat | `/aidlc` |

Three ways to start:

```text
/aidlc Build a REST API for inventory management     # describe it; AI-DLC proposes a plan
/aidlc express Build a Celsius/Fahrenheit CLI        # name a profile + the work; starts right away
/aidlc compose "harden the deploy pipeline"          # ask the composer for a tailored plan
```

When you describe the work, AI-DLC proposes a plan (for example "mvp - 19
stages, 19 approval gates") with **Go ahead**, **Use a different plan**, or
**Tailor a plan to this task**. Nothing starts until you confirm.

Users can write the description in their own language. AI-DLC continues in it.

## 7. During a run: what you will see

1. **Initialization** runs automatically (3 stages, under a second, no gate).
2. **The route is announced**: stage count and approval-gate count.
3. **Answer mode** (asked once per piece of work): **Guide me** / **I'll edit
   the file** / **Chat**. Questions are saved in a `*-questions.md` file under
   the record dir. With Guide me, answers are read back for one confirmation
   before anything is written.
4. **The stage works**. Reviewers may check the output (except in `express`).
   The agent may ask "Keep that for next time?" after you corrected it (the
   learning loop).
5. **Approval gate**: read the summary, then choose **Approve** or **Request
   Changes** (with a concrete instruction). You may also change depth or scope,
   add a skipped stage back (Ideation and Inception), or jump.
6. **Construction**: you approve each Unit's **code plan** before it is built
   (Plan Approval), confirm the verification command once, and choose
   **Continue automatically** or **Review each checkpoint** for routine Unit
   checkpoints. Failures always stop.
7. Repeat until the run completes.

**Progress**: on Claude Code, the AI-DLC status line (if turned on). Elsewhere,
`/aidlc --status` (`$aidlc --status` on Codex) and the progress line at each
gate.

## 8. Everyday commands (Codex uses `$aidlc` instead of `/aidlc`)

| Command | Use it to |
|---|---|
| `/aidlc` | Resume the open workflow (or start one if none exists) |
| `/aidlc --status` | See where you are (read-only) |
| `/aidlc --doctor` | Health check |
| `/aidlc --help` / `--version` | Usage / version |
| `/aidlc park` | Pause at a stage boundary for later or for someone else |
| `/aidlc --resume` | Continue a parked or interrupted workflow |
| `/aidlc --stage <name>` / `--phase <name>` | Jump (stages passed over are marked skipped; jumping back reopens) |
| `/aidlc --stage <name> --single` | Run one stage alone, without moving the workflow |
| `/aidlc --scope <name>` | Change the scope of the active work |
| `/aidlc --depth minimal\|standard\|comprehensive` | Fewer or more questions and detail |
| `/aidlc --test-strategy minimal\|standard\|comprehensive` | Fewer or more tests |
| `/aidlc intent` | List or switch pieces of work |
| `/aidlc config list` | See all 13 workflow settings for the active work |
| `/aidlc --config` | Change project configuration conversationally |

Plain words work too: "let me edit the file this time", "use minimal depth",
"jump back to requirements". The full list is in
`R/docs/guide/12-cli-commands.md` ("Quick Reference").

## 9. Sessions: resume, park, new chat, model changes

- Running bare `/aidlc` in a new session continues where the work stopped and
  re-asks any unanswered question. You can say "redo this stage", "jump to X",
  or "start fresh" at any time.
- State lives on disk (`aidlc-state.md` + audit), so context compaction or a
  crash loses nothing that was approved.
- To change the model or effort: do it **between stages, in a new chat**, then
  run `/aidlc` (see `R/docs/guide/11-session-management.md`, "Changing Model
  Mid-Workflow").

## 10. The five-run learning path (recommended for newcomers)

Do Runs 1 to 4 in the folder this conversation is open in, not in a
throwaway folder (the official onboarding uses `/tmp/aidlc-hello`). The user can
then ask the navigator questions in the same conversation as `/aidlc`. Each run
adds one idea. Runs 2 and 3 are new intents in the same project: when AI-DLC
asks what to do with the new request, choose **Separate new piece of work**.
The earlier intent stays as it was. For a user short on time, Run 1 is one
copy-paste block: `cd` to the root, `git init` if needed,
`aidlc config --harness <h>` (choose the recommended defaults), start a new
conversation, and run `/aidlc express ...`.

| Run | Do | Learn |
|---|---|---|
| 1 (about 15 min) | In the project root: `aidlc config --harness <h>`, a new conversation, then `/aidlc express Build a CLI that converts Celsius and Fahrenheit` | The ask → stage → gate → next loop. You only answer gates; the engine routes. |
| 2 | Same idea as a new intent with `/aidlc poc ...` (choose **Separate new piece of work**) | Scope (not skipping by hand) changes the route |
| 3 | `/aidlc poc ...` again, and at the first gate choose **Request Changes** ("success criteria need a target date") | A gate is a two-way door; reviewer finding IDs stay stable |
| 4 | Open `aidlc/spaces/default/intents/<newest>/`: `aidlc-state.md` (`[x]` done, `[S]` skipped), phase folders, an `audit/` shard | Where the "why" lives on disk |
| 5 | In a real project: `/aidlc feature <real feature>` | The full lifecycle, now with a mental model |

Checklist: can state the engine/conductor split in one sentence, has done an
`express` run, has seen scope change the route, has used Request Changes, has
found an audit shard, and has run a real `feature`.

Source: `R/docs/guide/onboarding.md`. Annotated full run:
`R/docs/guide/02-your-first-workflow.md`. Worked bugfix and feature examples:
`R/docs/guide/16-worked-examples.md`.

## 11. "It's stuck": what is really happening

| Symptom | Real cause | What to do |
|---|---|---|
| "It stopped and won't continue." | An approval gate is waiting | Read the summary; **Approve** or **Request Changes** |
| "It won't just write the code." | Construction needs earlier inputs | Let the earlier stages run, or pick a smaller scope |
| "Way too many steps." | The scope is bigger than the task | Restart with `express`, `poc`, or `bugfix` |
| "Too many questions." | Depth | `/aidlc --depth minimal` (about 2 to 4 questions per stage) |
| "Which stage am I on?" | — | Status line, or `/aidlc --status` |
| "Where did that decision go?" | — | The record dir and its `audit/` shards |
| Every agent command is refused, or the same step repeats | A fault below the workflow (hook not running, a check refusing in error) | Stop the agent, run `aidlc doctor --export` in a terminal, and follow `R/docs/guide/facilitator-guide.md` ("Recovery playbook") |
| `aidlc` not found | PATH | See §2 |
| Codex hooks don't run | Hooks not trusted | `R/docs/guide/harnesses/codex-cli.md` |
| Bedrock access fails (AccessDenied, model not found) | Model access not enabled in that region, expired SSO login, wrong profile or region, or missing `bedrock:InvokeModel` | Refresh the login (for example `aws sso login --profile <p>`), check region and profile in `.claude/settings.local.json`, and ask the AWS admin for model access or permission. AI-DLC's check is offline and can't test this |
| Refreshed skills not taking effect | Old session | Start a new harness session |

Always start with `aidlc doctor`. Full symptom index:
`R/docs/guide/15-troubleshooting.md`.

## 12. Updating

```bash
aidlc update          # user runs it: updates the machine install
aidlc doctor          # shows project/runtime version skew
aidlc config          # refresh each project (best done after finishing the active workflow)
```

Going back to an earlier version, pinning, release channels:
`R/docs/guide/18-install-and-lifecycle.md`.

## 13. Bigger work and teams

- Before a large feature or a workshop, write two short notes: a **vision
  document** and a **technical environment document**
  (`R/docs/guide/writing-inputs/`).
- Teams: commit the setup (§4), put company standards in team knowledge
  (`R/docs/guide/08-knowledge.md`), let rules accumulate through the learning
  loop, and see `R/docs/guide/workshop-mode.md` for multi-team Construction.
- Facilitators: `R/docs/guide/facilitator-guide.md` (readiness check,
  recovery playbook, harness comparison).
