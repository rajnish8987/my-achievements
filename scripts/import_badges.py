#!/usr/bin/env python3
"""
Manual Credly Badge Importer - Copy/paste badges from Credly directly.

Since Credly uses heavy JavaScript rendering, this tool helps you manually
enter badge details in an interactive way or from a JSON file.

Usage:
  python scripts/import_badges.py interactive
  python scripts/import_badges.py --from-file my_badges.json --auto-add
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ACHIEVEMENTS_PATH = os.path.join(ROOT, "achievements.json")


def interactive_badge_entry() -> List[Dict]:
    """Interactive mode to manually enter badges."""
    badges = []
    
    print("\n" + "="*70)
    print("MANUAL CREDLY BADGE IMPORTER")
    print("="*70)
    print("\nInstructions:")
    print("1. Go to https://www.credly.com/users/rajnish8987/badges")
    print("2. Right-click each badge and select 'Inspect'")
    print("3. Look for: alt text (badge name), src (image), and href (badge link)")
    print("4. Copy the information below for each badge")
    print("\nPress Enter to start adding badges, or 'q' to quit.\n")
    
    badge_num = 1
    while True:
        print(f"\n--- Badge #{badge_num} ---")
        name = input("Badge Name (or 'q' to finish): ").strip()
        
        if name.lower() == 'q':
            break
        
        if not name:
            print("Skipping - name is required")
            continue
        
        issuer = input("Issuer (e.g., Google Cloud): ").strip() or "Credly"
        image_url = input("Image URL (right-click badge > Copy image link): ").strip() or ""
        badge_url = input("Badge URL (copy from browser address bar or link): ").strip() or "https://www.credly.com"
        date_str = input("Date earned (YYYY-MM-DD, or press Enter for today): ").strip() or datetime.now().strftime("%Y-%m-%d")
        
        badge = {
            "name": name,
            "issuer": issuer,
            "image_url": image_url,
            "url": badge_url,
            "issued_date": date_str
        }
        
        badges.append(badge)
        print(f"✓ Added: {name}")
        badge_num += 1
    
    return badges


def load_badges_from_file(file_path: str) -> List[Dict]:
    """Load badges from JSON file."""
    full_path = os.path.join(ROOT, file_path) if not os.path.isabs(file_path) else file_path
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            badges = json.load(f)
        print(f"✓ Loaded {len(badges)} badges from {file_path}")
        return badges
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        sys.exit(1)


def convert_badge_to_achievement(badge: Dict, index: int) -> Dict:
    """Convert badge to achievement entry."""
    date_str = badge.get("issued_date") or badge.get("issued_on") or datetime.now().strftime("%Y-%m-%d")
    
    return {
        "title": badge.get("name", f"Badge {index}"),
        "date": date_str,
        "description": f"Certified by {badge.get('issuer', 'Credly')}",
        "image": badge.get("image_url", ""),
        "references": [
            {
                "label": "View Badge",
                "url": badge.get("url", "https://www.credly.com")
            }
        ]
    }


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/import_badges.py interactive")
        print("  python scripts/import_badges.py --from-file FILE [--auto-add]")
        print("\nExamples:")
        print("  python scripts/import_badges.py interactive")
        print("  python scripts/import_badges.py --from-file scripts/credly_template.json --auto-add")
        sys.exit(1)
    
    auto_add = "--auto-add" in sys.argv
    from_file = None
    
    # Parse --from-file argument
    for i, arg in enumerate(sys.argv):
        if arg == "--from-file" and i + 1 < len(sys.argv):
            from_file = sys.argv[i + 1]
    
    # Get badges
    if sys.argv[1] == "interactive":
        badges = interactive_badge_entry()
    elif from_file:
        badges = load_badges_from_file(from_file)
    else:
        print(f"Unknown command: {sys.argv[1]}")
        sys.exit(1)
    
    if not badges:
        print("No badges entered.")
        return
    
    # Display summary
    print(f"\n{'='*70}")
    print(f"SUMMARY: {len(badges)} badges collected")
    print(f"{'='*70}\n")
    
    for i, badge in enumerate(badges, start=1):
        print(f"{i}. {badge.get('name', 'Unknown')}")
        print(f"   Issuer: {badge.get('issuer', 'N/A')}")
        print(f"   Date: {badge.get('issued_date', 'N/A')}")
        print(f"   URL: {badge.get('url', 'N/A')[:50]}...")
    
    # Save to temp file for review
    temp_file = os.path.join(ROOT, "imported_badges.json")
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(badges, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved to {temp_file} for review")
    
    # Option to auto-add
    if auto_add or input("\nAdd these to achievements.json? (y/n): ").lower() == 'y':
        try:
            with open(ACHIEVEMENTS_PATH, "r", encoding="utf-8") as f:
                achievements = json.load(f)
        except FileNotFoundError:
            achievements = []
        
        # Convert and add
        new_achievements = [convert_badge_to_achievement(b, i) for i, b in enumerate(badges, start=1)]
        achievements.extend(new_achievements)
        
        with open(ACHIEVEMENTS_PATH, "w", encoding="utf-8") as f:
            json.dump(achievements, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Added {len(new_achievements)} badges to achievements.json")
        print("\nNext step:")
        print("  python scripts/generate_readme.py")
    else:
        print("Badges saved but not added to achievements.json")
        print(f"To add later: python scripts/import_badges.py --from-file {temp_file} --auto-add")


if __name__ == "__main__":
    main()
