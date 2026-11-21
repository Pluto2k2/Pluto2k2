"""Compose a neofetch-style header SVG: ASCII face (left) + info panel (right)."""
import sys
from html import escape

face_txt, out_svg = sys.argv[1], sys.argv[2]
face = open(face_txt, encoding="utf-8").read().rstrip("\n").split("\n")

FS = 11
CW = FS * 0.6          # monospace advance
LH = FS * 1.05
PAD = 28
BAR = 34               # window title bar height
face_cols = max(len(l) for l in face)

INFO = [
    ("title", "oussama@github"),
    ("rule", ""),
    ("kv", ("Name", "Oussama")),
    ("kv", ("Handle", "Pluto2k2")),
    ("kv", ("Role", "AI & Software Engineering")),
    ("kv", ("Focus", "NFR classification · LLMs")),
    ("kv", ("Languages", "Python · TypeScript · JavaScript")),
    ("kv", ("AI", "Classic ML · Deep Learning · LLMs")),
    ("kv", ("LLM Stack", "Llama 3.3 via Groq")),
    ("kv", ("Web", "Full-stack apps")),
    ("kv", ("Projects", "Requify · NFR-Decision-Tree")),
    ("kv", ("", "LAB2MARKET · ResearchPath")),
    ("kv", ("Status", "Always learning")),
    ("blank", ""),
    ("colors", ""),
]

info_x = PAD + face_cols * CW + 40
ICW = 15 * 0.6       # info font advance
info_w = 46 * ICW
W = int(info_x + info_w + PAD)
face_h = len(face) * LH
H = int(BAR + PAD + face_h + PAD)
info_top = BAR + PAD + (face_h - len(INFO) * LH * 1.6) / 2

parts = []
# face
for i, line in enumerate(face):
    if not line.strip():
        continue
    y = BAR + PAD + (i + 1) * LH
    parts.append(
        f'<text class="f" x="{PAD}" y="{y:.1f}" style="animation-delay:{i*0.03:.2f}s">'
        f'{escape(line).replace(" ", "&#160;")}</text>'
    )

# info
start = len(face) * 0.03 + 0.2
for j, (kind, val) in enumerate(INFO):
    y = info_top + (j + 1) * LH * 1.6
    d = f"animation-delay:{start + j*0.12:.2f}s"
    if kind == "title":
        parts.append(f'<text class="i t" x="{info_x:.1f}" y="{y:.1f}" style="{d}">{escape(val)}</text>')
    elif kind == "rule":
        parts.append(f'<text class="i r" x="{info_x:.1f}" y="{y:.1f}" style="{d}">{"─"*44}</text>')
    elif kind == "kv":
        k, v = val
        key = f'<tspan class="k">{escape(k + ":") if k else ""}</tspan>'
        parts.append(
            f'<text class="i" x="{info_x:.1f}" y="{y:.1f}" style="{d}">{key}'
            f'<tspan class="v" x="{info_x + 12*ICW:.1f}">{escape(v)}</tspan></text>'
        )
    elif kind == "colors":
        cols = ["#0d1117", "#f87171", "#4ade80", "#facc15", "#38bdf8", "#c084fc", "#22d3ee", "#e5e7eb"]
        g = [f'<g class="i" style="{d}">']
        for n, c in enumerate(cols):
            g.append(f'<rect x="{info_x + n*26:.1f}" y="{y-12:.1f}" width="24" height="14" rx="2" fill="{c}" stroke="#30363d"/>')
        g.append("</g>")
        parts.append("".join(g))

cursor_y = info_top + (len(INFO) + 1) * LH * 1.6
parts.append(f'<rect class="cur" x="{info_x:.1f}" y="{cursor_y-11:.1f}" width="7" height="13" fill="#38bdf8"/>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="fg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#bae6fd"/>
      <stop offset="100%" stop-color="#0ea5e9"/>
    </linearGradient>
  </defs>
  <style>
    text {{ font-family: "Fira Code","JetBrains Mono",Consolas,"Courier New",monospace; font-size:{FS}px; white-space:pre; }}
    .f {{ fill:url(#fg); animation:fade .4s ease-out backwards; }}
    .i {{ animation:fade .4s ease-out backwards; font-size:15px; }}
    .t {{ fill:#7dd3fc; font-weight:700; font-size:17px; }}
    .r {{ fill:#30363d; }}
    .k {{ fill:#38bdf8; font-weight:700; }}
    .v {{ fill:#c9d1d9; }}
    .cur {{ animation:blink 1s steps(1) infinite; }}
    @keyframes fade {{ from {{ opacity:0; }} }}
    @keyframes blink {{ 50% {{ opacity:0; }} }}
  </style>
  <rect width="{W}" height="{H}" rx="12" fill="#0d1117" stroke="#30363d"/>
  <path d="M0 12 a12 12 0 0 1 12 -12 H{W-12} a12 12 0 0 1 12 12 V{BAR} H0 Z" fill="#161b22"/>
  <circle cx="22" cy="{BAR/2}" r="6" fill="#ff5f56"/>
  <circle cx="42" cy="{BAR/2}" r="6" fill="#ffbd2e"/>
  <circle cx="62" cy="{BAR/2}" r="6" fill="#27c93f"/>
  <text x="{W/2}" y="{BAR/2+4}" text-anchor="middle" style="font-size:12px;fill:#8b949e">oussama@github: ~</text>
  {chr(10).join("  " + p for p in parts)}
</svg>
'''
open(out_svg, "w", encoding="utf-8").write(svg)
print(f"{W}x{H}")
