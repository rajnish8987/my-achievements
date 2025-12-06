#!/usr/bin/env python3
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ACHIEVEMENTS_PATH = os.path.join(ROOT, "achievements.json")

print("=== Add Credly Badge to Achievements ===\n")
print("Paste badge URL from Credly (e.g., https://www.credly.com/badges/abc123):")
badge_url = input("> ").strip()

print("\nBadge name:")
name = input("> ").strip()

print("\nIssuer (e.g., Google Cloud, AWS):")
issuer = input("> ").strip()

print("\nImage URL (right-click badge image → Copy image address):")
image_url = input("> ").strip()

print("\nIssued date (YYYY-MM-DD, or press Enter for today):")
date = input("> ").strip()
if not date:
    from datetime import datetime
    date = datetime.now().strftime("%Y-%m-%d")

# Load achievements
try:
    with open(ACHIEVEMENTS_PATH, "r", encoding="utf-8") as f:
        achievements = json.load(f)
except:
    achievements = []

# Add new achievement
achievements.append({
    "title": name,
    "date": date,
    "description": f"Earned from {issuer}",
    "image": image_url,
    "references": [{"label": "View on Credly", "url": badge_url}]
})

# Save
with open(ACHIEVEMENTS_PATH, "w", encoding="utf-8") as f:
    json.dump(achievements, f, indent=2, ensure_ascii=False)

print(f"\n✓ Added '{name}' to achievements.json")
print("\nAdd another? (y/n):")
if input("> ").lower() == 'y':
    os.system(f"python {__file__}")
else:
    print("\nRun: python scripts/generate_readme.py")
