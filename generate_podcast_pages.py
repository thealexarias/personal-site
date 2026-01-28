from pathlib import Path
from datetime import date, timedelta

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
    number: string like "0.1", "0.5", "1", "124"
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

    # ---- Pre-series episodes with Cesar: 0.1–0.5 ----
    # Dates given by you (MM/DD/YYYY):
    # ep 0.1 10/25/2020
    # ep 0.2 12/10/2020
    # ep 0.3 12/10/2020
    # ep 0.4 1/10/2021
    # ep 0.5 2/10/2023 (after ep 1, but you want it numbered 0.5)
    pre_episodes = [
        ("0.1", date(2020, 10, 25)),
        ("0.2", date(2020, 12, 10)),
        ("0.3", date(2020, 12, 10)),
        ("0.4", date(2021, 1, 10)),
        ("0.5", date(2023, 2, 10)),
    ]

    for number, recorded_date in pre_episodes:
        write_episode_file(number, recorded_date)

    # ---- Main run: episodes 1–124, one per day ----
    # ep 1  recorded 2023-02-01
    # ep 124 recorded 2023-06-04
    start_date = date(2023, 2, 1)  # episode 1
    for n in range(1, 125):  # 1 through 124 inclusive
        recorded_date = start_date + timedelta(days=n - 1)
        write_episode_file(str(n), recorded_date)

if __name__ == "__main__":
    main()
