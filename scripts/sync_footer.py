#!/usr/bin/env python3
"""
Sync the site footer across every HTML file.

Edit FOOTER_HTML below, then run:
    python3 scripts/sync_footer.py

The script inserts the footer between <!-- footer:start --> and
<!-- footer:end --> markers. On first run (no markers yet) it inserts
them just before </body>. Re-running replaces whatever is between the
markers, so this is safe to run repeatedly.
"""

import re
from pathlib import Path

FOOTER_HTML = """    <footer>
        <nav class="socials" aria-label="Social links">
            <a href="https://github.com/thealexarias" aria-label="GitHub" rel="me noopener" target="_blank">
                <svg aria-hidden="true"><use href="/icons.svg#github"/></svg>
            </a>
            <a href="https://instagram.com/the_alexarias" aria-label="Instagram" rel="me noopener" target="_blank">
                <svg aria-hidden="true"><use href="/icons.svg#instagram"/></svg>
            </a>
            <a href="https://x.com/the_alexarias" aria-label="X" rel="me noopener" target="_blank">
                <svg aria-hidden="true"><use href="/icons.svg#x"/></svg>
            </a>
        </nav>
        <p><a href="https://ko-fi.com/the_alexarias">Support</a></p>
        <p>&copy; 2026 Alex Arias. All rights reserved.</p>
    </footer>
"""

START = "<!-- footer:start -->"
END = "<!-- footer:end -->"

ROOT = Path(__file__).resolve().parent.parent

BLOCK = f"    {START}\n{FOOTER_HTML}    {END}\n"

marker_re = re.compile(
    re.escape(START) + r".*?" + re.escape(END),
    re.DOTALL,
)
body_close_re = re.compile(r"([ \t]*)</body>", re.IGNORECASE)


def update(html: str) -> str:
    if START in html and END in html:
        return marker_re.sub(BLOCK.strip(), html)
    match = body_close_re.search(html)
    if not match:
        return html
    return html[: match.start()] + BLOCK + match.group(0) + html[match.end():]


def main() -> None:
    files = sorted(ROOT.rglob("*.html"))
    changed = 0
    skipped = 0
    for path in files:
        if ".git" in path.parts:
            continue
        original = path.read_text(encoding="utf-8")
        updated = update(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
        else:
            skipped += 1
    print(f"updated {changed} file(s), unchanged {skipped}")


if __name__ == "__main__":
    main()
