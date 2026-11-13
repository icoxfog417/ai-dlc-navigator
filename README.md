# ai-dlc-navigator

An agent skill that onboards first-time users of
[AI-DLC](https://github.com/awslabs/aidlc-workflows) (AI-Driven Development Life
Cycle) in their own language: Japanese, English, or any other. It explains:

1. **What AI-DLC is and why** it works the way it does
2. **How to use it**: install, set up a project, run the first `/aidlc`
   workflow, answer approval gates, and get unstuck
3. **Which settings to choose**: tool, model and effort, workflow profile,
   depth, Guard Policy, and more, for your situation

It bundles a snapshot of the AI-DLC documentation, so it works without cloning
AI-DLC. To develop the skill itself, see [DEVELOPMENT.md](DEVELOPMENT.md).

## Install

Requires the [GitHub CLI](https://cli.github.com/) 2.100 or later (`gh skill`
is in preview).

```bash
gh skill install icoxfog417/ai-dlc-navigator ai-dlc-navigator --agent claude-code --scope user
```

This puts the skill in `~/.claude/skills/ai-dlc-navigator/`, so it's available
in every project. To stay on one version, add `--pin v0.1.0`.

## Use

Start a **new** Claude Code session (skills load when a session starts), then
either ask in your own words or call the skill by name:

```text
AI-DLC とは？初めてなので、何から始めればいいですか？
/ai-dlc-navigator How do I set up AI-DLC for my team?
```

The navigator replies in the language you write in. It can explain the
concepts and the reasons behind them, walk you through installing AI-DLC and
your first `/aidlc` run, and recommend settings for your situation.

## Update

**The skill** (new summaries, fixes, and newer bundled docs, when released):

```bash
gh skill update ai-dlc-navigator
```

If you installed with `--pin`, the update skips it. Add `--unpin` to follow
new releases again.

This repo checks for new AI-DLC releases every week and bundles their docs in
a new skill release after review. The installed skill doesn't update itself,
so run `gh skill update` every few weeks. If
the bundled docs are more than 60 days old, the navigator reminds you once per
conversation.

**Only the bundled AI-DLC docs**, when AI-DLC has released a newer version than
the one bundled (Python 3, standard library only):

```bash
# macOS / Linux
python3 ~/.claude/skills/ai-dlc-navigator/scripts/update-aidlc-docs.py --check   # compare versions
python3 ~/.claude/skills/ai-dlc-navigator/scripts/update-aidlc-docs.py           # update to AI-DLC's latest release
```

```powershell
# Windows
py "$env:USERPROFILE\.claude\skills\ai-dlc-navigator\scripts\update-aidlc-docs.py" --check
py "$env:USERPROFILE\.claude\skills\ai-dlc-navigator\scripts\update-aidlc-docs.py"
```

It downloads the release that AI-DLC's own installer would install, and replaces
the bundled docs only when the download succeeds. Start a new session afterwards.
A later `gh skill update` brings the docs back to the release's copy.

## Using it next to AI-DLC

The navigator works alongside AI-DLC's own commands and doesn't change them.

- **Names don't overlap.** AI-DLC's commands and skills are `/aidlc` and
  `aidlc-*`. This skill is `ai-dlc-navigator`, outside that namespace.
- **The navigator explains; you decide and run.** It never runs `/aidlc`
  stages, answers approval gates for you, or edits AI-DLC's records under
  `aidlc/`. It runs only read-only checks (`aidlc version`, `aidlc doctor`,
  `aidlc config --dry-run`) and shows any other command for you to run.
- **Start a new conversation after `aidlc config`.** `/aidlc` and AI-DLC's
  hooks load when a session starts. The navigator is available in the new
  conversation too, so you can ask about a gate while you work.
- **User scope is the safest place.** A project-scope install (the project's
  `.claude/skills/`) also works: AI-DLC's `aidlc config` keeps it on setup and
  refresh (checked with AI-DLC 2.11.2). But **don't delete the whole `.claude/`
  folder** to reset AI-DLC, because that deletes the skill too. To take AI-DLC
  out of a project, follow its manifest-based removal ("Remove AI-DLC from a
  Project" in AI-DLC's install guide), which keeps files AI-DLC didn't install.
- **Version differences.** If your AI-DLC is newer than the bundled docs, the
  navigator says so and points you to the docs update above. `aidlc doctor` and
  `/aidlc --help` on your machine are always the final word.
- Generative AI can make mistakes. Review what the navigator and AI-DLC
  produce, and the costs, before acting on them.

## License

[MIT-0](LICENSE). The bundled AI-DLC documentation keeps its own MIT-0 license
(`skills/ai-dlc-navigator/references/aidlc-workflows/LICENSE`).
