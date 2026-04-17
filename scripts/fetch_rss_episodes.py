#!/usr/bin/env python3
"""
Fetch podcast episodes from the Spotify for Creators RSS feed and write
podcasts/episodes.json. Merges with any existing JSON so hand-written
blurbs survive re-runs (matched on audio_url).

Usage:
    python3 scripts/fetch_rss_episodes.py
"""

import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import urlopen

RSS_URL = "https://anchor.fm/s/10118647c/podcast/rss"

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "podcasts" / "episodes.json"

# Normal format: "137: Title 6/10/2025" or "136: Book Club: 11 - 5/16/2025"
TITLE_RE = re.compile(
    r"^(\d+(?:\.\d+)?):\s*(.+?)\s*[-–—]?\s*(\d{1,2})/(\d{1,2})/(\d{2,4})\s*$"
)
# "Opposite" format used on exactly one episode: "2023/18/4 Opposite Podcast: 77"
# — year/day/month then title then episode number.
OPPOSITE_RE = re.compile(
    r"^(\d{4})/(\d{1,2})/(\d{1,2})\s+(.+?):\s+(\d+(?:\.\d+)?)\s*$"
)

TAG_RE = re.compile(r"<[^>]+>")


def normalize_date(year: str, month: str, day: str) -> str:
    y = int(year)
    if y < 100:
        y += 2000
    return f"{y:04d}-{int(month):02d}-{int(day):02d}"


def parse_title(title: str):
    m = TITLE_RE.match(title)
    if m:
        num, t, mo, d, y = m.groups()
        return num, t.strip(), normalize_date(y, mo, d)
    m = OPPOSITE_RE.match(title)
    if m:
        y, d, mo, t, num = m.groups()
        return num, t.strip(), normalize_date(y, mo, d)
    return None


def strip_html(text: str) -> str:
    """Turn HTML-in-description into readable plain text."""
    text = re.sub(r"</p\s*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</li\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<li[^>]*>", "• ", text, flags=re.IGNORECASE)
    text = TAG_RE.sub("", text)
    text = html.unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def parse_feed(xml_bytes: bytes):
    root = ET.fromstring(xml_bytes)
    channel = root.find("channel")
    episodes = []
    warnings = []
    for item in channel.findall("item"):
        raw_title = (item.findtext("title") or "").strip()
        raw_desc = (item.findtext("description") or "").strip()
        enclosure = item.find("enclosure")
        audio_url = enclosure.get("url") if enclosure is not None else ""

        parsed = parse_title(raw_title)
        if parsed:
            number, title, date = parsed
        else:
            number, title, date = "", raw_title, ""
            warnings.append(raw_title)

        episodes.append({
            "number": number,
            "title": title,
            "date": date,
            "audio_url": audio_url,
            "description": strip_html(raw_desc),
            "blurb": "",
        })
    return episodes, warnings


def sort_key(ep):
    num = ep.get("number", "")
    if not num:
        return (1, 0, 0)  # unparseable entries to the bottom
    main, _, sub = num.partition(".")
    try:
        main_i = int(main)
    except ValueError:
        return (1, 0, 0)
    sub_i = int(sub) if sub.isdigit() else 0
    return (0, -main_i, -sub_i)


def merge_blurbs(new_eps):
    if not JSON_PATH.exists():
        return new_eps
    existing = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    blurbs = {
        e["audio_url"]: e.get("blurb", "")
        for e in existing
        if e.get("audio_url") and e.get("blurb")
    }
    for e in new_eps:
        if e["audio_url"] in blurbs:
            e["blurb"] = blurbs[e["audio_url"]]
    return new_eps


def main():
    print(f"Fetching {RSS_URL}")
    with urlopen(RSS_URL) as resp:
        xml_bytes = resp.read()

    episodes, warnings = parse_feed(xml_bytes)
    episodes = merge_blurbs(episodes)
    episodes.sort(key=sort_key)

    JSON_PATH.parent.mkdir(exist_ok=True)
    JSON_PATH.write_text(
        json.dumps(episodes, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(episodes)} episodes to {JSON_PATH.relative_to(ROOT)}")

    if warnings:
        print(f"\n{len(warnings)} unparseable title(s) — fix manually in episodes.json:")
        for w in warnings:
            print(f"  - {w}")


if __name__ == "__main__":
    main()
