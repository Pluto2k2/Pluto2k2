"""Generate a pixel-art header SVG (8-bit space scene + pixel-font name).

Usage: python scripts/build_pixel_header.py assets/header.svg
"""
import math
import random
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets/header.svg"
CELL = 6                 # px per pixel-art cell
GW, GH = 200, 50         # grid size in cells -> 1200 x 300 px
W, H = GW * CELL, GH * CELL
random.seed(7)

# ---------------------------------------------------------------- 5x7 font
FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "*": [".....", ".....", ".....", "..#..", ".....", ".....", "....."],
    ">": ["#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."],
    " ": ["....."] * 7,
}

rects = []  # (x_px, y_px, w_px, h_px, color, cls)


def px(x, y, color, size=CELL, cls=None, w=1):
    rects.append((x * size, y * size, w * size, size, color, cls))


def text(s, x, y, size, colors, gap=1, shadow=None):
    """Draw string at grid (x, y) on a grid of `size` px. colors: list per glyph row."""
    cx = x
    for ch in s:
        g = FONT[ch]
        for r, row in enumerate(g):
            for c, bit in enumerate(row):
                if bit == "#":
                    if shadow:
                        rects.append(((cx + c) * size + size // 2, (y + r) * size + size // 2, size, size, shadow, None))
        cx += 5 + gap
    cx = x
    for ch in s:
        g = FONT[ch]
        for r, row in enumerate(g):
            run = None
            for c, bit in enumerate(row + "."):
                if bit == "#" and run is None:
                    run = c
                elif bit != "#" and run is not None:
                    rects.append(((cx + run) * size, (y + r) * size, (c - run) * size, size, colors[r], None))
                    run = None
        cx += 5 + gap
    return cx


# ---------------------------------------------------------------- background
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
BANDS = ["#060a1c", "#0a1030", "#0f1840", "#15204f", "#1b295e"]
for y in range(GH):
    t = y / (GH - 1) * (len(BANDS) - 1)
    lo = int(t)
    hi = min(lo + 1, len(BANDS) - 1)
    frac = t - lo
    row = []
    for x in range(GW):
        row.append(BANDS[hi] if frac * 16 > BAYER[y % 4][x % 4] else BANDS[lo])
    # merge runs
    start = 0
    for x in range(1, GW + 1):
        if x == GW or row[x] != row[start]:
            rects.append((start * CELL, y * CELL, (x - start) * CELL, CELL, row[start], None))
            start = x

# ---------------------------------------------------------------- stars
PLANET = (158, 26, 17)
MOON = (186, 11, 4)


def free(x, y):
    for cx, cy, r in (PLANET, MOON):
        if (x - cx) ** 2 + (y - cy) ** 2 <= (r + 2) ** 2:
            return False
    return not (8 <= x <= 104 and 6 <= y <= 44)  # keep text area calm


for _ in range(110):
    x, y = random.randrange(1, GW - 1), random.randrange(1, GH - 1)
    if free(x, y):
        color = random.choice(["#ffffff", "#c7d2fe", "#a5b4fc", "#fde68a"])
        px(x, y, color, cls=random.choice(["s1", "s2", "s3", None, None]))
# a few bigger "plus" stars
for x, y in [(118, 8), (132, 40), (6, 46), (112, 24), (194, 44), (140, 4)]:
    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
        px(x + dx, y + dy, "#ffffff" if (dx, dy) == (0, 0) else "#93c5fd", cls="s2")

# ---------------------------------------------------------------- planets
def sphere(cx, cy, r, tones, heart=False):
    lx, ly, lz = -0.55, -0.55, 0.63
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            dx, dy = (x - cx) / r, (y - cy) / r
            d2 = dx * dx + dy * dy
            if d2 > 1:
                continue
            dz = math.sqrt(1 - d2)
            light = max(0.0, dx * lx + dy * ly + dz * lz)
            v = light * (len(tones) - 1)
            i = int(v)
            if (v - i) * 16 > BAYER[y % 4][x % 4]:
                i = min(i + 1, len(tones) - 1)
            color = tones[i]
            if heart:
                # Pluto's heart (Tombaugh Regio), lower-left of centre
                hx, hy = (dx + 0.12) / 0.42, (dy - 0.2) / 0.42
                hy = -hy
                if (hx * hx + hy * hy - 1) ** 3 - hx * hx * hy ** 3 < 0:
                    color = "#f6e7d2" if light > 0.35 else "#d8c2a6"
            px(x, y, color)


sphere(*PLANET, ["#2a1a14", "#5b3a29", "#8a5a3c", "#b9875f", "#e2b98f"], heart=True)
sphere(*MOON, ["#1f2433", "#4b5563", "#8b93a3", "#c9ced8"])

# ---------------------------------------------------------------- text
NAME_COLORS = ["#fef3c7", "#fde68a", "#fde68a", "#fcd34d", "#fbbf24", "#f59e0b", "#d97706"]
# handle line (small, 3px grid)
end = text("> PLUTO2K2", 28, 22, 3, ["#67e8f9"] * 7)
# name (big, 12px pixels = 2 cells)
end = text("OUSSAMA", 7, 8, 12, NAME_COLORS, gap=1, shadow="#3b1d6e")
cursor_x = end * 12 + 4
# subtitle (3px grid)
text("SOFTWARE ENGINEERING * FULL-STACK", 28, 68, 3, ["#c7d2fe"] * 7)

# ---------------------------------------------------------------- frame
FRAME = "#3b4a8a"
for x in range(2, GW - 2):
    px(x, 0, FRAME); px(x, GH - 1, FRAME)
for y in range(2, GH - 2):
    px(0, y, FRAME); px(GW - 1, y, FRAME)
for x, y in [(1, 1), (GW - 2, 1), (1, GH - 2), (GW - 2, GH - 2)]:
    px(x, y, FRAME)

# ---------------------------------------------------------------- svg
body = []
for x, y, w, h, c, cls in rects:
    k = f' class="{cls}"' if cls else ""
    body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"{k}/>')

# shooting star (animated group)
trail = "".join(
    f'<rect x="{-i*CELL}" y="{-i*CELL}" width="{CELL}" height="{CELL}" fill="#ffffff" opacity="{1 - i*0.18:.2f}"/>'
    for i in range(6)
)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" shape-rendering="crispEdges">
<style>
  .s1 {{ animation: tw 2.4s steps(2) infinite; }}
  .s2 {{ animation: tw 3.1s steps(2) .8s infinite; }}
  .s3 {{ animation: tw 1.7s steps(2) .3s infinite; }}
  @keyframes tw {{ 50% {{ opacity: .15; }} }}
  .cur {{ animation: bl 1s steps(1) infinite; }}
  @keyframes bl {{ 50% {{ opacity: 0; }} }}
  .shoot {{ animation: sh 7s linear infinite; opacity: 0; }}
  @keyframes sh {{
    0% {{ transform: translate({W*0.55:.0f}px, -20px); opacity: 0; }}
    3% {{ opacity: 1; }}
    14% {{ transform: translate({W*0.85:.0f}px, {H*0.6:.0f}px); opacity: 0; }}
    100% {{ transform: translate({W*0.85:.0f}px, {H*0.6:.0f}px); opacity: 0; }}
  }}
</style>
{chr(10).join(body)}
<rect class="cur" x="{cursor_x}" y="{8*12}" width="{CELL*2}" height="{7*12}" fill="#67e8f9"/>
<g class="shoot">{trail}</g>
</svg>
'''
open(OUT, "w", encoding="utf-8").write(svg)
print(f"{W}x{H}, {len(rects)} rects, {len(svg)//1024} KB")
