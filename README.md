# ai-dlc-navigator

An agent skill that onboards first-time users of
[AI-DLC](https://github.com/awslabs/aidlc-workflows) (AI-Driven Development Life
Cycle) in their own language: Japanese, English, or any other. It explains:

1. **What AI-DLC is and why** it works the way it does
2. **How to use it**: install, set up a project, run the first `/aidlc`
   workflow, answer approval gates, and get unstuck
3. **Which settings to choose**: tool, model and effort, workflow profile,
   depth, Guard Policy, and more, for each situation

The skill bundles a snapshot of the AI-DLC documentation at a stable release
(`skills/ai-dlc-navigator/references/aidlc-workflows/`, see its `SOURCE.md`), so
it works offline and nobody needs to clone AI-DLC.

## Install

Requires the [GitHub CLI](https://cli.github.com/) with `gh skill` (preview).

```bash
gh skill install icoxfog417/ai-dlc-navigator ai-dlc-navigator --agent claude-code --scope user
```

Then start a new Claude Code session and ask, for example, 「AI-DLC とは？」 or
"How do I set up AI-DLC?".

- **User scope** (`--scope user`) makes it available in every project.
  Project scope (`.claude/skills/` of one project) also works: `aidlc config`
  keeps it on setup and refresh (checked with AI-DLC 2.11.2). But a hand-made
  reset that deletes the whole `.claude/` folder deletes the skill too. To take
  AI-DLC out of a project, use its manifest-based removal instead, which keeps
  files it didn't install.
- Stay on one version: add `--pin v0.1.0`. Update: `gh skill update ai-dlc-navigator`.

## Develop and use it at the same time

The source of truth is `skills/ai-dlc-navigator/`, which is **outside**
`.claude/`. A reset of AI-DLC's files can't take it with it, and AI-DLC's guard
hooks, which refuse agent commands on `.claude/` paths, don't get in the way of
editing it. Claude Code still loads skills only from a `.claude/skills/` folder,
so link the source into one. **Pick one** of these, not both, so the same skill
isn't loaded twice:

```bash
# A) This project only (what this repo uses; relative, so it survives moving the repo)
mkdir -p .claude/skills && ln -s ../../skills/ai-dlc-navigator .claude/skills/ai-dlc-navigator

# B) User level: available in every project
ln -s "$PWD/skills/ai-dlc-navigator" ~/.claude/skills/ai-dlc-navigator
```

Run A once after cloning. `.claude/` is git-ignored (`gh skill publish` warns
when `.claude/skills/` is committed), so the link isn't in the repo. Why not
keep the skill itself in `.claude/skills/`? `gh skill publish` doesn't look in
hidden folders, so it would find nothing to release.

AI-DLC keeps either link. `aidlc config` (setup and refresh) removes only its
own unchanged files that a newer release dropped, `aidlc uninstall` leaves
project files alone, and AI-DLC has no command that removes it from a project.
Don't copy the folder instead of linking: a copy goes stale as soon as you
edit the source.

- Edit files under `skills/ai-dlc-navigator/`. Changes apply from the next new
  Claude Code session.
- You can also run AI-DLC itself in this folder (`aidlc config`, then `/aidlc`)
  to try the navigator end to end. Its files (`.claude/`, `aidlc/`, ...) are
  git-ignored.
- On the development machine, **don't** run `gh skill install` or `gh skill update`
  for this skill. Through the symlink, they would overwrite the source and add
  install metadata to `SKILL.md`. If that metadata ever gets committed,
  `gh skill publish --fix` strips it.

## Release

```bash
gh skill publish --dry-run          # validate against the Agent Skills spec
gh skill publish --tag v0.1.0       # create a GitHub release that users install
```

## Update the bundled AI-DLC docs

```bash
skills/ai-dlc-navigator/scripts/update-aidlc-docs.sh [vX.Y.Z]   # default: newest stable tag
```

It rebuilds the snapshot beside the old one and swaps it in only when the
rebuild succeeds. Afterwards, check the summaries in
`skills/ai-dlc-navigator/references/*.md` and the version line in `SKILL.md`
against the new `CHANGELOG.md`.

## License

[MIT-0](LICENSE). The bundled AI-DLC documentation keeps its own MIT-0 license
(`skills/ai-dlc-navigator/references/aidlc-workflows/LICENSE`).
