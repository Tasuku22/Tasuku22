import os
import math
import requests
from collections import Counter

# =========================
# GitHub API settings
# =========================
GITHUB_API = "https://api.github.com"
TOKEN = os.getenv("GH_TOKEN")

if not TOKEN:
    raise RuntimeError("GITHUB_TOKEN is not set")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
}

# =========================
# Language colors (official image colors)
# =========================
LANG_COLORS = {
    "Python": "#3776AB",
    "C": "#555555",
    "C++": "#00599C",
    "C#": "#512BD4",
    "Java": "#B07219",
    "JavaScript": "#F7DF1E",
    "TypeScript": "#3178C6",
    "Go": "#00ADD8",
    "Rust": "#DEA584",
    "Shell": "#89E051",
    "HTML": "#E34F26",
    "CSS": "#1572B6",
    "PHP": "#777BB4",
    "Ruby": "#CC342D",
    "Swift": "#F05138",
    "Kotlin": "#A97BFF",
    "Jupyter Notebook": "#FF914D",
    "R": "#198CE7",
    "MATLAB": "#E16737",
    "Dockerfile": "#2496ED",
    "Makefile": "#427819",
    "TeX": "#53ae53",
    "Other": "#9CA3AF",
}

# =========================
# SVG layout
# =========================
WIDTH = 520
HEIGHT = 220
CX = 110
CY = 110
R = 80

# =========================
# GitHub API functions
# =========================
def get_repositories():
    repos = []
    page = 1
    while True:
        url = f"{GITHUB_API}/user/repos?per_page=100&page={page}"
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos


def collect_languages(repos):
    counter = Counter()
    for repo in repos:
        if repo["fork"]:
            continue
        r = requests.get(repo["languages_url"], headers=HEADERS)
        r.raise_for_status()
        counter.update(r.json())
    return counter


def top5_with_other(counter):
    items = counter.most_common()
    total = sum(counter.values())
    top5 = items[:5]
    other = sum(v for _, v in items[5:])
    result = top5.copy()
    if other > 0:
        result.append(("Other", other))
    return result, total

# =========================
# SVG helpers
# =========================
def polar(cx, cy, r, angle):
    return cx + r * math.cos(angle), cy + r * math.sin(angle)


def arc_path(cx, cy, r, start, end):
    x1, y1 = polar(cx, cy, r, start)
    x2, y2 = polar(cx, cy, r, end)
    large = 1 if end - start > math.pi else 0
    return f"M {cx},{cy} L {x1:.2f},{y1:.2f} A {r},{r} 0 {large},1 {x2:.2f},{y2:.2f} Z"

# =========================
# SVG generation
# =========================
def generate_svg(data, total):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
  width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<style>
.label, .value {{
  font-family: "Noto Sans", "Noto Sans JP",
               -apple-system, BlinkMacSystemFont,
               "Segoe UI", Helvetica, Arial, sans-serif;
  fill: #374151;
}}

.label {{
  font-size: 14px;
}}

.value {{
  font-size: 13px;
}}

/* Dark mode */
@media (prefers-color-scheme: dark) {{
  .label, .value {{
    fill: #E5E7EB;
  }}
}}

</style>
'''

    angle = -math.pi / 2
    for lang, size in data:
        frac = size / total
        end = angle + frac * 2 * math.pi
        color = LANG_COLORS.get(lang, LANG_COLORS["Other"])
        svg += f'<path d="{arc_path(CX, CY, R, angle, end)}" fill="{color}"/>'
        angle = end

    y = 45
    for lang, size in data:
        pct = size / total * 100
        color = LANG_COLORS.get(lang, LANG_COLORS["Other"])
        svg += f'<rect x="230" y="{y-10}" width="12" height="12" fill="{color}"/>'
        svg += f'<text x="250" y="{y}" class="label">{lang}</text>'
        svg += f'<text x="460" y="{y}" class="value">{pct:.1f}%</text>'
        y += 26

    svg += "</svg>"
    return svg

# =========================
# Main
# =========================
def main():
    repos = get_repositories()
    counter = collect_languages(repos)
    data, total = top5_with_other(counter)
    svg = generate_svg(data, total)

    with open("languages.svg", "w", encoding="utf-8") as f:
        f.write(svg)

    print("languages.svg generated")

if __name__ == "__main__":
    main()
