"""Time-of-day header for the profile README.

Picks the sky for the current time in India (dawn, day, dusk or night) and writes
two files, hero-light.svg and hero-dark.svg, so GitHub's light and dark themes each
get their own version of the same sky. It also reads the latest commit on
th3kumar/anatomygo-site for the "Last shipped" pill.

Run: python3 scripts/sky.py [out_dir] [--period dawn|day|dusk|night] [--all]
A GitHub Action runs it every hour and publishes the result to the `output` branch.
"""
import json, os, random, re, sys, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape

IST = timezone(timedelta(hours=5, minutes=30))
SHIP_REPO = "th3kumar/anatomygo-site"
FONT = "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Inter, Roboto, 'Helvetica Neue', Arial, sans-serif"
ROLE = "SOFTWARE ENGINEER II @ VAHAN   ·   FOUNDER, ANATOMYGO"
TAGLINE = "Android &amp; web engineer. I build calm, tactile interfaces."

LINES = {
    "dawn": "Early morning in India  ·  first chai, then code",
    "day": "Daytime in India  ·  somewhere inside a Compose screen",
    "dusk": "Evening in India  ·  switching to AnatomyGo mode",
    "night": "Late night in India  ·  probably shipping AnatomyGo",
}

# Each sky has a light and a dark version. Orbs: three soft colour fields.
SKIES = {
    ("dawn", "light"): dict(bg=("#fbeadf", "#f2e1ec"), o=("#f4b192", "#e8a2b8", "#f2cf8a"), op=.6,
                            text="#2a2230", muted="#6d5d6a", faint="#9a8a96", ink="#2a2230", inkop=.06, accent="#d98c6a", body="sun_low"),
    ("dawn", "dark"):  dict(bg=("#1c1519", "#241a24"), o=("#c97f68", "#b86f8a", "#c9a25e"), op=.42,
                            text="#f3e9ec", muted="#bba9b2", faint="#857480", ink="#ffffff", inkop=.07, accent="#e8a58c", body="sun_low_dim"),
    ("day", "light"):  dict(bg=("#f3f8fc", "#eef4f1"), o=("#9cc6e8", "#a7d0bd", "#f4d98f"), op=.55,
                            text="#1f2328", muted="#5b6572", faint="#98a1ac", ink="#0f172a", inkop=.05, accent="#5f9c86", body="sun_high"),
    ("day", "dark"):   dict(bg=("#0f1620", "#101c1d"), o=("#4f83b0", "#4f8f78", "#b59a55"), op=.42,
                            text="#e6edf3", muted="#9aa7b4", faint="#5f6b78", ink="#ffffff", inkop=.07, accent="#8fb8a6", body="sun_high_dim"),
    ("dusk", "light"): dict(bg=("#f4eef8", "#fbece6"), o=("#b3a6ec", "#f0b29a", "#d39ac4"), op=.55,
                            text="#2a2438", muted="#6a6079", faint="#a197ad", ink="#2a2438", inkop=.06, accent="#c98a72", body="sun_set"),
    ("dusk", "dark"):  dict(bg=("#2b2540", "#3a2b45"), o=("#9b8ae0", "#e5a088", "#b47aa6"), op=.55,
                            text="#f4eef7", muted="#c4b8d0", faint="#8f83a0", ink="#ffffff", inkop=.08, accent="#e8a58c", body="sun_set_dim"),
    ("night", "light"): dict(bg=("#eef1f8", "#e8edf6"), o=("#8ea2dc", "#86c0bb", "#a99de0"), op=.45,
                             text="#1d2333", muted="#5c6479", faint="#9aa1b4", ink="#1d2333", inkop=.06, accent="#6f8fc4", body="moon_light"),
    ("night", "dark"):  dict(bg=("#0a0f1e", "#111730"), o=("#3a58a8", "#2f8580", "#6656b8"), op=.5,
                             text="#e7eaf3", muted="#949db3", faint="#5f6880", ink="#ffffff", inkop=.07, accent="#8fb3d9", body="moon_dark"),
}


def period_for(now):
    h = now.hour + now.minute / 60
    if 5 <= h < 8:
        return "dawn"
    if 8 <= h < 17:
        return "day"
    if 17 <= h < 20:
        return "dusk"
    return "night"


def text_w(s, size):
    w = 0
    for ch in s:
        if ch in " .·,|ilj'":
            w += 0.3
        elif ch.isupper() or ch in "mwMW":
            w += 0.68
        elif ch.isdigit():
            w += 0.58
        else:
            w += 0.53
    return w * size


def last_shipped(now):
    """'Last shipped · <commit subject> · 3 days ago', or None if it can't be read."""
    req = urllib.request.Request(f"https://api.github.com/repos/{SHIP_REPO}/commits?per_page=1",
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "th3kumar-sky"})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            c = json.load(r)[0]["commit"]
    except Exception as e:  # network, rate limit, empty repo
        print("last_shipped: skipped:", e, file=sys.stderr)
        return None
    subject = c["message"].splitlines()[0].strip()
    subject = re.sub(r"^\w+(\([^)]*\))?!?:\s*", "", subject)        # drop "feat(x):" style prefixes
    subject = re.sub(r"\s*\(#\d+\)$", "", subject)                   # drop "(#12)"
    if not subject or subject.lower().startswith(("merge ", "wip", "update readme")):
        subject = "a new update"
    subject = subject[0].lower() + subject[1:] if subject[:2] != subject[:2].upper() else subject
    if len(subject) > 34:
        subject = subject[:33].rstrip() + "…"
    when = datetime.fromisoformat(c["committer"]["date"].replace("Z", "+00:00")).astimezone(IST)
    days = (now.date() - when.date()).days
    ago = "today" if days <= 0 else "yesterday" if days == 1 else f"{days} days ago"
    return f"Last shipped  ·  {subject}  ·  {ago}"


def celestial(kind, s):
    if kind.startswith("sun"):
        y = {"sun_low": 252, "sun_low_dim": 252, "sun_high": 126, "sun_high_dim": 126, "sun_set": 286, "sun_set_dim": 286}[kind]
        fill, op = ("#fff6dc", .92) if not kind.endswith("dim") else (("#f2b38f", .7) if kind.startswith("sun_low") else ("#f5d08a", .72))
        if kind.startswith("sun_set"):
            fill, op = ("#ffd9b8", .8) if kind == "sun_set" else ("#f3b48f", .6)
        return f'<circle cx="1040" cy="{y}" r="34" fill="{fill}" fill-opacity="{op}"/>'
    rnd = random.Random(7)
    star = "#ffffff" if kind == "moon_dark" else "#5c6a90"
    star_op = 1 if kind == "moon_dark" else .45
    out = ""
    for _ in range(38):
        x, y = rnd.uniform(560, 1180), rnd.uniform(16, 320)
        out += (f'<circle class="st" style="animation-delay:-{rnd.uniform(0, 5):.1f}s" cx="{x:.0f}" cy="{y:.0f}" '
                f'r="{rnd.choice([.8, 1, 1.3])}" fill="{star}" fill-opacity="{star_op}"/>')
    moon = "#e9ecf5" if kind == "moon_dark" else "#b9c5e3"
    out += ('<mask id="moon"><circle cx="1050" cy="132" r="26" fill="#fff"/><circle cx="1062" cy="124" r="24" fill="#000"/></mask>'
            f'<circle cx="1050" cy="132" r="26" fill="{moon}" fill-opacity=".95" mask="url(#moon)"/>')
    return out


def hero(period, theme, ship):
    s = SKIES[(period, theme)]
    W, H = 1200, 340
    ease = "cubic-bezier(.22,1,.36,1)"

    def orb(i, c):
        return (f'<radialGradient id="g{i}"><stop offset="0" stop-color="{c}" stop-opacity="{s["op"]}"/>'
                f'<stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>')

    line = LINES[period]
    lw = text_w(line, 13) + 44
    ship_svg = ""
    if ship:
        sw = text_w(ship, 13) + 30
        sx = W - 40 - sw
        ship_svg = (f'<rect x="{sx:.0f}" y="40" width="{sw:.0f}" height="30" rx="15" fill="{s["ink"]}" fill-opacity="{s["inkop"]}"/>'
                    f'<text x="{sx + 15:.0f}" y="59.5" font-size="13" fill="{s["muted"]}">{escape(ship)}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" role="img">
<title>Mantu Kumar. Android and web engineer. {escape(line)}</title>
<style>
  .t{{font-family:{FONT}}}
  @keyframes d1{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(90px,30px)}}}}
  @keyframes d2{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(-110px,-25px)}}}}
  @keyframes d3{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(-60px,40px)}}}}
  .o1{{animation:d1 26s ease-in-out infinite}}.o2{{animation:d2 32s ease-in-out infinite}}.o3{{animation:d3 38s ease-in-out infinite}}
  @keyframes en{{0%,42%{{opacity:1}}50%,92%{{opacity:0}}100%{{opacity:1}}}}
  @keyframes hi{{0%,42%{{opacity:0}}50%,92%{{opacity:1}}100%{{opacity:0}}}}
  .en{{animation:en 10s ease-in-out infinite}}.hi{{opacity:0;animation:hi 10s ease-in-out infinite}}
  @keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.8}}}}
  .st{{animation:tw 5s ease-in-out infinite}}
  @keyframes breathe{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}
  .dot{{animation:breathe 3.6s ease-in-out infinite}}
  @keyframes fadeUp{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
  .a{{opacity:0;animation:fadeUp 1.1s {ease} .2s forwards}}
  @media (prefers-reduced-motion: reduce){{*{{animation:none!important}}.a,.en{{opacity:1}}.hi{{display:none}}}}
</style>
<defs>
  <clipPath id="clip"><rect width="{W}" height="{H}" rx="28"/></clipPath>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{s["bg"][0]}"/><stop offset="1" stop-color="{s["bg"][1]}"/></linearGradient>
  {orb(1, s["o"][0])}{orb(2, s["o"][1])}{orb(3, s["o"][2])}
</defs>
<g clip-path="url(#clip)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <g class="o1"><circle cx="830" cy="90" r="260" fill="url(#g1)"/></g>
  <g class="o2"><circle cx="1060" cy="250" r="240" fill="url(#g2)"/></g>
  <g class="o3"><circle cx="700" cy="330" r="200" fill="url(#g3)"/></g>
  {celestial(s["body"], s)}
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="27.5" stroke="{s["ink"]}" stroke-opacity=".08"/>
<g class="t a">
  <rect x="72" y="40" width="{lw:.0f}" height="30" rx="15" fill="{s["ink"]}" fill-opacity="{s["inkop"]}"/>
  <circle class="dot" cx="90" cy="55" r="4" fill="{s["accent"]}"/>
  <text x="102" y="59.5" font-size="13" fill="{s["muted"]}">{escape(line)}</text>
  <text class="en" x="74" y="118" font-size="15" letter-spacing="1.5" fill="{s["muted"]}">HI, I'M</text>
  <text class="hi" x="74" y="118" font-size="17" fill="{s["muted"]}">नमस्ते, मैं</text>
  <text x="72" y="180" font-size="60" font-weight="600" letter-spacing="-1.5" fill="{s["text"]}">Mantu Kumar</text>
  <text x="74" y="222" font-size="21" fill="{s["muted"]}">{TAGLINE}</text>
  <text x="74" y="288" font-size="13.5" letter-spacing=".4" fill="{s["faint"]}">{ROLE}</text>
  {ship_svg}
</g>
</svg>
'''


def main():
    args = sys.argv[1:]
    out = Path(next((a for a in args if not a.startswith("--") and a not in SKIES_PERIODS), "dist"))
    out.mkdir(parents=True, exist_ok=True)
    now = datetime.now(IST)
    ship = last_shipped(now)
    forced = args[args.index("--period") + 1] if "--period" in args else None
    periods = SKIES_PERIODS if "--all" in args else [forced or period_for(now)]
    for p in periods:
        suffix = "" if len(periods) == 1 else f"-{p}"
        for theme in ("light", "dark"):
            (out / f"hero{suffix}-{theme}.svg").write_text(hero(p, theme, ship))
    print(f"{now:%Y-%m-%d %H:%M} IST -> {', '.join(periods)}; ship: {ship}")


SKIES_PERIODS = ["dawn", "day", "dusk", "night"]

if __name__ == "__main__":
    main()
