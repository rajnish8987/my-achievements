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
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except Exception:
            continue
    return None


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
        body_lines.append(f"<a id=\"ach-{i}\"></a>\n### {i}. {title} ({date})\n\n")

        # Use a simple two-column table for a clean, supported layout on GitHub
        body_lines.append("<table><tr>\n")
        # Left column: image (rounded corners)
        if img:
            body_lines.append(
                f"<td width=\"240\" valign=\"top\">\n<img src=\"{img}\" alt=\"{title}\" width=\"220\" style=\"border-radius:8px;\" />\n</td>\n"
            )
        else:
            body_lines.append("<td width=\"240\" valign=\"top\">(no image)</td>\n")

        # Right column: description + references
        body_lines.append("<td valign=\"top\">\n")
        if desc:
            body_lines.append(f"{desc}\n\n")

        # Render references (links) if present
        if refs:
            ref_items = []
            for r in refs:
                if isinstance(r, dict):
                    label = r.get("label") or r.get("title") or r.get("name") or r.get("url")
                    url = r.get("url")
                else:
                    # allow string shorthand
                    label = r
                    url = r
                if url:
                    ref_items.append(f"<a href=\"{url}\">{label}</a>")
            if ref_items:
                body_lines.append("<p><strong>References:</strong> ")
                body_lines.append(" | ".join(ref_items))
                body_lines.append("</p>\n")

        # Back links and close table
        body_lines.append("[Back to Index](#index) | [Back to Top](#my-achievements)\n\n")
        body_lines.append("</td>\n</tr></table>\n\n---\n\n")

    # Repository documentation appended at the end
    repo_docs = (
        "## Repository Documentation\n\n"
        "### How it works\n\n"
        "- The file `achievements.json` contains structured entries.\n"
        "- The script `scripts/generate_readme.py` reads `achievements.json` and writes the `## Achievements Gallery` section in `README.md`.\n"
        "- You can edit `achievements.json` and run the script to update the README so GitHub shows your images directly on the repository page.\n\n"
        "### Example\n\n"
        "Edit `achievements.json` and add entries like:\n\n"
        "    {\n"
        "      \"title\": \"Won Math Olympiad\",\n"
        "      \"date\": \"2024-06-12\",\n"
        "      \"description\": \"First place in regional math competition.\",\n"
        "      \"image\": \"images/my-award.jpg\"\n"
        "    }\n\n"
        "Then run:\n\n"
        "    python scripts/generate_readme.py\n\n"
        "The script will sort entries by date (newest first) and rewrite the gallery section in this `README.md`.\n\n"
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
