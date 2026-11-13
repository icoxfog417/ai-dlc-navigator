#!/usr/bin/env sh
# Refresh the bundled AI-DLC docs snapshot (references/aidlc-workflows) from a stable release tag.
# Usage: scripts/update-aidlc-docs.sh [vX.Y.Z]   (default: newest stable tag, previews excluded)
#
# The snapshot is plain files (no .git), so it travels with the skill however the
# skill is shared. Provenance lives in references/aidlc-workflows/SOURCE.md.
# Pinned to release tags, not main: the installer ships releases/latest, and main
# carries doc changes for unreleased versions.
set -eu

SKILL_DIR=$(cd "$(dirname "$0")/.." && pwd)
DEST="$SKILL_DIR/references/aidlc-workflows"
UPSTREAM=https://github.com/awslabs/aidlc-workflows.git

# What the navigator reads. The repo's own CLAUDE.md is left out on purpose:
# Claude Code auto-loads a nested CLAUDE.md when files beside it are read, which
# would inject the AI-DLC repo's developer instructions into the navigator.
INCLUDE_DIRS="docs assets"
INCLUDE_FILES="README.md AGENTS.md CHANGELOG.md LICENSE"
INCLUDE="$INCLUDE_DIRS $INCLUDE_FILES"
# Contributor-only material a newcomer never needs (links to it from developer
# pages are left dangling; SOURCE.md lists them as upstream-only).
REMOVE="docs/reference/research docs/reference/examples docs/reference/09-testing.md docs/reference/kiro-ide-hook-payload.md"

old=$(sed -n 's/^- Tag: `\(.*\)`$/\1/p' "$DEST/SOURCE.md" 2>/dev/null || true)

if [ $# -ge 1 ]; then
  tag=$1
else
  tag=$(git ls-remote --tags --refs "$UPSTREAM" \
    | sed 's#.*refs/tags/##' \
    | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' \
    | sort -V | tail -1)
fi
[ -n "$tag" ] || { echo "error: no stable release tag found" >&2; exit 1; }

if [ "$old" = "$tag" ]; then
  echo "Bundled AI-DLC docs already at $tag."
  exit 0
fi

# Work beside DEST so the final swap is a same-filesystem rename.
work=$(mktemp -d "$SKILL_DIR/references/.update.XXXXXX")
trap 'rm -rf "$work"' EXIT INT TERM

git -c advice.detachedHead=false clone --quiet --depth 1 --branch "$tag" \
  --filter=blob:none --sparse "$UPSTREAM" "$work/repo"
{
  for p in $INCLUDE_DIRS; do echo "/$p/"; done
  for p in $INCLUDE_FILES; do echo "/$p"; done
} | git -C "$work/repo" sparse-checkout set --no-cone --stdin

commit=$(git -C "$work/repo" rev-parse HEAD)
commit_date=$(git -C "$work/repo" log -1 --format=%cI)

mkdir "$work/new"
for p in $INCLUDE; do cp -R "$work/repo/$p" "$work/new/"; done
for p in $REMOVE; do rm -rf "$work/new/$p"; done

{
  echo "# Source of this snapshot"
  echo
  echo "Plain-file snapshot of the AI-DLC repository, bundled with the aidlc-navigator skill."
  echo "Do not edit by hand. Refresh with \`scripts/update-aidlc-docs.sh\` from the skill folder."
  echo
  echo "- Repository: https://github.com/awslabs/aidlc-workflows"
  echo "- Tag: \`$tag\`"
  echo "- Commit: \`$commit\` ($commit_date)"
  echo "- Snapshot taken: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "- Included: $(echo "$INCLUDE" | sed 's/ /, /g')"
  echo "- Left out on purpose: the repo's CLAUDE.md (it would auto-load into the agent's context), engine source, tests, and build files"
  echo "- Removed as contributor-only (upstream only; links to them from developer pages will not resolve here): $(echo "$REMOVE" | sed 's/ /, /g')"
  echo
  echo "To read anything left out, open it on GitHub:"
  echo "https://github.com/awslabs/aidlc-workflows/blob/$tag/<path>"
} > "$work/new/SOURCE.md"

changed=""
if [ -d "$DEST" ]; then
  changed=$(diff -rq "$DEST" "$work/new" 2>/dev/null | grep -vc 'SOURCE.md' || true)
  mv "$DEST" "$work/old"
fi
mv "$work/new" "$DEST"

echo "Bundled AI-DLC docs: ${old:-none} -> $tag${changed:+ ($changed files added, removed or changed)}"
echo "Next: re-check the summaries in references/*.md and the version line in SKILL.md against"
echo "  $DEST/CHANGELOG.md"
