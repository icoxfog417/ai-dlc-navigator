# Recommended settings: what to choose, and when to choose otherwise

Navigator guide to AI-DLC's settings, written against AI-DLC 2.11.2 (per-scope
defaults read from `core/scopes/*.md` at tag v2.11.2). `R/` means
`references/aidlc-workflows/`.

**Navigator rule:** recommend the defaults first. Most first-timers need only
three decisions: which harness, which model, and which workflow profile for
their first task. Bring up the rest only when the user's context calls for it.

## Contents

1. The settings map: what can be set, and where
2. Recommended baselines by situation
3. Model and effort
4. The `aidlc config` wizard, step by step
5. Project default scope
6. Picking a workflow profile for each task
7. Depth and test strategy
8. Ceremony switches, review cap, and per-scope defaults
9. Guard Policy
10. Construction approvals and execution
11. Personal vs shared settings, and permissions
12. Things not to do

---

## 1. The settings map

| Level | What | How to set | Stored in |
|---|---|---|---|
| Machine | AI-DLC install and version | installer, `aidlc update` | `~/.local/share/aidlc` (Windows `%LOCALAPPDATA%\aidlc`) |
| Harness (host) | Model provider, login, session model and effort | the harness itself; `aidlc config providers` for Bedrock | harness settings |
| Project (shared) | Harness surface, effort preset, plugins, MCP, default scope | `aidlc config ...` | `.claude/settings.json`, `aidlc.settings.json`, `.mcp.json` (committed) |
| Project (personal) | Status line, Bedrock env, local overrides | `aidlc config ... --local`, wizard answers | `*.local.json` (git-ignored) |
| Team rules | Standing practices, a locked Guard Policy, conversation language | learning loop, or edit by hand | `aidlc/spaces/<space>/memory/{org,team,project}.md` |
| One piece of work (intent) | Scope, depth, test strategy, review cap, Guard Policy, 5 ceremony switches | `/aidlc --<flag>`, plain words, at gates | the intent's `aidlc-state.md` |

Inspect the active work's settings with `/aidlc config list` and
`/aidlc --status`.

## 2. Recommended baselines by situation

| Situation | Harness and model | `aidlc config` | First runs | Per-work tuning |
|---|---|---|---|---|
| **Solo, first time** | The tool you already use; Opus 4.8 | **Recommended defaults** (choice 1) | `express`, then `poc`, then `feature` (the five-run path in `usage.md`) | none |
| **Team adopting AI-DLC** | One shared harness where possible (mixing is supported); Opus 4.8 | Defaults; record the preset **in the project, committed**; commit the setup files | A pilot `feature` on real code | Add team knowledge; let rules accumulate |
| **Regulated / high-assurance** | Their standard tool. Claude Code or Codex enforce most strongly (see `harnesses.md`) | Defaults; consider the `thorough` preset | Practice with `express` **in a practice project, never a production repo**. Then `bugfix` / `refactor` for small changes and `enterprise` for audited core work (§6) | Lock `Mode: strict` in `team.md` (§9); require PR review |
| **Workshop / training** | Whatever participants have; check the facilitator readiness pass first | Defaults | `workshop`; `express` for side tasks | `--depth minimal` if time is short |
| **Only a mid-tier model (for example Sonnet)** | Session at **medium** effort | `balanced` preset | Smaller scopes first | Raise effort for one hard stage only (§3) |
| **Quick fix in an existing repo** | Any | Defaults | `bugfix`, or `express --add functional-design` | none |

## 3. Model and effort

- **Recommended model: Claude Opus 4.8.** AI-DLC runs many turns of real
  reasoning, so a capable model matters more than anything else. On Kiro,
  Opus 4.8 needs a paid Kiro plan.
- **Where the model is set depends on the harness:**
  - Claude Code, Codex CLI, opencode: the session's model and effort drive the
    conductor and inheriting agents. `aidlc config models` sets agent
    efforts (presets) and per-agent exceptions.
  - GitHub Copilot, Cursor, Kiro IDE: set in the host for the whole session.
    Every agent uses the chat's model (on Kiro IDE, one agent can get its own
    model and effort via `aidlc config models --agent`).
  - Kiro CLI: one session model and one effort. Presets map to `minimal`=low,
    `balanced`=medium, `thorough`=extra-high. `/model` and `/effort` change
    them, and `/model set-current-as-default` saves the change for dispatched
    agents.
- **Effort presets** (effort only, never model IDs):

  | Preset | Deciding (9 agents) | Reviewing (2) | Writing up (3) | Choose when |
  |---|---|---|---|---|
  | `balanced` (**recommended default**) | medium | medium | medium | Almost always |
  | `thorough` | session effort | extra-high | session effort | High-stakes work; more cost and time accepted |
  | `minimal` | medium | medium | low | Cost- or time-sensitive runs |
  | `unchanged` | (no preset; shipped tier defaults) | | | You manage effort yourself |

- **Mid-tier model only:** start the session at **medium** effort (high or max
  on every turn makes the whole run much slower and more expensive). Raise
  effort only for a stage that needs it, for example
  `aidlc config models --agent developer --effort high --project --yes` for a
  hard Code Generation, then put it back with `--effort default`.
- **Changing model mid-workflow:** between stages, in a new chat, then `/aidlc`.

Source: `R/docs/guide/18-install-and-lifecycle.md` ("Model Policy",
"Choosing a Model and Effort"), `R/docs/guide/13-customization.md` ("Agent
Models and Effort").

## 4. The `aidlc config` wizard, step by step

The first prompt: **1. Yes, use recommended defaults** / **2. No, customize** /
**3. Exit**. Recommend **1** unless one of the cases below applies.

| Customize step | Options | Recommendation |
|---|---|---|
| 1. Harness | The detected tool is the default | The tool the user will actually open. See `harnesses.md` |
| 2. Model provider | `keep current` (default) / `amazon-bedrock` | **keep current**, unless the organization uses Claude through Amazon Bedrock. Bedrock asks for region and profile and writes them only to the personal `.claude/settings.local.json`. Two things AI-DLC **cannot verify** (its provider check is offline and never calls AWS): model access enabled in that region, and the `bedrock:InvokeModel` permission. They stay listed as pending actions (`aidlc config providers --check` exits non-zero while pending) until the user confirms them, typically after the first chat works, with `aidlc config providers --mark-done bedrock-model-access --yes`. Kiro needs no provider answer |
| 3. Effort preset | balanced / thorough / minimal / unchanged | **balanced** (§3). On Kiro IDE, Cursor, and Copilot no preset is recorded, because agents follow the session |
| 4. Plugins | all installed (default) / none optional / choose | **all installed**. "none optional" = bare core |
| 5. MCP servers | on / off | **on** (the recommended default), also for newcomers without AWS: a server whose credentials are missing (`context7` needs `CONTEXT7_API_KEY`; the AWS servers need `uvx` and AWS credentials) is simply unavailable and never blocks a workflow. Claude Code asks at first start which servers to enable; enable the ones with credentials or press Esc. Choose **off** only if the organization restricts MCP or the user wants a minimal setup |
| 6. Where to record the preset | project, committed (default) / project, just for you / this machine | **project, committed** for teams (everyone gets the same); **just for you** when experimenting in a shared repo |
| Status line (Claude Code) | Yes / No | **Yes**, it shows the stage and progress. `/aidlc --statusline off` gives yours back |

MCP servers shipped: `context7` (library docs, `CONTEXT7_API_KEY`), `aws-mcp`,
`aws-pricing`, `aws-iac`, `aws-serverless` (AWS credential chain). Never put
secrets in the committed `.mcp.json`.

Later changes: run `aidlc config` again, or individual sections
(`aidlc config models|providers|flags|trust ... --help`), or
`/aidlc --config` inside the harness.

## 5. Project default scope

What runs when a user types `/aidlc` with a description that matches no
profile. The shipped default is **`classic`**.

- Leave it unless the team wants another default, for example
  `aidlc config flags --default-scope feature --project --yes` (or `--local`).
- On Claude Code, `.claude/settings.json` ships `"AWS_AIDLC_DEFAULT_SCOPE":
  "classic"` in `env`, and that wins over the recorded flag. Edit or remove it
  there to change the default.
- Precedence: explicit `/aidlc <scope>` > the plan the agent proposes from the
  description > `AWS_AIDLC_DEFAULT_SCOPE` > recorded `--default-scope` >
  `classic`.

## 6. Picking a workflow profile for each task

| Situation | Profile | Stages (plus 3 automatic Initialization stages, under a second, no gate) |
|---|---|---|
| Learning AI-DLC; small, well-understood change | `express` | 7 |
| Known bug | `bugfix` | 6 |
| "Can this even work?" | `poc` | 5 |
| Clean-up without behavior change | `refactor` | 7 |
| CVE or vulnerability fix | `security-patch` | 7 |
| Environment, IaC, CDK, cost work | `infra` | 10 |
| V1-style Inception and Construction (no Ideation or Operation) | `classic` | 15 |
| First real product increment (no Operation) | `mvp` | 20 |
| Production feature, full lifecycle | `feature` | 30 |
| Regulated, audit-sensitive | `enterprise` | 30 (comprehensive) |
| Training lab or facilitated session | `workshop` | 23 |
| None of these fits | describe it, or `/aidlc compose "..."` | tailored |

**When in doubt, size by the change.** Start small and add the one stage you
need rather than starting big: `/aidlc express --add functional-design <change>`.
Don't use `express` for ambiguous, cross-team, regulated, or architecture-heavy
work, because its speed comes from removing exactly those decision points.

Full matrix: `R/docs/guide/05-scopes-and-depth.md` ("Stage-by-Scope Matrix").
Descriptions: `R/docs/guide/workflow-profiles.md`.

## 7. Depth and test strategy

Depth = how much detail and how many questions. Test strategy = how many tests.
They are independent. Each scope sets both (test strategy follows depth, except
`workshop`, which uses Standard depth with Minimal tests).

| Combination | Use for |
|---|---|
| Standard / Standard | Production features (`feature`, `classic`, `mvp`) |
| Standard / Minimal | Workshops, time-boxed sessions |
| Minimal / Minimal | `express`, quick fixes |
| Minimal / Comprehensive | A critical bug fix that needs confidence |
| Comprehensive / Comprehensive | Regulated enterprise features |

Change any time: `/aidlc --depth minimal`, `/aidlc --test-strategy standard`,
or say it at a gate. **"Too many questions" → `--depth minimal`** is the most
common first-week tweak.

## 8. Ceremony switches, review cap, and per-scope defaults

Five per-intent switches (`/aidlc --<name> on|off`):

- `sensors`: deterministic output checks
- `learnings`: the "Keep that for next time?" ritual and diary
- `summary-confirmation`: an extra confirmation of a consolidated summary before output is written
- `plan-approval`: approve each code plan before it is built (only the person can turn it off)
- `collaborators`: support agents join stages (off = lead agent only)

Review cap: `/aidlc --review adversarial|advisory|none` (it can only lower a
stage's declared review, never raise it).

Shipped defaults (v2.11.2):

| Scope | Depth | Review cap | Guard Policy | Sensors | Learnings | Summary conf. | Plan approval | Collaborators |
|---|---|---|---|---|---|---|---|---|
| enterprise | Comprehensive | — | **strict** | on | on | on | on | **on** |
| feature | Standard | — | off | on | on | on | on | off |
| mvp | Standard | — | off | on | on | on | on | off |
| infra | Standard | — | off | on | on | on | on | off |
| refactor | Minimal | — | off | on | on | on | on | off |
| security-patch | Minimal | — | off | on | on | on | on | off |
| classic | Standard | advisory | off | on | on | off | on | off |
| workshop | Standard (tests Minimal) | advisory | off | on | on | on | on | off |
| poc | Minimal | advisory | off | on | on | on | **off** | off |
| bugfix | Minimal | advisory | off | on | off | off | on | off |
| express | Minimal | **none** | off | off | off | off | off | off |

**Recommendation:** keep the scope defaults. They are tuned for each kind of
work. Typical deliberate changes:

- Fewer stops in a workshop: `--learnings off`, `--summary-confirmation off`.
- More rigor on a `feature`: `--collaborators on` (support agents join, at
  more cost and time).
- Want reviewers in a fast run: use `poc` instead of `express`
  (`express` disables reviewers).

Global kill switches (`AIDLC_DISABLE_SENSORS=1` and others) override
everything. They are meant for emergencies and automation, not daily use.

## 9. Guard Policy

`strict` / `relaxed` / `off`: how far the guards stand aside when something
you approved has changed underneath, or when the agent acts without being asked.

- **Defaults:** `strict` for `enterprise`, `off` for every other scope. A
  lowered fence still writes an audit row each time, and human presence is
  never lowered.
- **Recommendation for most users:** keep the default.
- **Regulated teams:** lock it for everyone by adding to
  `aidlc/spaces/<space>/memory/team.md` (or `org.md` / `project.md`):

  ```markdown
  ## Guard Policy
  Mode: strict
  ```

  A locked `strict` also keeps plan approval on, and requests to lower it are
  refused with a line naming the file.
- **Per work:** `/aidlc --guard-policy relaxed`, or say it in plain words
  ("stop asking me to re-approve when files change").
- Older name: Change Control (still accepted in 2.11.x).

Source: `R/docs/guide/13-customization.md` ("Guard Policy", "The five fences").

## 10. Construction approvals and execution

- New solo work with Units is built **one Unit at a time** (unit-major) with
  verified checkpoints. You approve each Unit's code plan.
- At Construction entry (or after the walking-skeleton checkpoint) you choose
  **Continue automatically** (routine checkpoints pass without a question) or
  **Review each checkpoint**. Recommend **Review each checkpoint** for a first
  run and **Continue automatically** once the user trusts the flow. Plan
  approval, the verification command, and failures still stop either way.
- Parallel (swarm) Unit builds need an explicit stage-major order plus swarm
  execution. This is advanced; skip it for newcomers. See
  `R/docs/guide/04-phases-and-stages.md` and `R/docs/guide/workshop-mode.md`.

## 11. Personal vs shared settings, and permissions

- Shared, committed: `.claude/settings.json`, `aidlc.settings.json`, `.mcp.json`, `aidlc/`.
- Personal, git-ignored: `.claude/settings.local.json` (start from
  `.claude/settings.local.json.example`), `aidlc.settings.local.json`. Use these
  for model overrides, local environment variables, permission changes, and
  anything sensitive.
- AI-DLC pre-approves the tool permissions it needs in `.claude/settings.json`
  (Claude Code shows the list on the trust prompt). Narrow or widen them in
  the local file. Other harnesses: `R/docs/guide/13-customization.md`
  ("Tool Permissions").

## 12. Things not to do

- Don't edit shipped agent files (`.claude/agents/aidlc-*.md`). Upgrades
  overwrite them, and `aidlc config models --check` reports hand edits as
  drift. Use team knowledge or `aidlc config models --agent` instead.
- Don't edit files under generated engine directories by hand. Re-run
  `aidlc config` to refresh.
- Don't put secrets in committed files (`settings.json`, `.mcp.json`).
- Don't install from an administrator PowerShell.
- Don't turn kill switches or `Guard Policy off` on just to "make it faster".
  Choose a smaller scope instead.
