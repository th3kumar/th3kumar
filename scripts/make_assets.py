"""Static SVG assets for the profile README: project cards, toolbox, footer.

Run: python3 scripts/make_assets.py

Every asset comes in a dark and a light variant (GitHub swaps them via <picture>).
Motion is slow (18-40s loops), eased, and switched off for prefers-reduced-motion.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)

FONT = "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Inter, Roboto, 'Helvetica Neue', Arial, sans-serif"

THEMES = {
    "dark": dict(
        bg="#0d1117", surface="#12171f", stroke="#ffffff", stroke_o=0.07,
        text="#e8eaed", muted="#8b94a3", faint="#5c6573",
        pill="#ffffff", pill_o=0.05,
        sage="#8fb8a6", lav="#a7a3e0", sand="#e3b99a", mist="#8fb3d9",
        orb_o=0.55,
    ),
    "light": dict(
        bg="#ffffff", surface="#f6f7f9", stroke="#0f172a", stroke_o=0.07,
        text="#1f2328", muted="#5f6873", faint="#9aa2ad",
        pill="#0f172a", pill_o=0.045,
        sage="#6f9d89", lav="#8c87d6", sand="#d4a27e", mist="#7ea3cc",
        orb_o=0.38,
    ),
}

BASE_CSS = """
  .t{font-family:%s;}
  @keyframes fadeUp{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
  @keyframes breathe{0%%,100%%{opacity:.35}50%%{opacity:1}}
  @media (prefers-reduced-motion: reduce){*{animation:none!important}}
""" % FONT


def svg(w, h, body, css=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'fill="none" role="img">\n<style>{BASE_CSS}{css}</style>\n{body}\n</svg>\n'
    )


def text_w(s, size, weight=400):
    # rough width estimate for system sans
    w = 0
    for ch in s:
        if ch in " .·,|ilj'": w += 0.3
        elif ch.isupper() or ch in "mwMW": w += 0.68
        elif ch.isdigit(): w += 0.58
        else: w += 0.53
    return w * size * (1.04 if weight >= 600 else 1)


# ---------------------------------------------------------------- hero
def hero(t):
    W, H = 1200, 340
    css = """
  @keyframes d1{0%%,100%%{transform:translate(0,0)}50%%{transform:translate(90px,30px)}}
  @keyframes d2{0%%,100%%{transform:translate(0,0)}50%%{transform:translate(-110px,-25px)}}
  @keyframes d3{0%%,100%%{transform:translate(0,0)}50%%{transform:translate(-60px,40px)}}
  .o1{animation:d1 26s ease-in-out infinite}
  .o2{animation:d2 32s ease-in-out infinite}
  .o3{animation:d3 38s ease-in-out infinite}
  .a1{opacity:0;animation:fadeUp 1.1s cubic-bezier(.22,1,.36,1) .15s forwards}
  .a2{opacity:0;animation:fadeUp 1.1s cubic-bezier(.22,1,.36,1) .35s forwards}
  .a3{opacity:0;animation:fadeUp 1.1s cubic-bezier(.22,1,.36,1) .55s forwards}
  .dot{animation:breathe 4s ease-in-out infinite}
  @media (prefers-reduced-motion: reduce){.a1,.a2,.a3{opacity:1}}
"""
    def orb(id_, color):
        return (f'<radialGradient id="{id_}"><stop offset="0" stop-color="{color}" stop-opacity="{t["orb_o"]}"/>'
                f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')

    body = f"""
<defs>
  <clipPath id="clip"><rect width="{W}" height="{H}" rx="28"/></clipPath>
  {orb("g1", t["sage"])}{orb("g2", t["lav"])}{orb("g3", t["sand"])}
</defs>
<g clip-path="url(#clip)">
  <rect width="{W}" height="{H}" fill="{t["surface"]}"/>
  <g class="o1"><circle cx="830" cy="90" r="260" fill="url(#g1)"/></g>
  <g class="o2"><circle cx="1060" cy="250" r="240" fill="url(#g2)"/></g>
  <g class="o3"><circle cx="700" cy="330" r="200" fill="url(#g3)"/></g>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="27.5" stroke="{t["stroke"]}" stroke-opacity="{t["stroke_o"]}"/>

<g class="t">
  <g class="a1">
    <circle class="dot" cx="78" cy="104" r="4" fill="{t["sage"]}"/>
    <text x="92" y="109" font-size="15" letter-spacing="1.5" fill="{t["muted"]}">HI, I'M</text>
  </g>
  <text class="a2" x="72" y="172" font-size="60" font-weight="600" letter-spacing="-1.5" fill="{t["text"]}">Mantu Kumar</text>
  <g class="a3">
    <text x="74" y="216" font-size="21" fill="{t["muted"]}">Android &amp; web engineer. I build calm, tactile interfaces</text>
    <text x="74" y="244" font-size="21" fill="{t["muted"]}">that feel good to use.</text>
    <text x="74" y="290" font-size="14" letter-spacing=".4" fill="{t["faint"]}">SOFTWARE ENGINEER @ VAHAN   ·   FOUNDER, ANATOMYGO   ·   INDIA</text>
  </g>
</g>
"""
    return svg(W, H, body, css)


# ---------------------------------------------------------------- project card
def card(t, title, lines, tags, status, accent_key, live=False, breathe=False):
    W, H = 580, 236
    a = t[accent_key]
    css = """
  @keyframes drift{0%,100%{transform:translate(0,0)}50%{transform:translate(-26px,14px)}}
  .orb{animation:drift 24s ease-in-out infinite}
  .dot{animation:breathe 3.6s ease-in-out infinite}
  @keyframes br{0%,100%{transform:scale(.8)}50%{transform:scale(1.12)}}
  .br{transform-box:fill-box;transform-origin:center;animation:br 10s ease-in-out infinite}
"""
    desc = "".join(
        f'<text x="32" y="{106 + i*24}" font-size="16" fill="{t["muted"]}">{escape(l)}</text>' for i, l in enumerate(lines)
    )
    # tags
    x = 32
    pills = []
    for tag in tags:
        w = text_w(tag, 13) + 24
        pills.append(
            f'<rect x="{x:.1f}" y="180" width="{w:.1f}" height="28" rx="14" fill="{t["pill"]}" fill-opacity="{t["pill_o"]}"/>'
            f'<text x="{x + w/2:.1f}" y="198.5" font-size="13" text-anchor="middle" fill="{t["muted"]}">{escape(tag)}</text>'
        )
        x += w + 8
    sw = text_w(status, 12.5) + 38
    sx = W - 28 - sw
    dot_cls = ' class="dot"' if live else ""
    bx, by = W - 92, 150
    breath = (f'<circle class="br" cx="{bx}" cy="{by}" r="62" fill="url(#g)"/>'
              f'<circle class="br" cx="{bx}" cy="{by}" r="44" fill="url(#g)"/>'
              f'<circle cx="{bx}" cy="{by}" r="24" fill="{t["surface"]}" stroke="{t["stroke"]}" stroke-opacity=".1"/>'
              f'<path d="M{bx-6} {by-9} L{bx+10} {by} L{bx-6} {by+9} Z" fill="{t["text"]}" fill-opacity=".8"/>') if breathe else ""
    body = f"""
<defs>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  <radialGradient id="g"><stop offset="0" stop-color="{a}" stop-opacity="{t["orb_o"]*0.75}"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>
</defs>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="{t["surface"]}"/>
  {"" if breathe else f'<g class="orb"><circle cx="{W-40}" cy="-10" r="190" fill="url(#g)"/></g>'}
</g>
{breath}
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="21.5" stroke="{t["stroke"]}" stroke-opacity="{t["stroke_o"]}"/>
<g class="t">
  <text x="32" y="72" font-size="26" font-weight="600" letter-spacing="-.4" fill="{t["text"]}">{escape(title)}</text>
  <rect x="{sx:.1f}" y="28" width="{sw:.1f}" height="28" rx="14" fill="{t["pill"]}" fill-opacity="{t["pill_o"]}"/>
  <circle{dot_cls} cx="{sx+16:.1f}" cy="42" r="3.5" fill="{a}"/>
  <text x="{sx+26:.1f}" y="46.5" font-size="12.5" fill="{t["muted"]}">{escape(status)}</text>
  {desc}
  {''.join(pills)}
</g>
"""
    return svg(W, H, body, css)


CARDS = {
    "anatomygo": dict(title="AnatomyGo", lines=["Interactive 3D anatomy you can rotate, explode", "and explore, pin by pin. Web + Android."],
                      tags=["TypeScript", "3D", "Android"], status="live · anatomygo.in", accent_key="sage", live=True),
    "cineverse": dict(title="CINEVERSE", lines=["An AI movie concierge that learns your vibe", "from a few swipes, then finds the film."],
                      tags=["Next.js", "TypeScript", "Groq"], status="proof of concept", accent_key="lav"),
    "tiernight": dict(title="Tier Night", lines=["A party tier-list game for Friday nights.", "Submit, vote, argue, rank."],
                      tags=["Next.js", "Supabase"], status="side project", accent_key="sand"),
    "snoozz": dict(title="Snoozz", lines=["A white-noise sleep buddy for Android.", "Tap to breathe along in your browser."],
                   tags=["Kotlin", "ExoPlayer", "Web Audio"], status="tap to listen", accent_key="mist", live=True, breathe=True),
}


# ---------------------------------------------------------------- toolbox
def toolbox(t):
    W = 1200
    rows = [
        ("Android", "sage", ["Kotlin", "Jetpack Compose", "Coroutines", "MVVM", "Retrofit", "ExoPlayer"]),
        ("Web", "lav", ["React", "Next.js", "TypeScript", "Supabase", "React Native"]),
        ("Craft", "sand", ["Figma", "Motion design", "Design systems", "Analytics instrumentation"]),
    ]
    H = 40 + len(rows) * 52
    parts = []
    for i, (label, key, items) in enumerate(rows):
        y = 34 + i * 52
        parts.append(f'<circle cx="40" cy="{y+14}" r="5" fill="{t[key]}"/>')
        parts.append(f'<text x="56" y="{y+19}" font-size="15" font-weight="600" fill="{t["text"]}">{label}</text>')
        x = 170
        for it in items:
            w = text_w(it, 14) + 30
            parts.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="30" rx="15" fill="{t["pill"]}" fill-opacity="{t["pill_o"]}"/>')
            parts.append(f'<text x="{x+w/2:.1f}" y="{y+19.5}" font-size="14" text-anchor="middle" fill="{t["muted"]}">{escape(it)}</text>')
            x += w + 10
    body = f"""
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="22" fill="{t["surface"]}" stroke="{t["stroke"]}" stroke-opacity="{t["stroke_o"]}"/>
<g class="t">{''.join(parts)}</g>
"""
    return svg(W, H, body)


# ---------------------------------------------------------------- footer
def footer(t):
    W, H = 1200, 120
    css = """
  @keyframes slide{from{transform:translateX(0)}to{transform:translateX(-600px)}}
  .w1{animation:slide 40s linear infinite}
  .w2{animation:slide 56s linear infinite}
"""
    def wave(y, amp):
        # 600px period, drawn across 1800px so it can slide seamlessly
        d = f"M0 {y}"
        for k in range(6):
            x0 = k * 300
            sgn = -1 if k % 2 == 0 else 1
            d += f" Q{x0+150} {y + sgn*amp} {x0+300} {y}"
        return d
    body = f"""
<defs>
  <linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{t["bg"]}" stop-opacity="1"/><stop offset=".18" stop-color="{t["bg"]}" stop-opacity="0"/><stop offset=".82" stop-color="{t["bg"]}" stop-opacity="0"/><stop offset="1" stop-color="{t["bg"]}" stop-opacity="1"/></linearGradient>
</defs>
<g class="w1"><path d="{wave(46, 10)}" stroke="{t["sage"]}" stroke-opacity=".55" stroke-width="1.5"/></g>
<g class="w2"><path d="{wave(54, 14)}" stroke="{t["lav"]}" stroke-opacity=".4" stroke-width="1.5"/></g>
<rect width="{W}" height="80" fill="url(#fade)"/>
<text class="t" x="{W/2}" y="108" font-size="14" text-anchor="middle" letter-spacing=".4" fill="{t["faint"]}">Thanks for stopping by. Take a slow breath before the next tab.</text>
"""
    return svg(W, H, body, css)


for name, t in THEMES.items():
    (OUT / f"toolbox-{name}.svg").write_text(toolbox(t))
    (OUT / f"footer-{name}.svg").write_text(footer(t))
    for slug, c in CARDS.items():
        (OUT / f"card-{slug}-{name}.svg").write_text(card(t, **c))

print(sorted(p.name for p in OUT.iterdir()))
