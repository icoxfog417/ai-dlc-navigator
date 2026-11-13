#!/usr/bin/env python3
"""Refresh the bundled AI-DLC docs snapshot (references/aidlc-workflows).

Usage (any OS, Python 3.8+, standard library only, no git needed):
    python update-aidlc-docs.py            # update to AI-DLC's latest release
    python update-aidlc-docs.py v2.11.4    # update to a specific release tag
    python update-aidlc-docs.py --check    # only compare bundled vs latest

"Latest" is GitHub's latest release, the same one AI-DLC's installer
(releases/latest) installs. The snapshot is plain files with provenance in
references/aidlc-workflows/SOURCE.md. It is rebuilt beside the old one and
swapped in only when the rebuild succeeded.
"""
import argparse
import datetime
import io
import json
import os
import re
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path, PurePosixPath

REPO = "awslabs/aidlc-workflows"
API = f"https://api.github.com/repos/{REPO}"
SKILL_DIR = Path(__file__).resolve().parent.parent
DEST = SKILL_DIR / "references" / "aidlc-workflows"

# What the navigator reads. The repo's own CLAUDE.md is left out on purpose:
# Claude Code auto-loads a nested CLAUDE.md when files beside it are read, which
# would inject the AI-DLC repo's developer instructions into the navigator.
INCLUDE_DIRS = ["docs", "assets"]
INCLUDE_FILES = ["README.md", "AGENTS.md", "CHANGELOG.md", "LICENSE"]
# Contributor-only material a newcomer never needs (links to it from developer
# pages are left dangling; SOURCE.md lists them as upstream-only).
REMOVE = [
    "docs/reference/research",
    "docs/reference/examples",
    "docs/reference/09-testing.md",
    "docs/reference/kiro-ide-hook-payload.md",
]


def fetch(url, accept="application/vnd.github+json"):
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "ai-dlc-navigator-docs-updater"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def latest_tag():
    return json.loads(fetch(f"{API}/releases/latest"))["tag_name"]


def bundled_tag():
    source = DEST / "SOURCE.md"
    if not source.is_file():
        return None
    m = re.search(r"^- Tag: `([^`]+)`$", source.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else None


def wanted(rel):
    """Is this repo-relative POSIX path part of the snapshot?"""
    top = rel.parts[0]
    if len(rel.parts) == 1 and top in INCLUDE_FILES:
        return True
    if top not in INCLUDE_DIRS:
        return False
    return not any(rel == PurePosixPath(r) or PurePosixPath(r) in rel.parents for r in REMOVE)


def extract(tag, into):
    data = fetch(f"https://codeload.github.com/{REPO}/tar.gz/refs/tags/{tag}", accept="*/*")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for member in tar.getmembers():
            parts = PurePosixPath(member.name).parts
            if len(parts) < 2:
                continue
            rel = PurePosixPath(*parts[1:])  # drop the "aidlc-workflows-<version>/" prefix
            if rel.is_absolute() or ".." in rel.parts or not wanted(rel):
                continue
            target = into.joinpath(*rel.parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():  # links and special files are skipped
                target.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(member) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
    missing = [p for p in INCLUDE_DIRS + INCLUDE_FILES if not (into / p).exists()]
    if missing:
        raise SystemExit(f"error: release {tag} has no {', '.join(missing)}; nothing changed")


def write_source(into, tag):
    commit = json.loads(fetch(f"{API}/commits/{tag}"))
    sha, date = commit["sha"], commit["commit"]["committer"]["date"]
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (into / "SOURCE.md").write_text(
        "# Source of this snapshot\n\n"
        "Plain-file snapshot of the AI-DLC repository, bundled with the ai-dlc-navigator skill.\n"
        "Do not edit by hand. Refresh with `python scripts/update-aidlc-docs.py` from the skill folder.\n\n"
        f"- Repository: https://github.com/{REPO}\n"
        f"- Tag: `{tag}`\n"
        f"- Commit: `{sha}` ({date})\n"
        f"- Snapshot taken: {now}\n"
        f"- Included: {', '.join(INCLUDE_DIRS + INCLUDE_FILES)}\n"
        "- Left out on purpose: the repo's CLAUDE.md (it would auto-load into the agent's context), "
        "engine source, tests, and build files\n"
        "- Removed as contributor-only (upstream only; links to them from developer pages will not "
        f"resolve here): {', '.join(REMOVE)}\n\n"
        "To read anything left out, open it on GitHub:\n"
        f"https://github.com/{REPO}/blob/{tag}/<path>\n",
        encoding="utf-8",
    )


def count_changes(old, new):
    def files(root):
        return {p.relative_to(root).as_posix(): p for p in root.rglob("*") if p.is_file() and p.name != "SOURCE.md"}
    a, b = files(old), files(new)
    return sum(1 for k in a.keys() | b.keys() if k not in a or k not in b or a[k].read_bytes() != b[k].read_bytes())


def main():
    parser = argparse.ArgumentParser(description="Refresh the bundled AI-DLC docs snapshot.")
    parser.add_argument("tag", nargs="?", help="release tag such as v2.11.4 (default: latest release)")
    parser.add_argument("--check", action="store_true", help="only report bundled and latest versions")
    args = parser.parse_args()

    old = bundled_tag()
    try:
        tag = args.tag or latest_tag()
    except OSError as exc:
        raise SystemExit(f"error: cannot reach GitHub ({exc}); nothing changed")
    if args.check:
        state = "up to date" if old == tag else "update available"
        print(f"Bundled AI-DLC docs: {old or 'none'}; latest release: {tag} ({state})")
        return
    if old == tag:
        print(f"Bundled AI-DLC docs already at {tag}.")
        return

    work = Path(tempfile.mkdtemp(prefix=".update.", dir=DEST.parent))  # same filesystem as DEST
    try:
        new = work / "new"
        new.mkdir()
        try:
            extract(tag, new)
            write_source(new, tag)
        except OSError as exc:
            raise SystemExit(f"error: download of {tag} failed ({exc}); nothing changed")
        changed = None
        if DEST.exists():
            changed = count_changes(DEST, new)
            os.replace(DEST, work / "old")
        os.replace(new, DEST)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    detail = f" ({changed} files added, removed or changed)" if changed is not None else ""
    print(f"Bundled AI-DLC docs: {old or 'none'} -> {tag}{detail}")
    print("The navigator's summaries were written for an earlier version; where they differ,")
    print("it now prefers these full docs. A new skill release brings updated summaries.")


if __name__ == "__main__":
    sys.exit(main())
