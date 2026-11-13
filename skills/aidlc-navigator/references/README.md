# Bundled references

| Path | What |
|---|---|
| `concepts.md` | What AI-DLC is and why: tenets, engine/conductor, features with their rationale |
| `usage.md` | Install → configure → doctor → first run → gates → everyday commands → five-run path → "stuck" table |
| `settings.md` | Recommended settings: baselines by situation, model/effort, the config wizard, scopes, depth, ceremony, Guard Policy |
| `harnesses.md` | Per-harness setup, enforcement strength, how to recommend a harness |
| `terminology.md` | Term glosses (with Japanese examples) and what never to translate |
| `aidlc-workflows/` | **Plain-file snapshot of `awslabs/aidlc-workflows`** at a stable release tag (no `.git`): `docs/`, `assets/` (the 2.0 specification PDF), `README.md`, `AGENTS.md`, `CHANGELOG.md`, `LICENSE`. `SOURCE.md` records the tag and commit and lists what was left out: the repo's `CLAUDE.md`, engine source, tests, build files, and four contributor-only pages |

Most useful pages in the snapshot:

| Topic | Page |
|---|---|
| Docs index | `aidlc-workflows/docs/README.md` |
| User Guide map | `aidlc-workflows/docs/guide/00-introduction.md` |
| Guided first week | `aidlc-workflows/docs/guide/onboarding.md` |
| Getting started (Claude Code screens) | `aidlc-workflows/docs/guide/01-getting-started.md` |
| Workflow profiles | `aidlc-workflows/docs/guide/workflow-profiles.md` |
| Annotated full run | `aidlc-workflows/docs/guide/02-your-first-workflow.md` |
| Phases and stages | `aidlc-workflows/docs/guide/04-phases-and-stages.md` |
| Scopes, depth, test strategy (matrix) | `aidlc-workflows/docs/guide/05-scopes-and-depth.md` |
| Agents | `aidlc-workflows/docs/guide/06-agents.md`, `aidlc-workflows/docs/guide/agents/` |
| Gates and answer modes | `aidlc-workflows/docs/guide/07-interaction-modes.md` |
| Knowledge / rules | `aidlc-workflows/docs/guide/08-knowledge.md`, `09-rules-and-the-learning-loop.md` |
| Sessions, resume | `aidlc-workflows/docs/guide/11-session-management.md` |
| All commands | `aidlc-workflows/docs/guide/12-cli-commands.md` (large; grep it) |
| Customization | `aidlc-workflows/docs/guide/13-customization.md` (large; grep it) |
| Troubleshooting | `aidlc-workflows/docs/guide/15-troubleshooting.md` (large; grep it) |
| Install, update, uninstall | `aidlc-workflows/docs/guide/18-install-and-lifecycle.md` (large; grep it) |
| Glossary | `aidlc-workflows/docs/guide/glossary.md` |
| Harness guides | `aidlc-workflows/docs/guide/harnesses/` |
| Facilitators | `aidlc-workflows/docs/guide/facilitator-guide.md`, `workshop-mode.md` |
| Design principles | `aidlc-workflows/AGENTS.md` (four tenets, factory picture) |
| Methodology spec | `aidlc-workflows/assets/AI-DLC-Workflows-2.0-Specification.pdf` |
| What changed per release | `aidlc-workflows/CHANGELOG.md` |

To refresh the snapshot, run `scripts/update-aidlc-docs.sh [vX.Y.Z]` from the skill
folder (maintainers only; it needs network access and `git`). It fetches the
newest stable tag (or the one named), rebuilds the snapshot beside the old one,
and swaps it in only when the build succeeds.
