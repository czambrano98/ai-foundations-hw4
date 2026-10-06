"""Replace the black studio background on product photos with white.

73 of the 102 supplied JPGs were composited on pure black, which reads heavy and
unprofessional on a light storefront. This flood-fills the background inward
from the image border and writes white-background copies to
`data/products_web/`.

Originals in `data/products/` are never modified. The backend prefers
`products_web/` when it exists and falls back to the originals, so deleting the
output directory cleanly reverts the change.

Why the threshold is so tight: measured across the source images, the
background is exactly (0, 0, 0) while even the darkest navy garment pixels sum
to roughly 40-180 across RGB. A loose tolerance leaks through the shadowed folds
of a navy hoodie and dissolves the whole garment, so the fill only accepts
pixels summing to 6 or less.

Usage:  python scripts/whiten_product_images.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "products"
DEST = ROOT / "data" / "products_web"

# Max sum of RGB for a pixel to count as background. See module docstring.
THRESHOLD = 6

# Average corner brightness below which an image is treated as black-background.
DARK_CORNER_MAX = 60

# Spacing of flood-fill seed points along each edge. Fills are cheap once a
# region is already white, so this mainly guards against a background split
# into separate regions by a garment touching the frame edge.
SEED_STEP = 10


def corner_brightness(image: Image.Image) -> float:
    w, h = image.size
    pts = [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]
    return sum(sum(image.getpixel(p)) for p in pts) / 12


def whiten(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    w, h = image.size
    white = (255, 255, 255)

    def seed(x, y):
        if sum(image.getpixel((x, y))) <= THRESHOLD:
            ImageDraw.floodfill(image, (x, y), white, thresh=THRESHOLD)

    for x in range(1, w - 1, SEED_STEP):
        seed(x, 1)
        seed(x, h - 2)
    for y in range(1, h - 1, SEED_STEP):
        seed(1, y)
        seed(w - 2, y)

    return image


def main():
    if not SOURCE.exists():
        raise SystemExit(f"No source images at {SOURCE}. Unzip data.zip first.")

    DEST.mkdir(parents=True, exist_ok=True)
    whitened = copied = 0

    for path in sorted(SOURCE.glob("*.jpg")):
        image = Image.open(path).convert("RGB")
        if corner_brightness(image) < DARK_CORNER_MAX:
            whiten(image).save(DEST / path.name, "JPEG", quality=92)
            whitened += 1
        else:
            # Already on white; copy through so one directory serves everything.
            image.save(DEST / path.name, "JPEG", quality=92)
            copied += 1

    print(f"Wrote {whitened + copied} images to {DEST.relative_to(ROOT)}")
    print(f"  {whitened} black backgrounds whitened")
    print(f"  {copied} already white, copied through")


if __name__ == "__main__":
    main()
