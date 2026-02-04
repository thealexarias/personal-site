from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent
PODCAST_DIR = ROOT / "podcasts"

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/css/style.css">
    <title>Episode {number} | Alex Arias</title>
</head>
<body id="ep-{number}">
    <header id="masthead">
        <h1>
            <a href="/" title="Alex Arias">Alex Arias</a>
        </h1>
    </header>
    <main>
        <header>
            <div class="podparent">
                <a href="index.html">Podcasts:</a>
            </div>

            <div>
                <h2>Episode {number} — TODO TITLE</h2>
                <small>recorded {recorded_date}</small>

                <iframe
                    style="border-radius:12px"
                    src="https://open.spotify.com/embed/episode/TODO-EPISODE-ID"
                    width="100%"
                    height="152"
                    frameborder="0"
                    allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                    loading="lazy">
                </iframe>
            </div>
        </header>

        <p>This my episode {number} podcast</p>
    </main>
</body>
</html>
"""

def write_episode_file(number: str, recorded_date: date):
    """
    number: string like "41.1", "125", "137"
    recorded_date: datetime.date object
    """
    recorded_str = recorded_date.isoformat()  # YYYY-MM-DD
    year_month = recorded_date.strftime("%Y-%m")  # YYYY-MM

    # filename: YYYY-MM-<episode-number>.html
    filename = f"{year_month}-{number}.html"
    html_path = PODCAST_DIR / filename

    # don't overwrite existing files
    if html_path.exists():
        print(f"Skipping existing file: {html_path.relative_to(ROOT)}")
        return

    html = TEMPLATE.format(
        number=number,
        recorded_date=recorded_str,
    )

    html_path.write_text(html, encoding="utf-8")
    print(f"Created {html_path.relative_to(ROOT)}")

def main():
    PODCAST_DIR.mkdir(exist_ok=True)

    # Episodes and dates (MM/DD/YYYY -> YYYY-MM-DD)
    extra_eps = [
        ("41.1", date(2023, 3, 10)),  # 3/10/2023
        ("41.2", date(2023, 3, 14)),  # 3/14/2023
        ("125",  date(2023, 9, 25)),  # 9/25/2023
        ("126",  date(2025, 2, 14)),  # 2/14/2025
        ("127",  date(2025, 2, 21)),  # 2/21/2025
        ("128",  date(2025, 2, 28)),  # 2/28/2025
        ("129",  date(2025, 3, 7)),   # 3/7/2025
        ("130",  date(2025, 3, 14)),  # 3/14/2025
        ("131",  date(2025, 3, 21)),  # 3/21/2025
        ("132",  date(2025, 3, 28)),  # 3/28/2025
        ("133",  date(2025, 4, 4)),   # 4/4/2025
        ("134",  date(2025, 4, 11)),  # 4/11/2025
        ("135",  date(2025, 4, 18)),  # 4/18/2025
        ("136",  date(2025, 5, 16)),  # 5/16/2025
        ("137",  date(2025, 6, 10)),  # 6/10/2025
    ]

    for number, recorded_date in extra_eps:
        write_episode_file(number, recorded_date)

if __name__ == "__main__":
    main()
