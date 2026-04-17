#!/usr/bin/env python3
"""
Build all podcast HTML from podcasts/episodes.json.

- Regenerates each individual episode page at podcasts/{YYYY-MM}-{number}.html
- Regenerates the <main> block of podcasts/index.html
- Removes orphan episode HTML files that no longer appear in episodes.json

Usage:
    python3 scripts/build_podcasts.py           # write everything
    python3 scripts/build_podcasts.py --dry-run # print planned changes only
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PODCAST_DIR = ROOT / "podcasts"
JSON_PATH = PODCAST_DIR / "episodes.json"
INDEX_PATH = PODCAST_DIR / "index.html"

SHOW_URL = "https://open.spotify.com/show/0G3oDMRDDe5AhvKJyZx9tG"

EPISODE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/css/style.css">
    <title>Episode {number} | Alex Arias</title>
</head>
<body id="ep-{body_id}">
    <header id="masthead">
        <h1>
            <a href="/" title="Alex Arias">Alex Arias</a>
        </h1>
    </header>
    <main class="prose">
        <header>
            <div class="podparent">
                <a href="index.html">Podcasts:</a>
            </div>

            <div>
                <h2>Episode {number} — {title}</h2>
                <small>recorded {date}</small>

                <audio controls preload="none" src="{audio_url}"></audio>
                <p>Also on <a href="{show_url}">Spotify</a>.</p>
            </div>
        </header>

{description_html}
    </main>
    <!-- footer:start -->
    <footer>
        <p>&copy; 2026 Alex Arias. All rights reserved.</p>
    </footer>
    <!-- footer:end -->
</body>
</html>
"""


def description_to_html(text: str) -> str:
    if not text:
        return "        <p></p>"
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    rendered = []
    for p in paragraphs:
        escaped = html.escape(p).replace("\n", "<br>")
        rendered.append(f"        <p>{escaped}</p>")
    return "\n".join(rendered)


def filename_for(ep: dict) -> str:
    year_month = ep["date"][:7]  # YYYY-MM
    return f"{year_month}-{ep['number']}.html"


def render_episode(ep: dict) -> str:
    return EPISODE_TEMPLATE.format(
        number=html.escape(ep["number"]),
        body_id=ep["number"],
        title=html.escape(ep["title"]),
        date=ep["date"],
        audio_url=html.escape(ep["audio_url"], quote=True),
        show_url=SHOW_URL,
        description_html=description_to_html(ep["description"]),
    )


def render_index_main(episodes: list) -> str:
    lines = [
        '    <main class="catalog">',
        "",
        "        <h2>Podcasts:</h2>",
        '        <ul class="catalog">',
    ]
    for ep in episodes:
        filename = filename_for(ep)
        year_month = ep["date"][:7]
        blurb = ep.get("blurb", "").strip()
        lines.append("            <li>")
        lines.append(f'                <span class="ep-num">({html.escape(ep["number"])})</span>')
        lines.append(f'                <a href="/podcasts/{filename}">{html.escape(ep["title"])}</a>')
        lines.append(f'                <span class="desc">{year_month}</span>')
        if blurb:
            lines.append(f'                <p class="catalog-detail">{html.escape(blurb)}</p>')
        lines.append("            </li>")
    lines.append("        </ul>")
    lines.append("")
    lines.append("    </main>")
    return "\n".join(lines)


MAIN_RE = re.compile(r"<main\b[^>]*>.*?</main>", re.DOTALL | re.IGNORECASE)


def rebuild_index(episodes: list, dry_run: bool):
    content = INDEX_PATH.read_text(encoding="utf-8")
    new_main = render_index_main(episodes)
    if not MAIN_RE.search(content):
        print("ERROR: couldn't find <main>...</main> in podcasts/index.html", file=sys.stderr)
        sys.exit(1)
    new_content = MAIN_RE.sub(new_main.strip(), content, count=1)
    if dry_run:
        print(f"[dry-run] would rewrite {INDEX_PATH.relative_to(ROOT)}")
    else:
        INDEX_PATH.write_text(new_content, encoding="utf-8")
        print(f"wrote {INDEX_PATH.relative_to(ROOT)}")


def write_episode_pages(episodes: list, dry_run: bool) -> set:
    expected_files = set()
    for ep in episodes:
        filename = filename_for(ep)
        expected_files.add(filename)
        path = PODCAST_DIR / filename
        rendered = render_episode(ep)
        if dry_run:
            print(f"[dry-run] would write {path.relative_to(ROOT)}")
            continue
        path.write_text(rendered, encoding="utf-8")
    if not dry_run:
        print(f"wrote {len(episodes)} episode pages")
    return expected_files


def delete_orphans(expected_files: set, dry_run: bool):
    keep = {"index.html"} | expected_files
    removed = 0
    for path in PODCAST_DIR.glob("*.html"):
        if path.name in keep:
            continue
        if dry_run:
            print(f"[dry-run] would delete orphan {path.relative_to(ROOT)}")
        else:
            path.unlink()
        removed += 1
    if removed and not dry_run:
        print(f"deleted {removed} orphan file(s)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    episodes = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    expected = write_episode_pages(episodes, args.dry_run)
    delete_orphans(expected, args.dry_run)
    rebuild_index(episodes, args.dry_run)


if __name__ == "__main__":
    main()
