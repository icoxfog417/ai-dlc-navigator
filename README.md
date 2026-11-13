# aidlc-navigator

An agent skill that onboards first-time users of
[AI-DLC](https://github.com/awslabs/aidlc-workflows) (AI-Driven Development Life
Cycle) in their own language: Japanese, English, or any other. It explains:

1. **What AI-DLC is and why** it works the way it does
2. **How to use it**: install, set up a project, run the first `/aidlc`
   workflow, answer approval gates, and get unstuck
3. **Which settings to choose**: tool, model and effort, workflow profile,
   depth, Guard Policy, and more, for each situation

The skill bundles a snapshot of the AI-DLC documentation at a stable release
(`skills/aidlc-navigator/references/aidlc-workflows/`, see its `SOURCE.md`), so
it works offline and nobody needs to clone AI-DLC.

## Install

Requires the [GitHub CLI](https://cli.github.com/) with `gh skill` (preview).

```bash
gh skill install icoxfog417/aidlc-navigator aidlc-navigator --agent claude-code --scope user
```

Then start a new Claude Code session and ask, for example, 「AI-DLC とは？」 or
"How do I set up AI-DLC?".

- **Install at user scope** (`--scope user`). AI-DLC's `aidlc config` manages
  the project's `.claude/` folder and can overwrite a skill installed there at
  project scope.
- Stay on one version: add `--pin v0.1.0`. Update: `gh skill update aidlc-navigator`.

## Develop and use it at the same time

The source of truth is `skills/aidlc-navigator/`, which is **outside**
`.claude/`, so `aidlc config` and AI-DLC's guard hooks never touch it. Claude
Code loads it through a user-level symlink:

```bash
ln -s "$PWD/skills/aidlc-navigator" ~/.claude/skills/aidlc-navigator
```

- Edit files under `skills/aidlc-navigator/`. Changes apply from the next new
  Claude Code session, in every project.
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
skills/aidlc-navigator/scripts/update-aidlc-docs.sh [vX.Y.Z]   # default: newest stable tag
```

It rebuilds the snapshot beside the old one and swaps it in only when the
rebuild succeeds. Afterwards, check the summaries in
`skills/aidlc-navigator/references/*.md` and the version line in `SKILL.md`
against the new `CHANGELOG.md`.

## License

[MIT-0](LICENSE). The bundled AI-DLC documentation keeps its own MIT-0 license
(`skills/aidlc-navigator/references/aidlc-workflows/LICENSE`).
