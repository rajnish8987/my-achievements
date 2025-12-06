#!/usr/bin/env python3
"""
Generate `README.md` from `achievements.json` with:

- numbered index (TOC) linking to each achievement
- entries sorted by date (newest first)
- back-to-index links for easy navigation
- repository documentation appended at the end

Usage:
  python scripts/generate_readme.py
"""

import json
import datetime
import os
import sys
from typing import List, Dict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JSON_PATH = os.path.join(ROOT, "achievements.json")
OUT_PATH = os.path.join(ROOT, "README.md")


def parse_date(s: str):
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except Exception:
            continue
    return None

def format_date(s: str) -> str:
    d = parse_date(s)
    return d.strftime("%B %d, %Y") if d else s


def make_md(entries: List[Dict]) -> str:
    top = (
        "# My Achievements\n\n"
        "This README is generated from `achievements.json`.\n\n"
        "Run `python scripts/generate_readme.py` after you add images to `images/` and entries to `achievements.json`.\n\n"
        "---\n\n"
    )

    # Index / Table of contents
    index_lines = ["## Index\n\n", "- [All achievements](#achievements-gallery)\n"]
    for i, e in enumerate(entries, start=1):
        title = e.get("title", "Untitled")
        item = f"- [{i}. {title}](#ach-{i})\n"
        index_lines.append(item)
    index_lines.append("- [Repository Documentation](#repository-documentation)\n\n")

    # Achievements Gallery heading anchor so 'All achievements' works
    gallery_header = "<a id=\"achievements-gallery\"></a>\n## Achievements Gallery\n\n"

    body_lines = []
    for i, e in enumerate(entries, start=1):
        title = e.get("title", "Untitled")
        date = e.get("date", "")
        desc = e.get("description", "")
        img = e.get("image", "")
        refs = e.get("references") or []

        # Card heading with anchor
        formatted_date = format_date(date)
        body_lines.append(f"<a id=\"ach-{i}\"></a>\n### {i}. {title} ({formatted_date})\n\n")

        # Use a simple two-column table for a clean, supported layout on GitHub
        body_lines.append("<table><tr>\n")
        # Left column: image(s) (rounded corners)
        body_lines.append("<td width=\"240\" valign=\"top\">\n")
        if img:
            images = img if isinstance(img, list) else [img]
            for idx, image_url in enumerate(images):
                margin = "margin-bottom:10px;" if idx < len(images) - 1 else ""
                body_lines.append(f"<img src=\"{image_url}\" alt=\"{title}\" width=\"220\" style=\"border-radius:8px;{margin}\" /><br/>\n")
        else:
            body_lines.append("(no image)")
        body_lines.append("</td>\n")

        # Right column: description + references
        body_lines.append("<td valign=\"top\">\n")
        if desc:
            body_lines.append(f"{desc}\n\n")

        # Render references (links/images) if present
        if refs:
            ref_items = []
            ref_images = []
            for r in refs:
                if isinstance(r, dict):
                    label = r.get("label") or r.get("title") or r.get("name") or r.get("url")
                    url = r.get("url")
                    ref_img = r.get("image")
                    if ref_img:
                        ref_images.append((label, ref_img))
                    elif url:
                        ref_items.append(f"<a href=\"{url}\" target=\"_blank\">{label}</a>")
                else:
                    ref_items.append(f"<a href=\"{r}\" target=\"_blank\">{r}</a>")
            if ref_items:
                body_lines.append("<p><strong>References:</strong> ")
                body_lines.append(" | ".join(ref_items))
                body_lines.append("</p>\n")
            if ref_images:
                body_lines.append("<p>")
                for lbl, img_url in ref_images:
                    body_lines.append(f"<strong>{lbl}:</strong><br/>")
                    body_lines.append(f"<img src=\"{img_url}\" alt=\"{lbl}\" width=\"400\" style=\"border-radius:8px; margin-top:8px;\"/><br/>")
                body_lines.append("</p>\n")

        # Back links and close table
        body_lines.append("</td>\n</tr></table>\n\n")
        body_lines.append("[Back to Index](#index) | [Back to Top](#my-achievements)\n\n---\n\n")

    # Repository documentation appended at the end
    repo_docs = (
        "## Repository Documentation\n\n"
        "### Installation\n\n"
        "Install required dependencies:\n\n"
        "    pip install requests beautifulsoup4\n\n"
        "### Usage\n\n"
        "**Add a badge interactively:**\n\n"
        "    python scripts/add_badge.py\n\n"
        "**Generate README:**\n\n"
        "    python scripts/generate_readme.py\n\n"
        "### How it works\n\n"
        "- `achievements.json` contains all entries\n"
        "- `scripts/add_badge.py` helps add Credly badges interactively\n"
        "- `scripts/generate_readme.py` generates this README with achievements sorted by date (newest first)\n"
        "- All dates are displayed in standard format: Month DD, YYYY\n\n"
        "### Manual Entry\n\n"
        "Edit `achievements.json` directly:\n\n"
        "    {\n"
        "      \"title\": \"Your Achievement\",\n"
        "      \"date\": \"2024-06-12\",\n"
        "      \"description\": \"Description here\",\n"
        "      \"image\": \"images/badge.png\",\n"
        "      \"references\": [{\"label\": \"Link\", \"url\": \"https://...\"}]\n"
        "    }\n\n"
        "Then run: `python scripts/generate_readme.py`\n\n"
    )

    # Combine parts. Provide an explicit index anchor so index links work and include top anchor
    full = []
    full.append("<a id=\"my-achievements\"></a>\n")
    full.append(top)
    full.append("<a id=\"index\"></a>\n")
    full.extend(index_lines)
    full.append(gallery_header)
    full.extend(body_lines)
    full.append(repo_docs)

    return "".join(full)


def main():
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        print("Error: cannot read achievements.json:", exc)
        sys.exit(1)

    if not isinstance(data, list):
        print("Error: achievements.json must be a JSON array of entries.")
        sys.exit(1)

    def sort_key(e):
        d = parse_date(e.get("date", ""))
        return d or datetime.date.min

    entries = sorted(data, key=sort_key, reverse=True)

    md = make_md(entries)
    try:
        with open(OUT_PATH, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Wrote {OUT_PATH} with {len(entries)} entries.")
    except Exception as exc:
        print("Error: cannot write README.md:", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
