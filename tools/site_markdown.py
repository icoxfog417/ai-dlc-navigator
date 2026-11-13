"""Python-Markdown extension for the GitHub Pages site (not shipped with the skill).

Listed under markdown_extensions in mkdocs.yml as `tools.site_markdown`. It is an
extension rather than an MkDocs hook because Zensical, which builds the site,
does not run MkDocs hooks; Python-Markdown extensions work in both.

The pages in docs/ are written to read well on GitHub too, so the site build
rewrites two things there:

- Trial-run notes between <!-- trial --> and <!-- /trial --> are for the
  people running the tutorial's trials. They stay in the Markdown and are
  left out of the site.
- GitHub alerts (> [!NOTE], > [!TIP], ...) become admonitions. A first body
  line in bold (> **Title**) becomes the admonition's title.
"""

import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

TRIAL = re.compile(r"^[ \t]*<!-- trial -->.*?<!-- /trial -->[ \t]*\n?", re.S | re.M)
ALERT = re.compile(r"^> \[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*$")
TITLE = re.compile(r"^\*\*(.+)\*\*\s*$")
KINDS = {
    "NOTE": ("note", "メモ"),
    "TIP": ("tip", "ヒント"),
    "IMPORTANT": ("info", "重要"),
    "WARNING": ("warning", "注意"),
    "CAUTION": ("danger", "注意"),
}


def strip_trial_notes(markdown: str) -> str:
    stripped = TRIAL.sub("", markdown)
    if "<!-- trial -->" in stripped or "<!-- /trial -->" in stripped:
        raise ValueError("unbalanced <!-- trial --> / <!-- /trial --> markers")
    return stripped


def alerts_to_admonitions(markdown: str) -> str:
    lines = markdown.split("\n")
    out = []
    i = 0
    while i < len(lines):
        match = ALERT.match(lines[i])
        if not match:
            out.append(lines[i])
            i += 1
            continue
        kind, title = KINDS[match.group(1)]
        body = []
        i += 1
        while i < len(lines) and lines[i].startswith(">"):
            body.append(lines[i][2:] if lines[i].startswith("> ") else lines[i][1:])
            i += 1
        heading = TITLE.match(body[0]) if body else None
        if heading:
            title = heading.group(1).replace('"', "'")
            body = body[1:]
            while body and not body[0].strip():
                body = body[1:]
        out.append(f'!!! {kind} "{title}"')
        out.append("")
        out.extend("    " + line if line.strip() else "" for line in body)
        out.append("")
    return "\n".join(out)


class _SitePreprocessor(Preprocessor):
    def run(self, lines):
        return alerts_to_admonitions(strip_trial_notes("\n".join(lines))).split("\n")


class SiteMarkdownExtension(Extension):
    def extendMarkdown(self, md):
        # Before html_block (20), which would stash the <!-- trial --> comments.
        md.preprocessors.register(_SitePreprocessor(md), "site_markdown", 28)


def makeExtension(**kwargs):
    return SiteMarkdownExtension(**kwargs)
