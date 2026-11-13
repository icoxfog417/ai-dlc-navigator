# Developing ai-dlc-navigator

How to edit, test, and publish the skill. To install and use it, see
[README.md](README.md).

## Layout

```
.
├── skills/ai-dlc-navigator/          ← the skill (source of truth; this is what gh publishes)
│   ├── SKILL.md                      ← instructions the agent follows
│   ├── references/*.md               ← navigator summaries and terminology
│   ├── references/aidlc-workflows/   ← bundled AI-DLC docs snapshot (generated, see SOURCE.md)
│   └── scripts/update-aidlc-docs.py  ← refreshes the snapshot (also run by users)
├── tools/check-skill.py              ← developer checks (not shipped)
├── tools/docs-refresh-pr-body.py     ← PR text for the weekly docs refresh (not shipped)
├── .github/workflows/refresh-aidlc-docs.yml ← weekly: new AI-DLC release → docs refresh PR
├── docs/                         ← GitHub Pages site source (Japanese tutorial + intro; not shipped)
├── mkdocs.yml, requirements-docs.{in,txt}, tools/site_markdown.py ← site build (not shipped)
├── .github/workflows/pages.yml   ← builds the site on PRs; publishes it from main
└── .claude/skills/ai-dlc-navigator   → ../../skills/ai-dlc-navigator   (local link, git-ignored)
```

Why the skill isn't kept directly in `.claude/skills/`:

- `gh skill publish` doesn't look in hidden folders, so it would find nothing
  to release.
- When AI-DLC is set up in this folder, its guard hooks refuse agent commands
  on `.claude/` paths. A hand-made reset that deletes `.claude/` would also
  delete the skill.

## Set up after cloning

Link the skill into this project so Claude Code loads it here:

```bash
# macOS / Linux
mkdir -p .claude/skills && ln -s ../../skills/ai-dlc-navigator .claude/skills/ai-dlc-navigator
```

```powershell
# Windows (a directory junction needs neither admin rights nor Developer Mode)
New-Item -ItemType Directory -Force .claude\skills | Out-Null
cmd /c mklink /J .claude\skills\ai-dlc-navigator skills\ai-dlc-navigator
```

The link is git-ignored, because `gh skill publish` warns when `.claude/skills/`
is committed. Use **either** this project link **or** a user-scope copy in
`~/.claude/skills/`, never both, so the skill isn't loaded twice. On a
development machine, don't run `gh skill install` or `gh skill update` for
this skill.

## Edit

- Edit files under `skills/ai-dlc-navigator/` (not through the `.claude/` link).
- Changes apply from the next **new** Claude Code session.
- Keep the skill name `ai-dlc-navigator`. `aidlc-` is AI-DLC's reserved
  prefix, and the name must match the folder.
- Don't edit `references/aidlc-workflows/` by hand. It's generated; see
  "Update the bundled AI-DLC docs" below.
- Wording in other languages follows `references/terminology.md`: plain local
  words for concepts, English for commands, labels, and setting names.

## Test

1. **Automated checks:**

   ```bash
   python3 tools/check-skill.py      # Windows: py tools\check-skill.py
   ```

   It checks the name rules (including the reserved `aidlc-` prefix), that
   every bundled path the skill cites exists, that no gh install metadata,
   nested `CLAUDE.md`, or `.git` slipped in, that the scripts compile, and it
   runs `gh skill publish --dry-run`.

2. **Try it in a new session** in this folder:

   ```text
   /ai-dlc-navigator AI-DLC とは？
   ```

   or non-interactively: `claude -p "/ai-dlc-navigator What is AI-DLC? One sentence."`

3. **Experience test** (for changes to tone, pacing, or recommendations). Have
   one Claude Code subagent play the navigator, with the skill loaded. Have
   another play a user persona who knows only what the navigator says. Relay
   about three turns, then ask the persona for feedback on clarity, pacing, and
   how natural the terms sound. Use contrasting personas: language, OS, tool,
   and solo vs regulated team. Fact-check the navigator's claims against the
   bundled docs.

4. **Optional end-to-end:** set up AI-DLC in this folder (`aidlc config`), then
   run `/aidlc` in a new session and ask the navigator about each gate.
   AI-DLC's files here (`.claude/`, `aidlc/`, ...) are git-ignored.

## Publish

1. Run the checks above, and commit.
2. Choose the version (semver):
   - **patch** (`v0.1.1`): fixes and wording
   - **minor** (`v0.2.0`): new guidance, or bundled docs for a newer AI-DLC release
   - **major** (`v1.0.0`): changes in how users install or call the skill
3. Push and publish:

   ```bash
   git push
   gh skill publish --tag v0.2.0
   ```

   This creates the GitHub release that `gh skill install` and `gh skill update`
   use. A plain `git push` alone is not installable.
4. Check it the way a user would, in a throwaway folder:

   ```bash
   gh skill install icoxfog417/ai-dlc-navigator ai-dlc-navigator --pin v0.2.0 --dir "$(mktemp -d)"
   ```

Recommended once: protect release tags (repo Settings → Rules → Rulesets), so
a published version can't be changed later. `gh skill publish` warns until
there is a ruleset.

## Site

`docs/` is the source of <https://icoxfog417.github.io/ai-dlc-navigator/>,
built with [Zensical](https://zensical.org/) (the successor of Material for
MkDocs), which reads `mkdocs.yml`. Pages are written to read well on GitHub too:

- Trial-run notes go between `<!-- trial -->` and `<!-- /trial -->` (each on
  its own line). They stay in the Markdown and are left out of the site.
- Use GitHub alerts (`> [!NOTE]`, `> [!TIP]`, `> [!WARNING]`). A bold first
  line (`> **Title**`) becomes the box title on the site.

Both are done by `tools/site_markdown.py`, a Python-Markdown extension. It is
not an MkDocs hook on purpose: Zensical ignores `hooks:` without a warning, and
the trial notes would be published. Preview locally from the repo root:

```bash
python3 -m venv .venv-docs
.venv-docs/bin/pip install --require-hashes --no-deps -r requirements-docs.txt
.venv-docs/bin/zensical serve   # http://localhost:8000
```

`.github/workflows/pages.yml` builds with `--strict` on every pull request that
touches the site, fails if a trial marker reaches the built HTML, and publishes
from `main` (Settings → Pages → Source: **GitHub Actions**). To change the
Zensical version, edit `requirements-docs.in` and regenerate
`requirements-docs.txt` with
`pip-compile --generate-hashes --strip-extras requirements-docs.in`.
Zensical is still 0.x: read its release notes before bumping it.

## Update the bundled AI-DLC docs

### Automatically (weekly pull request)

`.github/workflows/refresh-aidlc-docs.yml` runs every Monday (and on demand from
the Actions tab, optionally with a tag). When AI-DLC has a release newer than the
bundled docs, it refreshes the snapshot, runs `tools/check-skill.py`, and opens a
pull request from `bot/aidlc-docs-<tag>` with excerpts of the new release notes
and a checklist. It never publishes. To ship it:

1. Push summary edits to the PR branch (steps 1 and 2 below). If the checks
   failed, a page the skill cites probably moved upstream: fix the citation.
2. Merge, then publish a **minor** release (see "Publish").

If a newer AI-DLC release comes out while a refresh PR is still open, the
workflow opens a second PR, which links to the first. Move any edits you pushed
to the first PR, then close it.

If a run stops with "Branch ... exists without a pull request", an earlier run
was interrupted or someone else created that branch. Check the branch, delete
it, and run the workflow again.

One-time repo settings:

- **Settings → Actions → General → Workflow permissions → "Allow GitHub Actions
  to create and approve pull requests"**. This also lets workflow tokens
  approve PRs, so keep the safeguards below.
- **Settings → Rules → Rulesets**: protect `main` (require a pull request) and
  `v*` tags (no updates or deletions). The workflow's token can write
  contents, and rulesets stop it, or a compromised step, from pushing to
  `main` or moving a release tag.

GitHub turns off scheduled workflows in a repo with no activity for 60 days.
If that happens, turn it back on from the Actions tab.

Security rules for this workflow (also in the file's header comment):

- Never add a `pull_request_target` trigger, and never run code from a PR with
  its write token. Today it runs only on schedule or manual dispatch, so fork
  PRs can't start it.
- Upstream content is untrusted. It is downloaded and parsed in the read-only
  `fetch` job, and the update script refuses unsafe paths, agent instruction
  files (`CLAUDE.md`) and hidden files, and caps sizes. The write token is
  given only to the push and PR steps.
- Pin actions by commit SHA. When updating one, look up the SHA of the
  release tag (`gh api repos/actions/checkout/commits/v7.0.1 --jq .sha`).
- The bundled docs are read by the navigator as instructions, so review
  each refresh diff for text aimed at an agent (the PR checklist asks for this).

### By hand

```bash
python3 skills/ai-dlc-navigator/scripts/update-aidlc-docs.py --check   # bundled vs latest
python3 skills/ai-dlc-navigator/scripts/update-aidlc-docs.py           # or a tag: ... v2.11.4
```

Then:

1. Read the new release entries in `references/aidlc-workflows/CHANGELOG.md`.
   Update the summaries in `references/*.md` where facts changed: stage counts,
   defaults, commands, versions.
2. Update the "written for AI-DLC X.Y.Z" line in `SKILL.md` ("Accuracy and
   versions").
3. Run the checks, then publish a **minor** release.
