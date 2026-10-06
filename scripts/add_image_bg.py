"""Add a derived `image_bg` column holding each photo's own background color.

The supplied photography is inconsistent: 73 of the 102 JPGs are composited on
pure black, the rest on white or cream. Framing them all on one color leaves
harsh seams around whichever group doesn't match.

Instead, each product card is painted with the background color sampled from
its own image, so the photo blends into its tile no matter which it is.

Sampling is per-corner, then a per-channel median across the four corners. The
median rather than the mean means a garment overlapping one corner cannot drag
the result (two corners would have to be covered to shift it, which does not
happen in this catalogue).

`image_bg` is additive and reproducible. Safe to re-run.

Usage:  python scripts/add_image_bg.py
"""

import sqlite3
import statistics
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "campus_customs.db"
IMAGES_DIR = ROOT / "data" / "products"

# Size of the square sampled at each corner. Large enough to average out JPEG
# noise, small enough to stay clear of the garment.
PATCH = 8


def corner_background(path: Path) -> str:
    image = Image.open(path).convert("RGB")
    w, h = image.size

    patches = [
        (0, 0),
        (w - PATCH, 0),
        (0, h - PATCH),
        (w - PATCH, h - PATCH),
    ]

    corner_colors = []
    for x, y in patches:
        region = image.crop((x, y, x + PATCH, y + PATCH))
        # Downsampling to a single pixel with a box filter is just the mean of
        # the patch, without materialising the pixel list.
        corner_colors.append(region.resize((1, 1), Image.Resampling.BOX).getpixel((0, 0)))

    # Per-channel median across the four corners.
    r, g, b = (
        round(statistics.median(c[channel] for c in corner_colors))
        for channel in range(3)
    )
    return f"#{r:02x}{g:02x}{b:02x}"


def main():
    if not DB_PATH.exists():
        raise SystemExit(f"Database not found at {DB_PATH}. Unzip data.zip first.")
    if not IMAGES_DIR.exists():
        raise SystemExit(f"No images at {IMAGES_DIR}. Unzip data.zip first.")

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    columns = {r[1] for r in cur.execute("PRAGMA table_info(catalogue)")}
    if "image_bg" not in columns:
        cur.execute("ALTER TABLE catalogue ADD COLUMN image_bg TEXT")
        print("Added column catalogue.image_bg")
    else:
        print("Column catalogue.image_bg already exists, repopulating")

    rows = cur.execute("SELECT product_id, image_file_path FROM catalogue").fetchall()
    missing = []

    for product_id, image_path in rows:
        path = IMAGES_DIR / Path(image_path).name
        if not path.exists():
            missing.append(product_id)
            continue
        cur.execute(
            "UPDATE catalogue SET image_bg = ? WHERE product_id = ?",
            (corner_background(path), product_id),
        )

    if missing:
        raise SystemExit(f"ERROR: {len(missing)} images not found, e.g. {missing[:3]}")

    nulls = cur.execute(
        "SELECT COUNT(*) FROM catalogue WHERE image_bg IS NULL"
    ).fetchone()[0]
    if nulls:
        raise SystemExit(f"ERROR: {nulls} products still have no image_bg")

    con.commit()

    summary = cur.execute(
        "SELECT image_bg, COUNT(*) AS n FROM catalogue "
        "GROUP BY image_bg ORDER BY n DESC LIMIT 8"
    ).fetchall()
    total = cur.execute("SELECT COUNT(DISTINCT image_bg) FROM catalogue").fetchone()[0]

    print(f"\n{len(rows)} products sampled, {total} distinct background colors")
    print("\nmost common:")
    for color, n in summary:
        print(f"  {color}  {n:>3}")

    con.close()


if __name__ == "__main__":
    main()
