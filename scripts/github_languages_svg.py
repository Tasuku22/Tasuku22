# This script was created with assistance from generative AI (ChatGPT / OpenAI GPT-5.2).
# 本スクリプトは、生成AI（ChatGPT / OpenAI GPT-5.2）の支援を受けて作成されています。
# The final design and validation were performed by the repository author.
# 最終的な設計および検証は、リポジトリの作成者が行っています。

import os
import math
import requests
from collections import Counter
from typing import Dict, Tuple

# =========================
# GitHub API settings
# =========================
GITHUB_API = "https://api.github.com"
TOKEN = os.getenv("GH_TOKEN")

if not TOKEN:
    raise RuntimeError("GH_TOKEN is not set")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
}

# =========================
# Language classification
# =========================
PROGRAMMING_LANGUAGES = {
    "Python", "JavaScript", "TypeScript", "Ruby", "PHP", "Perl", "Lua",
    "C", "C++", "C#", "Java", "Go", "Rust", "Swift", "Kotlin",
    "Haskell", "OCaml", "F#", "Elixir", "Erlang",
    "MATLAB", "Julia", "Fortran", "R",
    "Scala", "Groovy",
    "Shell", "Bash", "PowerShell",
    "Dart", "Objective-C", "Assembly", "WebAssembly",
    "SQL",
}

MARKUP_LANGUAGES = {
    "HTML", "CSS", "SCSS", "Sass", "Less",
    "Markdown", "reStructuredText", "AsciiDoc",
    "YAML", "JSON", "TOML", "INI", "XML",
    "Dockerfile", "Makefile",
    "TeX", "LaTeX",
    "SVG",
}

# =========================
# Colors (per language)
# =========================
# =========================
# Language colors
# (based on official icons / GitHub Linguist / Simple Icons)
# =========================
LANG_COLORS = {
    # --- Programming Languages ---
    "Python": "#3776AB",
    "JavaScript": "#F7DF1E",
    "TypeScript": "#3178C6",
    "C": "#555555",
    "C++": "#00599C",
    "C#": "#512BD4",
    "Java": "#B07219",
    "Go": "#00ADD8",
    "Rust": "#DEA584",
    "Ruby": "#CC342D",
    "PHP": "#777BB4",
    "Swift": "#F05138",
    "Kotlin": "#A97BFF",
    "Dart": "#0175C2",
    "Scala": "#DC322F",
    "Groovy": "#4298B8",
    "Objective-C": "#438EFF",
    "Assembly": "#6E4C13",
    "WebAssembly": "#654FF0",

    # Functional / Scientific
    "Haskell": "#5E5086",
    "OCaml": "#EC6813",
    "F#": "#378BBA",
    "Elixir": "#4B275F",
    "Erlang": "#A90533",
    "Julia": "#9558B2",
    "MATLAB": "#E16737",
    "Fortran": "#734F96",
    "R": "#198CE7",

    # Shell / Script
    "Shell": "#89E051",
    "Bash": "#4EAA25",
    "PowerShell": "#5391FE",

    # Data / DB
    "SQL": "#003B57",

    # --- Markup / Config Languages ---
    "HTML": "#E34F26",
    "CSS": "#1572B6",
    "SCSS": "#CC6699",
    "Sass": "#CC6699",
    "Less": "#1D365D",

    "Markdown": "#083FA1",
    "reStructuredText": "#141414",
    "AsciiDoc": "#73A0C5",

    "JSON": "#292929",
    "YAML": "#CB171E",
    "TOML": "#9C4121",
    "INI": "#6B7280",
    "XML": "#0060AC",

    "Dockerfile": "#2496ED",
    "Makefile": "#427819",

    "TeX": "#3D6117",
    "LaTeX": "#008080",
    "SVG": "#FFB13B",

    # --- Fallback ---
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


def split_by_category(counter: Counter) -> Tuple[Counter, Counter]:
    prog = Counter()
    markup = Counter()

    for lang, size in counter.items():
        if lang in PROGRAMMING_LANGUAGES:
            prog[lang] += size
        elif lang in MARKUP_LANGUAGES:
            markup[lang] += size

    return prog, markup


def top_with_other(counter: Counter, top_n: int = 5):
    items = counter.most_common()
    total = sum(counter.values())
    top = items[:top_n]
    other = sum(v for _, v in items[top_n:])
    if other > 0:
        top.append(("Other", other))
    return top, total

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
def generate_svg(title: str, data, total):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
  width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<style>
.label, .value, .title {{
  font-family: -apple-system, BlinkMacSystemFont,
               "Segoe UI", Helvetica, Arial, sans-serif;
  fill: #374151;
}}
.title {{ font-size: 16px; font-weight: 600; }}
.label {{ font-size: 14px; }}
.value {{ font-size: 13px; }}

@media (prefers-color-scheme: dark) {{
  .label, .value, .title {{ fill: #E5E7EB; }}
}}
</style>

<text x="20" y="24" class="title">{title}</text>
'''

    angle = -math.pi / 2
    for lang, size in data:
        frac = size / total if total > 0 else 0
        end = angle + frac * 2 * math.pi
        color = LANG_COLORS.get(lang, LANG_COLORS["Other"])
        svg += f'<path d="{arc_path(CX, CY, R, angle, end)}" fill="{color}"/>'
        angle = end

    y = 50
    for lang, size in data:
        pct = size / total * 100 if total > 0 else 0
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

    prog, markup = split_by_category(counter)

    prog_data, prog_total = top_with_other(prog)
    markup_data, markup_total = top_with_other(markup)

    prog_svg = generate_svg(
        "Programming Languages (Composition)",
        prog_data,
        prog_total,
    )

    markup_svg = generate_svg(
        "Markup / Config Languages (Composition)",
        markup_data,
        markup_total,
    )

    with open("languages_programming.svg", "w", encoding="utf-8") as f:
        f.write(prog_svg)

    with open("languages_markup.svg", "w", encoding="utf-8") as f:
        f.write(markup_svg)

    print("languages_programming.svg generated")
    print("languages_markup.svg generated")


if __name__ == "__main__":
    main()
