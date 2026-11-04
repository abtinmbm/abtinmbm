"""Generate the profile header banner (dark and light) as SVG.

A night sky: twinkling stars, a crescent moon, a shooting star every few
seconds and layered mountain ridges. The light version is the same scene at dusk.
Everything is seeded, so rerunning gives the same picture.

    python make_banner.py assets
"""
import math
import random
import sys

W, H = 1200, 300
SANS = "'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "dark": dict(
        sky=("#05070f", "#0b1330", "#1a1f4a"),
        star="#ffffff", glow="#9fb4ff", moon="#f4f1e1",
        ridges=("#1c2350", "#121738", "#080b1f"),
        fg="#f0f3ff", muted="#9aa6d6", star_peak=1.0,
    ),
    "light": dict(
        sky=("#2b2d6e", "#7a5aa6", "#f2a36b"),
        star="#ffffff", glow="#ffe2c4", moon="#fff6e0",
        ridges=("#5b4a8a", "#3b2f66", "#1f1a40"),
        fg="#ffffff", muted="#ffe7d6", star_peak=0.85,
    ),
}


def ridge(rng, base, rough, height, steps=7):
    """Midpoint displacement: a natural-looking skyline across the full width."""
    pts = [base + rng.uniform(-height, height) * 0.3, base + rng.uniform(-height, height) * 0.3]
    amp = height
    for _ in range(steps):
        new = []
        for a, b in zip(pts, pts[1:]):
            new += [a, (a + b) / 2 + rng.uniform(-amp, amp)]
        pts = new + [pts[-1]]
        amp *= rough
    dx = W / (len(pts) - 1)
    line = " ".join(f"L{i * dx:.1f},{y:.1f}" for i, y in enumerate(pts))
    return f"M0,{H} {line} L{W},{H} Z"


def sparkle(cx, cy, r):
    """Four-pointed star for the few bright stars."""
    k = r * 0.22
    return (f"M{cx},{cy - r} Q{cx + k},{cy - k} {cx + r},{cy} Q{cx + k},{cy + k} {cx},{cy + r} "
            f"Q{cx - k},{cy + k} {cx - r},{cy} Q{cx - k},{cy - k} {cx},{cy - r} Z")


def svg(theme):
    c = THEMES[theme]
    rng = random.Random(2027)
    top, mid, bot = c["sky"]
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Abtin Aryanpour">',
        "<defs>",
        f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/>'
        f'<stop offset="0.6" stop-color="{mid}"/><stop offset="1" stop-color="{bot}"/></linearGradient>',
        f'<radialGradient id="moonglow"><stop offset="0" stop-color="{c["glow"]}" stop-opacity="0.35"/>'
        f'<stop offset="1" stop-color="{c["glow"]}" stop-opacity="0"/></radialGradient>',
        f'<linearGradient id="trail" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c["star"]}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{c["star"]}" stop-opacity="1"/></linearGradient>',
        f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="12"/></clipPath>',
        "</defs>",
        '<g clip-path="url(#frame)">',
        f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
    ]

    # Moon: a crescent cut out of a disc, with a soft glow behind it.
    mx, my = 1040, 78
    p.append(f'<circle cx="{mx}" cy="{my}" r="90" fill="url(#moonglow)"/>')
    p.append(f'<mask id="crescent"><rect width="{W}" height="{H}" fill="white"/>'
             f'<circle cx="{mx + 13}" cy="{my - 8}" r="25" fill="black"/></mask>')
    p.append(f'<circle cx="{mx}" cy="{my}" r="28" fill="{c["moon"]}" mask="url(#crescent)"/>')

    # Stars, denser toward the top; each twinkles on its own period so they never sync.
    for _ in range(170):
        x = rng.uniform(0, W)
        y = rng.uniform(0, H * 0.8) ** 1.15 / (H * 0.8) ** 0.15
        if math.hypot(x - mx, y - my) < 40:
            continue
        r = rng.choice([0.6, 0.8, 0.8, 1.0, 1.0, 1.3, 1.6])
        lo = rng.uniform(0.15, 0.5) * c["star_peak"]
        hi = rng.uniform(0.7, 1.0) * c["star_peak"]
        dur = rng.uniform(2.5, 7.0)
        begin = rng.uniform(0, dur)
        p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{c["star"]}" opacity="{hi:.2f}">'
                 f'<animate attributeName="opacity" values="{hi:.2f};{lo:.2f};{hi:.2f}" dur="{dur:.1f}s" '
                 f'begin="-{begin:.1f}s" repeatCount="indefinite"/></circle>')
    for x, y, r in [(150, 45, 6), (470, 32, 5), (700, 96, 4.5), (905, 150, 5.5), (330, 200, 4), (1160, 190, 4)]:
        dur = rng.uniform(3, 5)
        p.append(f'<path d="{sparkle(x, y, r)}" fill="{c["star"]}">'
                 f'<animate attributeName="opacity" values="1;0.25;1" dur="{dur:.1f}s" repeatCount="indefinite"/></path>')

    # Shooting star: visible for the first ~0.9 s of an 8 s cycle, then waits.
    p.append('<g opacity="0">'
             '<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.02;0.08;0.11;1" dur="8s" begin="1.5s" repeatCount="indefinite"/>'
             '<animateTransform attributeName="transform" type="translate" values="0,0;340,120;340,120" keyTimes="0;0.11;1" dur="8s" begin="1.5s" repeatCount="indefinite"/>'
             f'<g transform="translate(560,20) rotate(19.4)"><rect x="-130" y="-1" width="130" height="2" rx="1" fill="url(#trail)"/>'
             f'<circle cx="0" cy="0" r="2" fill="{c["star"]}"/></g></g>')

    # Mountains, back to front.
    for fill, base, rough, height, steps in zip(c["ridges"], (225, 252, 280), (0.62, 0.58, 0.55), (95, 70, 38), (7, 7, 8)):
        p.append(f'<path d="{ridge(rng, base, rough, height, steps)}" fill="{fill}"/>')

    p += [
        f'<text x="64" y="112" font-family="{SANS}" font-size="58" font-weight="600" letter-spacing="1" fill="{c["fg"]}">Abtin Aryanpour</text>',
        f'<text x="67" y="148" font-family="{MONO}" font-size="16" letter-spacing="1" fill="{c["muted"]}">computer engineering · university of waterloo</text>',
        "</g>",
        "</svg>",
    ]
    return "\n".join(p)


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    for theme in THEMES:
        with open(f"{out_dir}/header-{theme}.svg", "w", encoding="utf-8") as f:
            f.write(svg(theme))
    print("ok")
