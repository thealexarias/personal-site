import os
from pathlib import Path

ROOT = Path(__file__).parent
AUDIO_DIR = ROOT / "audio"
PODCAST_DIR = ROOT / "podcasts"

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/css/style.css">
    <title>{title} | Alex Arias</title>
</head>
<body id="{body_id}">
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
                <h2>{title}</h2>
                <small>recorded ????-??-??</small>
            </div>

            <audio src="../audio/{audio_filename}" preload="none" controls></audio>
        </header>

        <p>placeholder for description or something</p>
    </main>
</body>
</html>
"""

def slugify(s: str) -> str:
    """Very simple slug/id generator."""
    return "".join(c.lower() if c.isalnum() else "-" for c in s).strip("-")

def main():
    PODCAST_DIR.mkdir(exist_ok=True)

    audio_files = sorted(
        f for f in AUDIO_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in {".mp3", ".m4a"}
    )

    if not audio_files:
        print("No audio files found in ./audio")
        return

    for audio in audio_files:
        base = audio.stem  # e.g. "0" from "0.mp3"
        html_name = f"{base}.html"
        html_path = PODCAST_DIR / html_name

        if html_path.exists():
            print(f"Skipping existing file: {html_path}")
            continue

        # For now, use a generic title you can edit later
        title = f"Episode {base}"
        body_id = f"ep-{slugify(base)}"

        html_content = TEMPLATE.format(
            title=title,
            body_id=body_id,
            audio_filename=audio.name,
        )

        html_path.write_text(html_content, encoding="utf-8")
        print(f"Created {html_path}")

if __name__ == "__main__":
    main()
