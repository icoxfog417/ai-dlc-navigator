#!/usr/bin/env python3
"""Developer checks for the skills in this repo (not shipped with the skill).

Usage, from the repo root:  python tools/check-skill.py   (py on Windows)
Exits non-zero when a check fails.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")  # Agent Skills naming rule
# Bundled-doc citations: R/..., references/aidlc-workflows/..., aidlc-workflows/...
# (not preceded by "/" so URLs such as github.com/awslabs/aidlc-workflows/... are skipped)
CITE_RE = re.compile(r"(?<![\w/.-])(?:R/|references/aidlc-workflows/|aidlc-workflows/)([A-Za-z0-9_./-]+)")

failures = []


def fail(msg):
    failures.append(msg)
    print(f"FAIL  {msg}")


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else None


def check_skill(skill):
    rel = skill.relative_to(ROOT)
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    fm = frontmatter(text)
    if fm is None:
        return fail(f"{rel}/SKILL.md: no frontmatter")
    name = re.search(r"^name:\s*(\S+)\s*$", fm, re.M)
    name = name.group(1) if name else None
    if name != skill.name:
        fail(f"{rel}: frontmatter name {name!r} differs from folder name")
    if not name or not NAME_RE.match(name) or len(name) > 64:
        fail(f"{rel}: name {name!r} breaks the Agent Skills naming rule")
    if name and name.startswith("aidlc-"):
        fail(f"{rel}: name uses AI-DLC's reserved 'aidlc-' prefix")
    if not re.search(r"^description:\s*\S", fm, re.M):
        fail(f"{rel}: missing description")
    if "github-" in fm:
        fail(f"{rel}/SKILL.md: gh install metadata in frontmatter (run: gh skill publish --fix)")

    docs = skill / "references" / "aidlc-workflows"
    # Agent instruction files and hidden folders must never be bundled (any case, any depth).
    for p in docs.rglob("*"):
        if p.name.lower() in ("claude.md", "claude.local.md") or p.name.startswith("."):
            fail(f"{rel}: bundled docs contain {p.relative_to(docs)}")
    missing = set()
    for md in [skill / "SKILL.md", *sorted((skill / "references").glob("*.md"))]:
        for cite in CITE_RE.findall(md.read_text(encoding="utf-8")):
            path = cite.rstrip(".,)").rstrip("/")
            if path and not (docs / path).exists():
                missing.add(f"{md.relative_to(ROOT)}: {path}")
    for m in sorted(missing):
        fail(f"cited bundled path not found: {m}")

    for script in sorted((skill / "scripts").glob("*.py")):
        try:  # built-in compile() writes no __pycache__ into the shipped skill
            compile(script.read_text(encoding="utf-8"), str(script), "exec")
        except SyntaxError as exc:
            fail(f"{script.relative_to(ROOT)} does not compile: {exc}")
    print(f"ok    {rel} checked")


def main():
    skills = sorted(p.parent for p in ROOT.glob("skills/*/SKILL.md"))
    if not skills:
        fail("no skills/*/SKILL.md found")
    for skill in skills:
        check_skill(skill)
    if shutil.which("gh"):
        r = subprocess.run(["gh", "skill", "publish", "--dry-run"], cwd=ROOT, capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip()
        if r.returncode != 0 and 'unknown command "skill"' in out:
            print("skip  this gh has no `gh skill` (needs 2.100+): run `gh skill publish --dry-run` yourself")
        elif r.returncode != 0:
            fail("gh skill publish --dry-run:\n" + out)
        else:
            print("ok    gh skill publish --dry-run" + "".join(f"\n      {l}" for l in out.splitlines() if l.startswith("warning")))
    else:
        print("skip  gh not found: run `gh skill publish --dry-run` yourself")
    print(f"\n{len(failures)} problem(s)" if failures else "\nAll checks passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
