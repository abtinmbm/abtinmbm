"""Generate the profile header banner (dark and light) as SVG.

The bottom strip draws the name as a keystroke timeline: each bar is one key,
x = when it was pressed, width = how long it was held. Timings are illustrative.
"""
import random
import sys

out_dir = sys.argv[1]

THEMES = {
    "dark": dict(bg="#0d1117", fg="#e6edf3", muted="#7d8590", rule="#30363d",
                 accent="#e3b341", bar="#e3b341", bar2="#58a6ff"),
    "light": dict(bg="#ffffff", fg="#1f2328", muted="#656d76", rule="#d0d7de",
                  accent="#9a6700", bar="#bf8700", bar2="#0969da"),
}

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
SERIF = "Georgia, 'Iowan Old Style', 'Times New Roman', serif"

W, H = 1200, 300
PAUSE_MS = 3000   # how long the finished name stays up before replaying
FADE_MS = 300
name = "abtin aryanpour"

rng = random.Random(8)
keys = []
t = 0.0
for ch in name:
    hold = rng.uniform(70, 125) if ch != " " else rng.uniform(95, 140)
    keys.append((ch, t, hold))
    t += rng.uniform(105, 190) if ch != " " else rng.uniform(230, 290)
total = keys[-1][1] + keys[-1][2]

x0, x1 = 64, W - 64
scale = (x1 - x0) / total
base_y = 262


def svg(theme):
    c = THEMES[theme]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Abtin Aryanpour">',
        f'<rect width="{W}" height="{H}" rx="12" fill="{c["bg"]}"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{c["rule"]}"/>',
        f'<text x="64" y="62" font-family="{MONO}" font-size="15" fill="{c["muted"]}">~/abtinmbm $ whoami</text>',
        f'<text x="62" y="128" font-family="{SERIF}" font-size="60" fill="{c["fg"]}">Abtin Aryanpour</text>',
        f'<text x="64" y="166" font-family="{MONO}" font-size="16" fill="{c["muted"]}">computer engineering @ uwaterloo  ·  security <tspan fill="{c["accent"]}">×</tspan> ml  ·  warg autonomy</text>',
        # blinking caret after the prompt (monospace, so its position is predictable)
        f'<rect x="{64 + 19 * 9.03 + 6:.0f}" y="48" width="9" height="18" fill="{c["accent"]}"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/></rect>',
        f'<line x1="{x0}" y1="{base_y}" x2="{x1}" y2="{base_y}" stroke="{c["rule"]}"/>',
    ]
    # Animation: the name is "typed" in real time, held on screen, then replays.
    cycle = total + PAUSE_MS
    dur = f"{cycle / 1000:.2f}s"
    for i, (ch, start, hold) in enumerate(keys):
        x = x0 + start * scale
        w = hold * scale
        h = 26 if ch != " " else 12
        color = c["bar"] if ch != " " else c["bar2"]
        k0 = start / cycle            # key pressed
        k1 = (start + hold) / cycle   # key released
        k_end = 1 - FADE_MS / cycle   # start fading out before the replay
        def fade(peak):
            return (f'<animate attributeName="opacity" dur="{dur}" repeatCount="indefinite" '
                    f'values="0;0;{peak};{peak};0" keyTimes="0;{k0:.4f};{k0 + 0.0005:.4f};{k_end:.4f};1"/>')
        appear = fade("0.9")
        grow = (f'<animate attributeName="width" dur="{dur}" repeatCount="indefinite" '
                f'values="0;0;{w:.1f};{w:.1f}" keyTimes="0;{k0:.4f};{k1:.4f};1"/>')
        parts.append(f'<rect x="{x:.1f}" y="{base_y - h}" width="{w:.1f}" height="{h}" rx="3" fill="{color}" opacity="0.9">{appear}{grow}</rect>')
        label = ch if ch != " " else "␣"
        label_anim = fade("1")
        parts.append(f'<text x="{x + w/2:.1f}" y="{base_y - h - 8}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{c["muted"]}">{label}{label_anim}</text>')
    parts.append(f'<text x="{x1}" y="{base_y + 24}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{c["muted"]}">each bar is a key: press → release</text>')
    parts.append("</svg>")
    return "\n".join(parts)


for theme in THEMES:
    with open(f"{out_dir}/header-{theme}.svg", "w", encoding="utf-8") as f:
        f.write(svg(theme))
print("ok", round(total))
