"""Convert a portrait on a solid blue background into an ASCII-art SVG."""
import sys
from html import escape
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

src, out_svg, out_txt = sys.argv[1], sys.argv[2], sys.argv[3]
COLS = int(sys.argv[4]) if len(sys.argv) > 4 else 64
RAMP = " .,:;-~=+*cxoeaO0%#@"

img = Image.open(src).convert("RGB")
CROP = tuple(int(v) for v in sys.argv[6].split(",")) if len(sys.argv) > 6 else None
if CROP:
    img = img.crop(CROP)
INVERT = len(sys.argv) > 7 and sys.argv[7] == "inv"
w, h = img.size

# Mask: background = strongly blue pixels. Also drop the white sticker outline
# that touches the background by eroding the mask a little.
px = img.load()
mask = Image.new("L", img.size, 0)
mp = mask.load()
for y in range(h):
    for x in range(w):
        r, g, b = px[x, y]
        is_bg = b > 120 and b > r + 50 and b > g + 25
        mp[x, y] = 0 if is_bg else 255
mask = mask.filter(ImageFilter.MinFilter(11))  # erode -> removes white outline

gray = ImageOps.grayscale(img)
# local contrast: high-pass blended with original so facial features pop
from PIL import ImageChops
blur = gray.filter(ImageFilter.GaussianBlur(18))
hp = ImageChops.add(ImageChops.subtract(gray, blur, 1, 128), Image.new("L", gray.size, 0))
gray = Image.blend(gray, hp, 0.55)
gray = ImageOps.equalize(gray, mask=mask)          # equalize only the subject
if INVERT:
    gray = ImageOps.invert(gray)
gray = gray.filter(ImageFilter.UnsharpMask(radius=3, percent=160, threshold=2))
GAMMA = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
gray = gray.point(lambda v: int(255 * ((v / 255) ** GAMMA)))

bbox = mask.getbbox()
gray, mask = gray.crop(bbox), mask.crop(bbox)
cw, ch = gray.size
rows = int(COLS * ch / cw * 0.5)  # monospace chars are ~2x taller than wide
gray = gray.resize((COLS, rows), Image.LANCZOS)
mask = mask.resize((COLS, rows), Image.LANCZOS)

lines = []
for y in range(rows):
    row = []
    for x in range(COLS):
        if mask.getpixel((x, y)) < 128:
            row.append(" ")
            continue
        v = gray.getpixel((x, y))
        # dark pixel -> dense glyph (we render light text on a dark bg, so invert)
        idx = int((v / 255) * (len(RAMP) - 1))
        row.append(RAMP[idx])
    lines.append("".join(row).rstrip())

with open(out_txt, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

# --- SVG ---
FS = 11            # font size
LH = FS * 1.0      # line height
CWID = FS * 0.6    # approx monospace advance
PAD = 18
W = int(COLS * CWID + PAD * 2)
H = int(rows * LH + PAD * 2)

text_lines = []
for i, line in enumerate(lines):
    if not line.strip():
        continue
    delay = round(i * 0.035, 3)
    text_lines.append(
        f'<text x="{PAD}" y="{PAD + (i + 1) * LH:.1f}" style="animation-delay:{delay}s">'
        f"{escape(line).replace(' ', '&#160;')}</text>"
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#7dd3fc"/>
      <stop offset="100%" stop-color="#38bdf8"/>
    </linearGradient>
  </defs>
  <style>
    text {{
      font-family: "Fira Code", "JetBrains Mono", Consolas, "Courier New", monospace;
      font-size: {FS}px;
      fill: url(#g);
      white-space: pre;
      opacity: 0;
      animation: in .35s ease-out forwards;
    }}
    @keyframes in {{ to {{ opacity: 1; }} }}
  </style>
  <rect width="100%" height="100%" rx="14" fill="#0d1117"/>
  {chr(10).join("  " + t for t in text_lines)}
</svg>
'''
with open(out_svg, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"{COLS}x{rows} -> {W}x{H}px")
