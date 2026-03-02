from pathlib import Path
import re
from datetime import datetime

ROOT = Path(__file__).parent.parent
PODCAST_DIR = ROOT / "podcasts"
INDEX_FILE = PODCAST_DIR / "index.html"

# Regexes to pull data out of each episode file
H2_RE = re.compile(r"<h2>\s*Episode\s+([^ ]+)\s+—", re.IGNORECASE)
DATE_RE = re.compile(r"<small>\s*recorded\s+(\d{4}-\d{2}-\d{2})\s*</small>", re.IGNORECASE)

SECTION_TEMPLATE = """        <section>
            <h3>
                <a href="/podcasts/{filename}">{episode_number}: </a>
            </h3>
            <p>description section</p>
        </section>
"""

def parse_episode_file(path: Path):
    """
    Return (episode_number:str, recorded_date:datetime.date) or None if we can't parse.
    """
    text = path.read_text(encoding="utf-8")

    h2_match = H2_RE.search(text)
    date_match = DATE_RE.search(text)

    if not h2_match or not date_match:
        return None

    ep_number = h2_match.group(1).strip()
    date_str = date_match.group(1).strip()

    try:
        rec_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None

    return ep_number, rec_date

def episode_sort_key(item):
    """
    Sort by recorded_date desc, then by episode number desc (handling decimals like 41.1, 0.5).
    item = (filename, ep_number, rec_date)
    """
    filename, ep_number, rec_date = item

    # main and sub for things like "41.1", "0.5"
    if "." in ep_number:
        main, sub = ep_number.split(".", 1)
    else:
        main, sub = ep_number, "0"

    try:
        main_i = int(main)
    except ValueError:
        main_i = -9999  # weird cases go last

    try:
        sub_i = int(sub)
    except ValueError:
        sub_i = 0

    # We want newest first, so sort by -date, then -main_i, then -sub_i
    return (-rec_date.toordinal(), -main_i, -sub_i)

def main():
    if not INDEX_FILE.exists():
        raise FileNotFoundError("podcasts/index.html not found")

    items = []

    for file in PODCAST_DIR.iterdir():
        if not file.is_file():
            continue
        if file.name == "index.html":
            continue
        if not file.name.endswith(".html"):
            continue

        parsed = parse_episode_file(file)
        if not parsed:
            # Skip files we can't parse (e.g., not yet in Episode N format)
            continue

        ep_number, rec_date = parsed
        items.append((file.name, ep_number, rec_date))

    # Sort with our custom key
    items.sort(key=episode_sort_key)

    sections_html = ""
    for filename, ep_number, rec_date in items:
        sections_html += SECTION_TEMPLATE.format(
            filename=filename,
            episode_number=ep_number,
        )

    new_main = f"""
    <main>

        <section>
            <h2>Podcasts:</h2>
        </section>

{sections_html.rstrip()}
    </main>
"""

    content = INDEX_FILE.read_text(encoding="utf-8")
    content = re.sub(
        r"<main>.*?</main>",
        new_main,
        content,
        flags=re.DOTALL,
    )

    INDEX_FILE.write_text(content, encoding="utf-8")
    print("Updated podcasts/index.html")

if __name__ == "__main__":
    main()
