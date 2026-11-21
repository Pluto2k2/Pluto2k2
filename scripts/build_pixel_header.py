"""Generate a pixel-art header SVG: 8-bit space scene, pixel-font name and mascots.

Usage: python scripts/build_pixel_header.py assets/pixel-header.svg
"""
import math
import random
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets/pixel-header.svg"
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

rects = []  # static scene: (x_px, y_px, w_px, h_px, color, cls)


def px(x, y, color, cls=None, out=None):
    (rects if out is None else out).append((x * CELL, y * CELL, CELL, CELL, color, cls))


def text(s, x, y, size, colors, gap=1, shadow=None):
    """Draw string at grid (x, y) on a grid of `size` px. colors: one per glyph row."""
    if shadow:
        cx = x
        for ch in s:
            for r, row in enumerate(FONT[ch]):
                for c, bit in enumerate(row):
                    if bit == "#":
                        rects.append(((cx + c) * size + size // 2, (y + r) * size + size // 2,
                                      size, size, shadow, None))
            cx += 5 + gap
    cx = x
    for ch in s:
        for r, row in enumerate(FONT[ch]):
            run = None
            for c, bit in enumerate(row + "."):
                if bit == "#" and run is None:
                    run = c
                elif bit != "#" and run is not None:
                    rects.append(((cx + run) * size, (y + r) * size, (c - run) * size, size, colors[r], None))
                    run = None
        cx += 5 + gap
    return cx


def svg_rects(items):
    out = []
    for x, y, w, h, c, cls in items:
        k = f' class="{cls}"' if cls else ""
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"{k}/>')
    return "".join(out)


def sprite(rows, x0, y0, pal, cls_map=None):
    """Turn a char grid into rects (runs merged). '.' is transparent."""
    cls_map = cls_map or {}
    items = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            ch = row[c]
            if ch == ".":
                c += 1
                continue
            start = c
            while c < len(row) and row[c] == ch:
                c += 1
            items.append(((x0 + start) * CELL, (y0 + r) * CELL, (c - start) * CELL, CELL,
                          pal[ch], cls_map.get(ch)))
    return items


BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

# ---------------------------------------------------------------- background
BANDS = ["#060a1c", "#0a1030", "#0f1840", "#15204f", "#1b295e"]
NEB = ["#22184f", "#2e1d63", "#3a2270"]
NEB_CENTERS = [(150, 10, 46), (30, 50, 34), (196, 46, 22)]


def nebula(x, y):
    n = (math.sin(x * 0.11 + y * 0.07) + math.sin(x * 0.05 - y * 0.19 + 1.3)
         + math.sin((x + y) * 0.08 + 2.1)) / 3 * 0.5 + 0.5
    k = 0.0
    for cx, cy, r in NEB_CENTERS:
        d = math.hypot(x - cx, (y - cy) * 2) / r
        k = max(k, 1 - d)
    return max(0.0, n * k * 1.6)


for y in range(GH):
    t = y / (GH - 1) * (len(BANDS) - 1)
    lo = int(t)
    hi = min(lo + 1, len(BANDS) - 1)
    frac = t - lo
    row = []
    for x in range(GW):
        b = BAYER[y % 4][x % 4]
        color = BANDS[hi] if frac * 16 > b else BANDS[lo]
        v = nebula(x, y) * len(NEB)
        i = int(v)
        if (v - i) * 16 > b:
            i += 1
        if i > 0:
            color = NEB[min(i, len(NEB)) - 1]
        row.append(color)
    start = 0
    for x in range(1, GW + 1):
        if x == GW or row[x] != row[start]:
            rects.append((start * CELL, y * CELL, (x - start) * CELL, CELL, row[start], None))
            start = x

# ---------------------------------------------------------------- layout
PLUTO = (158, 26, 17)
MOON = (186, 11, 4)
RINGED = (187, 39, 5)
UFO_AT = (117, 2)
ASTRO_AT = (118, 19)
SAT_AT = (3, 3)
KEEP_OUT = [  # x0, y0, x1, y1 (cells) where no stars go
    (12, 8, 104, 40),        # text
    (114, 1, 135, 38),       # ufo + beam + astronaut
    (2, 2, 15, 8),           # satellite
    (174, 32, 199, 47),      # ringed planet
]


def free(x, y):
    for cx, cy, r in (PLUTO, MOON):
        if (x - cx) ** 2 + (y - cy) ** 2 <= (r + 2) ** 2:
            return False
    return not any(a <= x <= c and b <= y <= d for a, b, c, d in KEEP_OUT)


# ---------------------------------------------------------------- stars
for _ in range(130):
    x, y = random.randrange(1, GW - 1), random.randrange(1, GH - 1)
    if free(x, y):
        color = random.choice(["#ffffff", "#c7d2fe", "#a5b4fc", "#fde68a"])
        px(x, y, color, cls=random.choice(["s1", "s2", "s3", None, None]))
for x, y in [(132, 42), (6, 44), (140, 4), (178, 26), (60, 46), (94, 4)]:
    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
        px(x + dx, y + dy, "#ffffff" if (dx, dy) == (0, 0) else "#93c5fd", cls="s2")


# ---------------------------------------------------------------- planets
def sphere(cx, cy, r, tones, craters=()):
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
            for kx, ky, kr in craters:
                dd = math.hypot(dx - kx, dy - ky)
                if dd < kr:
                    i = max(0, i - 1)
                elif dd < kr + 0.07 and (dx - kx) + (dy - ky) > 0:
                    i = min(len(tones) - 1, i + 1)   # lit rim on the far side
            px(x, y, tones[i])


sphere(*PLUTO, ["#2a1a14", "#5b3a29", "#8a5a3c", "#b9875f", "#e2b98f"],
       craters=[(-0.35, -0.15, 0.17), (0.2, 0.35, 0.14), (0.38, -0.38, 0.1),
                (-0.15, 0.55, 0.1), (0.05, -0.05, 0.08)])
sphere(*MOON, ["#1f2433", "#4b5563", "#8b93a3", "#c9ced8"], craters=[(0.2, 0.1, 0.25)])

# ringed planet: back half of ring, planet, front half of ring
rcx, rcy, rr = RINGED
ring = []
for x in range(rcx - 11, rcx + 12):
    y = rcy + round((x - rcx) * -0.3)
    ring.append((x, y))
    if abs(x - rcx) <= 8:
        ring.append((x, y + 1))
for x, y in ring:
    if y < rcy and abs(x - rcx) <= rr:
        px(x, y, "#a78bfa")
sphere(rcx, rcy, rr, ["#3b1f6e", "#6d3fc0", "#a78bfa", "#ddd6fe"])
for x, y in ring:
    if not (y < rcy and abs(x - rcx) <= rr):
        px(x, y, "#f0abfc" if abs(x - rcx) > rr else "#e9d5ff")

# ---------------------------------------------------------------- text
NAME_COLORS = ["#fef3c7", "#fde68a", "#fde68a", "#fcd34d", "#fbbf24", "#f59e0b", "#d97706"]
text("> PLUTO2K2", 28, 22, 3, ["#67e8f9"] * 7)
end = text("OUSSAMA", 7, 8, 12, NAME_COLORS, gap=1, shadow="#3b1d6e")
cursor_x = end * 12 + 4
text("SOFTWARE ENGINEERING * FULL-STACK", 28, 68, 3, ["#c7d2fe"] * 7)

# ---------------------------------------------------------------- mascots
OUTL = "#0b1020"

ASTRO = [
    "....OOOOOO....",
    "...OWWWWWWO...",
    "..OWWWWWWWWO..",
    "..OWVVVVVVWO..",
    "..OWVvvVVVWO..",
    "..OWVvVVVVWO..",
    "..OWWVVVVWWO..",
    "...OWWWWWWO...",
    ".OOOWWWWWWOOO.",
    "OWWOWWRRWWOWWO",
    "OWWOWWWWWWOWWO",
    "OGWOWWGGWWOWGO",
    ".OOOWWWWWWOOO.",
    "...OWWWWWWO...",
    "...OWWOOWWO...",
    "...OWWOOWWO...",
    "...OGGOOGGO...",
    "...OOOOOOOO...",
]
ASTRO_PAL = {"O": OUTL, "W": "#f1f5f9", "G": "#94a3b8", "V": "#0ea5e9",
             "v": "#bae6fd", "R": "#f87171"}

UFO = [
    "......OOOO......",
    ".....OaaaaO.....",
    "....OaEaaEaO....",
    "..OOGGGGGGGGOO..",
    ".OGHHHHHHHHHHGO.",
    "OGG1GG2GG3GG1GGO",
    ".OOGGGGGGGGGGOO.",
    "...OOOOOOOOOO...",
]
UFO_PAL = {"O": OUTL, "a": "#4ade80", "E": "#052e16", "G": "#94a3b8", "H": "#cbd5e1",
           "1": "#facc15", "2": "#f472b6", "3": "#22d3ee"}

ROCKET = [
    "...OOO............",
    "...ORRO...........",
    "..OOWWWOOOOOO.....",
    "FFOWWWWWWWWWWOO...",
    "YFOWWWWWVVWWWWWOO.",
    "FFOWWWWWWWWWWOO...",
    "..OOWWWOOOOOO.....",
    "...ORRO...........",
    "...OOO............",
]
ROCKET_PAL = {"O": OUTL, "R": "#ef4444", "W": "#e2e8f0", "V": "#38bdf8",
              "F": "#f97316", "Y": "#fde047"}

SAT = [
    "BBBB...BBBB",
    "bBbBOGObBbB",
    "BBBBOLOBBBB",
    "bBbBOGObBbB",
    "BBBB.O.BBBB",
]
SAT_PAL = {"B": "#1d4ed8", "b": "#60a5fa", "O": OUTL, "G": "#94a3b8", "L": "#f87171"}

ux, uy = UFO_AT
beam = []
for i, y in enumerate(range(uy + 8, ASTRO_AT[1] + 2)):
    half = 3 + i // 2
    cx = ux + 8
    for x in range(cx - half, cx + half):
        beam.append((x * CELL, y * CELL, CELL, CELL, "#67e8f9", None))

astro = sprite(ASTRO, *ASTRO_AT, ASTRO_PAL)
ufo = sprite(UFO, *UFO_AT, UFO_PAL, {"1": "l1", "2": "l2", "3": "l3"})
rocket = sprite(ROCKET, 8, 40, ROCKET_PAL, {"F": "fl", "Y": "fl2"})
sat = sprite(SAT, *SAT_AT, SAT_PAL, {"L": "l2"})

# ---------------------------------------------------------------- frame
frame = []
FRAME = "#3b4a8a"
for x in range(2, GW - 2):
    px(x, 0, FRAME, out=frame); px(x, GH - 1, FRAME, out=frame)
for y in range(2, GH - 2):
    px(0, y, FRAME, out=frame); px(GW - 1, y, FRAME, out=frame)
for x, y in [(1, 1), (GW - 2, 1), (1, GH - 2), (GW - 2, GH - 2)]:
    px(x, y, FRAME, out=frame)

# ---------------------------------------------------------------- svg
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
  .astro {{ animation: bob 3.2s ease-in-out infinite; }}
  @keyframes bob {{ 50% {{ transform: translateY(-10px); }} }}
  .ufo {{ animation: hover 2.4s ease-in-out infinite; }}
  @keyframes hover {{ 50% {{ transform: translateY(5px); }} }}
  .beam {{ opacity: .38; animation: beam 2.4s ease-in-out infinite; }}
  @keyframes beam {{ 50% {{ opacity: .16; }} }}
  .l1 {{ animation: bl .9s steps(1) infinite; }}
  .l2 {{ animation: bl .9s steps(1) .3s infinite; }}
  .l3 {{ animation: bl .9s steps(1) .6s infinite; }}
  .rocket {{ animation: fly 16s linear infinite; }}
  @keyframes fly {{ from {{ transform: translateX(-260px); }} to {{ transform: translateX({W + 150}px); }} }}
  .fl {{ animation: bl .24s steps(1) infinite; }}
  .fl2 {{ animation: bl .24s steps(1) .12s infinite; }}
  .sat {{ animation: drift 6s ease-in-out infinite; }}
  @keyframes drift {{ 50% {{ transform: translate(4px, 3px); }} }}
  .shoot {{ animation: sh 7s linear infinite; opacity: 0; }}
  @keyframes sh {{
    0% {{ transform: translate({W*0.55:.0f}px, -20px); opacity: 0; }}
    3% {{ opacity: 1; }}
    14% {{ transform: translate({W*0.85:.0f}px, {H*0.6:.0f}px); opacity: 0; }}
    100% {{ transform: translate({W*0.85:.0f}px, {H*0.6:.0f}px); opacity: 0; }}
  }}
</style>
{svg_rects(rects)}
<rect class="cur" x="{cursor_x}" y="{8*12}" width="{CELL*2}" height="{7*12}" fill="#67e8f9"/>
<g class="sat">{svg_rects(sat)}</g>
<g class="ufo"><g class="beam">{svg_rects(beam)}</g>{svg_rects(ufo)}</g>
<g class="astro">{svg_rects(astro)}</g>
<g class="rocket">{svg_rects(rocket)}</g>
<g class="shoot">{trail}</g>
{svg_rects(frame)}
</svg>
'''
open(OUT, "w", encoding="utf-8").write(svg)
print(f"{W}x{H}, {len(svg)//1024} KB")
