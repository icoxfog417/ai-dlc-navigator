#!/usr/bin/env python3
"""Write the pull request body for an automated AI-DLC docs refresh (not shipped).

Used by .github/workflows/refresh-aidlc-docs.yml after
skills/ai-dlc-navigator/scripts/update-aidlc-docs.py has refreshed the snapshot:

    python tools/docs-refresh-pr-body.py --old v2.11.2 --check-status 0 \
        --check-log check.log [--superseded "#12 #15"] > body.md

The CHANGELOG is upstream text, so it is quoted in short excerpts with @mentions
defused, and each release links to its full notes on GitHub.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "ai-dlc-navigator"
DOCS = SKILL / "references" / "aidlc-workflows"
REPO = "awslabs/aidlc-workflows"
EXCERPT = 1200       # characters per paragraph quoted from a release entry
LOG_LIMIT = 6000     # characters of a failed check log
BODY_LIMIT = 60000   # GitHub rejects bodies over 65536 characters
HEADER_RE = re.compile(r"^## \[([^\]]+)\](.*)$", re.M)


def source_tag():
    m = re.search(r"^- Tag: `([^`]+)`$", (DOCS / "SOURCE.md").read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else "unknown"


def summaries_version():
    m = re.search(r"written for \*\*AI-DLC ([^*]+)\*\*", (SKILL / "SKILL.md").read_text(encoding="utf-8"))
    return m.group(1) if m else "unknown"


TAG_RE = re.compile(r"^v[0-9]+(\.[0-9]+)*$")
VERSION_RE = re.compile(r"^[0-9]+(\.[0-9]+)*$")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


def defuse(text):
    """Upstream text must not ping people or link, close or cross-reference issues here."""
    text = re.sub(r"@(?=[A-Za-z0-9])", "@\u200b", text)  # @user, @org/team
    text = re.sub(r"#(?=[0-9])", "#\u200b", text)       # #123, owner/repo#123, "Fixes #3"
    return re.sub(r"(?i)\bGH-(?=[0-9])", "GH-\u200b", text)  # GH-123


def shorten(text, limit=EXCERPT):
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + " …"


def new_releases(old):
    """CHANGELOG sections above the one for `old`, in file order (newest first)."""
    text = (DOCS / "CHANGELOG.md").read_text(encoding="utf-8")
    heads = list(HEADER_RE.finditer(text))
    old_version = old.lstrip("v")
    if not any(h.group(1) == old_version for h in heads):
        heads = heads[:1]  # old release not listed (e.g. a downgrade): quote the bundled one only
    out = []
    for i, h in enumerate(heads):
        if h.group(1) == old_version:
            break
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        paras = [p.strip() for p in text[h.end():end].split("\n\n") if p.strip()]
        # The lead paragraphs (compatibility line, summary) come before the first bullet or subheading.
        lead = []
        for p in paras:
            if p.startswith(("*", "-", "#")):
                break
            lead.append(p)
        version, date = h.group(1), h.group(2).strip(" -")
        if not VERSION_RE.match(version):
            continue  # not a release header we can link safely
        out.append((version, date if DATE_RE.match(date) else "", lead[:3]))
    return out or None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True, help="tag bundled before the refresh")
    ap.add_argument("--check-status", type=int, required=True, help="exit code of tools/check-skill.py")
    ap.add_argument("--check-log", type=Path, required=True)
    ap.add_argument("--diffstat", type=Path, help="output of git diff --stat for the refresh commit")
    ap.add_argument("--superseded", default="", help="open refresh PRs this one replaces, e.g. '#12 #15'")
    args = ap.parse_args()

    new = source_tag()
    for tag in (args.old, new):
        if not TAG_RE.match(tag):
            raise SystemExit(f"error: unexpected tag {tag!r}")
    superseded = args.superseded.split()
    if not all(re.fullmatch(r"#[0-9]+", s) for s in superseded):
        raise SystemExit(f"error: unexpected --superseded {args.superseded!r}")
    written_for = summaries_version()
    lines = [
        f"Automated refresh of the bundled AI-DLC docs (`references/aidlc-workflows/`): "
        f"**{args.old} → {new}**.",
        "",
        "> [!IMPORTANT]",
        "> Merging alone ships nothing to users: publish a **minor** release afterwards "
        "(`gh skill publish --tag vX.Y.0`). The navigator's summaries are written for "
        f"AI-DLC {written_for}; review them against the releases below first.",
        "",
        "## Checks",
        "",
    ]
    if args.check_status == 0:
        lines.append("✅ `tools/check-skill.py` passed.")
    else:
        log = args.check_log.read_text(encoding="utf-8", errors="replace") if args.check_log.is_file() else ""
        if len(log) > LOG_LIMIT:
            log = log[:LOG_LIMIT] + "\n… (truncated; see the workflow run)"
        lines += [
            "❌ `tools/check-skill.py` failed. A page the skill cites may have moved or been removed "
            "upstream: fix the citation on this branch.",
            "",
            "<details><summary>Check output</summary>",
            "",
            "```text",
            log.replace("```", "'''").rstrip(),
            "```",
            "",
            "</details>",
        ]

    if args.diffstat and args.diffstat.is_file():
        stat = args.diffstat.read_text(encoding="utf-8", errors="replace")
        if len(stat) > LOG_LIMIT:
            stat = stat[:LOG_LIMIT] + "\n… (truncated)"
        lines += ["", "<details><summary>Files changed</summary>", "", "```text",
                  stat.replace("```", "'''").rstrip(), "```", "", "</details>"]

    lines += ["", "## New AI-DLC releases", ""]
    releases = new_releases(args.old)
    if releases is None:
        lines.append(f"No CHANGELOG entries found above {args.old}; read the "
                     f"[release notes](https://github.com/{REPO}/releases/tag/{new}).")
        lines.append("")
    else:
        for version, date, lead in releases:
            title = f"### {version}" + (f" ({date})" if date else "")  # both format-checked
            lines += [title, "", f"[Full release notes](https://github.com/{REPO}/releases/tag/v{version})", ""]
            for p in lead:
                lines += ["> " + defuse(shorten(p)), ">"]
            if lead:
                lines.pop()
            lines.append("")

    lines += [
        "## Before merging",
        "",
        "Push edits to this branch:",
        "",
        "- [ ] Skim the docs diff for text aimed at an AI agent rather than a reader (\"ignore previous "
        "instructions\", requests to run commands, fetch URLs or change settings). The bundled docs are "
        "read by the navigator, so they act as its instructions",
        "- [ ] Read the new CHANGELOG entries and update the summaries in `references/*.md` where facts "
        "changed (stage counts, defaults, commands, versions)",
        f"- [ ] Update \"written for **AI-DLC {written_for}**\" in `SKILL.md` (\"Accuracy and versions\") "
        f"to `{new.lstrip('v')}`",
        "- [ ] `python3 tools/check-skill.py` passes",
        "- [ ] After merging: `gh skill publish --tag vX.Y.0` (minor)",
    ]
    if superseded:
        lines += ["", f"Supersedes {' '.join(superseded)}. This PR is based on `main`, so it has the "
                  "newer docs but none of the edits pushed to the older refresh PR. Move those edits here, "
                  "then close the older PR."]
    lines += ["", "_Opened by the `refresh-aidlc-docs` workflow._"]

    body = "\n".join(lines) + "\n"
    if len(body) > BODY_LIMIT:
        body = body[:BODY_LIMIT] + "\n\n… (truncated)\n"
    sys.stdout.write(body)


if __name__ == "__main__":
    main()
