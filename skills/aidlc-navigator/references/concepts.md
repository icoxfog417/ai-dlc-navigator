# AI-DLC concepts: what it is, and why it is built that way

Summary for the navigator, written against AI-DLC 2.11.2. Paths in "Read more"
point into the bundled docs snapshot (`references/aidlc-workflows/`, abbreviated to
`R/` here). Read the full page when a user wants more depth than this summary.

## Contents

1. The problem AI-DLC solves
2. The four tenets (the root of every "why")
3. The core idea: engine routes, conductor executes
4. The factory picture
5. Features, each with its why
6. Key numbers

---

## 1. The problem AI-DLC solves

Ad-hoc AI coding ("vibe coding") loses context as a project grows:
requirements, decisions, code, and tests drift apart, and nobody can say why
something was built. AI-DLC (AI-Driven Development Life Cycle) turns an AI
coding assistant into a **structured, verifiable delivery workflow** that keeps
intent → requirements → design → code → tests → deployment connected and
recorded. It started as the AWS AI-DLC methodology (AWS DevOps blog
"AI-Driven Development Life Cycle") and is implemented as an open-source
framework (`awslabs/aidlc-workflows`) that runs inside the coding tool the user
already has.

Read more: `R/README.md` ("Why AI-DLC"), `R/docs/guide/00-introduction.md`,
specification PDF `R/assets/AI-DLC-Workflows-2.0-Specification.pdf`.

## 2. The four tenets

In priority order (the first one wins any conflict):

1. **The human drives the engine.** The person keeps the wheel. AI-DLC asks
   only what only they can decide, never asks again what they already answered,
   and never refuses their explicit request (approve, change, skip, jump, stop,
   switch a check off).
2. **Tools for determinism.** Bookkeeping (which stage is next, what was
   approved and when, what already ran) is mechanical, so a deterministic tool
   does it the same way every time, not the LLM.
3. **LLM for knowledge.** The AI brings expertise the person may not have
   (coding, design, testing, the method, this codebase) and makes the calls
   that knowledge settles. When a choice is the person's, it asks like a good
   colleague: options in plain words, what each means, and a recommendation.
4. **Human for judgement.** The person decides what to build, whether it is
   right (each gate), what to trade off, and when to stop.

**How to use this when explaining:** almost every "why does AI-DLC do X?"
question goes back to one of these. Gates exist for tenet 4, the engine exists
for tenet 2, agents and knowledge exist for tenet 3, and the user can always
override (tenet 1).

Read more: `R/AGENTS.md` ("The four tenets").

## 3. The core idea: the engine routes, the conductor executes

- The **engine** is a plain, non-AI program. It decides *what happens next*:
  which stage runs, which stages the scope skips, when a gate must block, and
  when a phase boundary is verified. The same state always gives the same next
  move.
- The **conductor** is the `/aidlc` session (the AI). It decides *how well the
  work is done*: it adopts the right agent persona, asks good questions, and
  surfaces decisions. It never decides the route. It asks the engine "what's
  next?", does it, reports the outcome, and asks again.

```
You ──/aidlc──▶ Conductor (AI) ──"what next?"──▶ Engine (deterministic)
                     ▲   │                          │
                     │   └── works the stage ◀──────┘ "run stage X"
                     └── gate: Approve / Request Changes
```

**Why:** an LLM that improvises the process skips steps, forgets what was
approved, and behaves differently every run. Separating routing (deterministic)
from execution (AI) gives you predictability *and* expertise.

**Newcomer tip:** most "why won't it just do what I asked?" moments come from
expecting the AI to freelance. If it looks stuck, the engine is waiting for
something, usually your answer at a gate or a missing earlier input.
"The engine routes, I unblock the gates."

Read more: `R/docs/guide/onboarding.md` ("The one idea that makes AI-DLC
click").

## 4. The factory picture (a good analogy for beginners)

AI-DLC is a software factory for spec-driven development. The person drives it,
and the harness (Claude Code, Kiro, ...) is the building it runs in.

| Factory | AI-DLC term |
|---|---|
| Production line | **Scope** (workflow profile) |
| Station on the line | **Stage** |
| Worker at a station | **Agent** |
| Work order passed to the next station | Approved **artifact** |
| Foreman who cues the workers | **Conductor** |
| Line controller and logbook | **Engine** (+ state and audit) |
| Safety guards | **Fences**, tuned by **Guard Policy** |

It is **not a waterfall**: the person can go back to any station, change its
output, and iterate as often as they like.

Read more: `R/AGENTS.md` ("What AI-DLC is").

## 5. Features, each with its why

### 5 phases, 33 stages

`Initialization (3) → Ideation (7) → Inception (9) → Construction (7) → Operation (7)`

- Initialization: workspace detection, scaffold, state init. Automatic, no gates.
- Ideation: intent capture, market research, feasibility, scope definition,
  team formation, rough mockups, approval and handoff. Turns an intent into a
  clear idea.
- Inception: reverse engineering (existing code), practices discovery,
  requirements, user stories, refined mockups, domain design, units generation,
  contract design, delivery planning. Turns the idea into a spec and a plan.
- Construction: functional design, NFR requirements, NFR design,
  infrastructure design, code generation (these repeat per **Unit**), then
  build and test and CI pipeline once. Builds the code.
- Operation: deployment pipeline, environment provisioning, deployment
  execution, observability, incident response, performance validation,
  feedback and optimization. Deploys and verifies, and feeds back into Ideation.

**Why:** a stage never runs before its inputs exist, so code is never built on
requirements that don't exist yet. At phase boundaries a **verification gate**
runs automated traceability checks (missing links, orphaned artifacts) before
later stages build on them.

Read more: `R/docs/guide/04-phases-and-stages.md`.

### Scopes (workflow profiles): the right amount of ceremony

11 stock profiles pick which stages run and how deep, such as `express` (7
stages), `bugfix` (6), `poc` (5), `feature` (all 30 after setup),
`enterprise` (30, comprehensive), and `classic` (15, the default). If no stock
profile fits, the **composer** agent proposes a tailored plan.

**Why:** a one-line bug fix and a regulated payments service need very
different process. You get less ceremony by choosing a smaller scope, not by
bypassing the engine. See `settings.md` for which one to choose.

Read more: `R/docs/guide/workflow-profiles.md`,
`R/docs/guide/05-scopes-and-depth.md`.

### Approval gates: your control point

Every stage except the three automatic Initialization stages ends with a gate:
the workflow stops and waits for **Approve** or **Request Changes**. In
Construction, gates can come per Unit instead, and routine checkpoints can pass
automatically if you choose. The plan offer shows how many gates a run will
have before it starts, and a smaller scope means fewer gates. The summary shows what was produced and
any reviewer findings, each with a stable ID. Approving with open findings
records them as accepted risk, which is normal. After three rounds of
change requests, an **Accept as-is** option appears. In Construction you can
choose **Continue automatically** for routine checkpoints.

**Why:** tenet 4. The human judges whether the work is right before anything
is built on it. A gate is a two-way door: Request Changes is how you steer
without editing files yourself.

Read more: `R/docs/guide/07-interaction-modes.md`.

### Agents: a "small mob" of broad experts

14 agents: 11 domain experts (product, design, delivery, architect,
aws-platform, compliance, devsecops, developer, quality, pipeline-deploy,
operations), 2 reviewers (product lead, architecture reviewer), and the
composer. Each stage has a lead agent. Support agents join when collaborators
are on (by default only in `enterprise`).

**Why 11, not 30?** A human mob of 3 to 5 broad people covers a whole feature.
Dozens of narrow specialists recreate waterfall hand-offs, and every hand-off
is a place to lose information. Broad agents carry context across stages
(the architect leads seven stages across three phases). Agents never call each
other; only the conductor hands out work.

**Reviewers** challenge a builder's output at the gate (for example,
requirements are completeness-checked by the product lead and designs by the
architecture reviewer), which gives the user a second opinion before they
approve.

Read more: `R/docs/guide/06-agents.md`, `R/docs/guide/agents/`.

### Interaction modes: answer however suits you

When a stage needs input, its questions are written to a file and you pick
**Guide me** (one by one in chat), **I'll edit the file**, or **Chat** (talk
freely, and the agent extracts decisions). You choose once and later stages
reuse it. Each question is tagged with who would usually answer it, such as
`[Product owner]` or `[Developer]`.

**Why:** people think differently, and the questions file stays the single
source of truth whichever mode you use.

### Depth and test strategy

- **Depth** (Minimal / Standard / Comprehensive) sets how much detail
  documents get and how many questions are asked.
- **Test strategy** (Minimal / Standard / Comprehensive) sets how many tests
  are written, independently of depth. Minimal follows a "Nyquist" idea: the
  fewest tests that still verify every requirement.

**Why separate?** So you can, for example, keep full documents with lean tests
for a time-boxed workshop, or lean documents with thorough tests for a critical
bug fix.

### The record dir: everything is written down

Each piece of work (an **intent**) gets
`aidlc/spaces/<space>/intents/<YYMMDD>-<label>/`, which holds
`aidlc-state.md` (progress), versioned Markdown artifacts per phase, and an
append-only `audit/` trail (126 event types). It is committed to git.

**Why:** this is the durable memory that keeps a growing project coherent. It
survives sessions, context compaction, model changes, and teammates. To know
*why* something was built, look here. Bare `/aidlc` resumes from it.

Read more: `R/docs/guide/03-spaces-and-intents.md`,
`R/docs/guide/10-state-and-audit.md`, `R/docs/guide/14-artifacts-reference.md`.

### Spaces and intents

An **intent** is one piece of work (one run of the lifecycle). A **space** is
one team's world of intents, rules, and knowledge. Most people only ever use
the `default` space and switch between intents.

### Rules and the learning loop: it learns from your corrections

Rules are plain Markdown in `aidlc/spaces/<space>/memory/`, layered
`org.md → team.md → project.md → phases/<phase>.md`. All applicable layers are
added together (strictly additive). When you correct an agent, AI-DLC asks
once, "Keep that for next time?", and if you say yes it writes a standing rule.

**Why:** a correction should be made once, not every run. Rules are readable
and editable by humans, and are committed so the whole team shares them.

Read more: `R/docs/guide/09-rules-and-the-learning-loop.md`.

### Sensors: a deterministic second opinion

Six framework sensors (required sections, claim sources, upstream coverage,
traceability, linter, type check) check a stage's output the same way every
time. They are advisory unless a team makes one blocking.

**Why:** rules steer *before* work (feedforward), and sensors check *after*
it (feedback). Together they form the control loop, and they don't depend on
the LLM's mood.

### Knowledge: your company's standards

Tier 1 is methodology knowledge (shipped, per agent). Tier 2 is team knowledge
you add under `aidlc/spaces/<space>/knowledge/<agent>/` or the shared folder.
`/aidlc knowledge onboard` indexes your own documents.

**Why:** the agents should follow *your* API conventions or security
baseline. Don't edit the shipped agent files (upgrades overwrite them); add
knowledge instead.

Read more: `R/docs/guide/08-knowledge.md`.

### Guards and Guard Policy

**Fences** are deterministic checks that stop an agent's action that nothing
asked for, such as building code from an unapproved plan or editing an
artifact after its review. **Guard Policy** (`strict` / `relaxed` / `off`)
sets how far they stand aside for one piece of work. Human presence is never
lowered.

**Why:** guards keep the AI on the spec and plan *you* last approved. They
serve the person, never block the person's own explicit request, and record
every time they stand aside.

Read more: `R/docs/guide/13-customization.md` ("Guard Policy").

### One core, many harnesses

The same engine and method run in Claude Code, Kiro IDE / Kiro CLI, Codex CLI,
Cursor, opencode, and GitHub Copilot. Only the "shell" differs: how gates
render, whether there is a status line, and how strongly hooks can enforce.
Records live in a neutral `aidlc/` folder, so a team can mix tools.

**Why:** teams keep the tool they already like. The methodology is
provider-independent.

### Works in your language

AI-DLC detects the conversation language from what you type and writes
requirements, plans, questions, and reviews in it for the whole session.
Commands, IDs (`FR1`), option labels, and file paths stay English. To switch,
just ask, and it can remember the switch for the project.

## 6. Key numbers (v2.11.2)

| | |
|---|---|
| Phases / stages | 5 / 33 |
| Agents | 14 (11 domain experts + 2 reviewers + composer) |
| Stock scopes | 11 + composer-tailored plans |
| Depth levels / test strategy levels | 3 / 3 |
| Audit event types | 126 |
| Harnesses | 7 (Claude Code, Kiro IDE, Kiro CLI V2, Codex, Cursor, opencode, Copilot) |
