#!/usr/bin/env python3
"""
Fetch badges from Credly profile and optionally add to achievements.json.

Usage:
  python scripts/fetch_credly.py <credly_username> [--auto-add] [--output badges.json]

Examples:
  python scripts/fetch_credly.py rajnish8987
  python scripts/fetch_credly.py rajnish8987 --auto-add
  python scripts/fetch_credly.py rajnish8987 --output credly_badges.json
"""

import requests
import json
import sys
import os
from datetime import datetime
from typing import List, Dict
from pathlib import Path
from bs4 import BeautifulSoup
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ACHIEVEMENTS_PATH = os.path.join(ROOT, "achievements.json")


def fetch_credly_badges(username: str) -> List[Dict]:
    """
    Fetch badges from Credly profile using web scraping and JSON extraction.
    
    Args:
        username: Credly username (e.g., 'rajnish8987')
    
    Returns:
        List of badge dictionaries with name, issuer, image_url, url
    """
    profile_url = f"https://www.credly.com/users/{username}"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(profile_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error: Failed to fetch Credly profile: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    badges = []

    # Method 1: Look for JSON-LD script tags
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            json_data = json.loads(script.string)
            if isinstance(json_data, dict) and "badge" in json_data:
                badge = json_data["badge"]
                badges.append({
                    "name": badge.get("name", "Badge"),
                    "issuer": badge.get("issuer", {}).get("name", ""),
                    "image_url": badge.get("image", ""),
                    "url": profile_url
                })
        except:
            pass

    # Method 2: Look for embedded badge data in script tags
    for script in soup.find_all("script"):
        if script.string:
            try:
                # Extract JSON data if present
                json_match = re.search(r'"badges"\s*:\s*(\[.*?\])', script.string, re.DOTALL)
                if json_match:
                    badges_json = json.loads(json_match.group(1))
                    for badge in badges_json:
                        badges.append({
                            "name": badge.get("name", "Badge"),
                            "issuer": badge.get("issuer", ""),
                            "image_url": badge.get("imageUrl", ""),
                            "url": badge.get("url", profile_url)
                        })
                    break
            except:
                pass

    # Method 3: Look for badge containers in HTML
    if not badges:
        badge_containers = soup.find_all(class_=re.compile(r"badge", re.I))
        for container in badge_containers:
            try:
                badge_name = container.find(class_=re.compile(r"name|title", re.I))
                badge_img = container.find("img")
                badge_issuer = container.find(class_=re.compile(r"issuer", re.I))
                badge_link = container.find("a", href=True)
                
                if badge_name or badge_img:
                    badges.append({
                        "name": badge_name.get_text(strip=True) if badge_name else "Badge",
                        "issuer": badge_issuer.get_text(strip=True) if badge_issuer else "Credly",
                        "image_url": badge_img.get("src", "") if badge_img else "",
                        "url": badge_link.get("href", profile_url) if badge_link else profile_url
                    })
            except:
                pass

    return badges


def fetch_credly_api(username: str) -> List[Dict]:
    """
    Alternative: Fetch via Credly's public API (if available).
    This is a fallback approach using the Credly public data endpoints.
    """
    try:
        # Attempt to fetch from public profile endpoint
        api_url = f"https://www.credly.com/api/v1/public/profile/{username}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            badges = []
            
            if "badges" in data:
                for badge in data["badges"]:
                    badges.append({
                        "name": badge.get("name", ""),
                        "issuer": badge.get("issuer", {}).get("name", ""),
                        "image_url": badge.get("image_url", ""),
                        "url": badge.get("url", ""),
                        "issued_date": badge.get("issued_on", "")
                    })
            return badges
    except Exception as e:
        print(f"Note: API fetch not available: {e}", file=sys.stderr)
    
    return []


def convert_badge_to_achievement(badge: Dict, index: int) -> Dict:
    """
    Convert a Credly badge to an achievement entry.
    """
    # Handle both 'issued_date' and 'issued_on' formats
    date_str = badge.get("issued_date") or badge.get("issued_on") or datetime.now().strftime("%Y-%m-%d")
    
    return {
        "title": badge.get("name", f"Badge {index}"),
        "date": date_str,
        "description": f"Earned from {badge.get('issuer', 'Credly')}",
        "image": badge.get("image_url", ""),
        "references": [
            {
                "label": "View on Credly",
                "url": badge.get("url", "https://www.credly.com")
            }
        ]
    }


def load_badges_from_file(file_path: str) -> List[Dict]:
    """Load badges from a JSON file."""
    full_path = os.path.join(ROOT, file_path) if not os.path.isabs(file_path) else file_path
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            badges = json.load(f)
        print(f"✓ Loaded {len(badges)} badges from {file_path}")
        return badges
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/fetch_credly.py [OPTIONS]")
        print("\nOptions:")
        print("  <username>           Fetch badges from Credly username")
        print("  --from-file FILE     Load badges from JSON file (e.g., credly_template.json)")
        print("  --auto-add           Auto-add fetched badges to achievements.json")
        print("  --output FILE        Save raw badge data to file")
        print("\nExamples:")
        print("  python scripts/fetch_credly.py rajnish8987")
        print("  python scripts/fetch_credly.py rajnish8987 --auto-add")
        print("  python scripts/fetch_credly.py --from-file scripts/credly_template.json --auto-add")
        print("\nManual workflow:")
        print("  1. Copy scripts/credly_template.json to scripts/my_badges.json")
        print("  2. Fill in your badge details from https://www.credly.com/users/<your-username>")
        print("  3. Run: python scripts/fetch_credly.py --from-file scripts/my_badges.json --auto-add")
        print("  4. Run: python scripts/generate_readme.py")
        sys.exit(1)

    username = None
    auto_add = "--auto-add" in sys.argv
    output_file = None
    from_file = None
    
    for i, arg in enumerate(sys.argv[1:], start=1):
        if arg.startswith("--"):
            if arg == "--output" and i + 1 < len(sys.argv):
                output_file = sys.argv[i + 1]
            elif arg == "--from-file" and i + 1 < len(sys.argv):
                from_file = sys.argv[i + 1]
        elif not arg.startswith("-"):
            username = arg
    
    # If --from-file is specified, load from file instead
    if from_file:
        badges = load_badges_from_file(from_file)
    elif username:
        print(f"Fetching badges for '{username}' from Credly...")
        
        # Try API first, fallback to scraping
        badges = fetch_credly_api(username)
        if not badges:
            print("Trying web scraping...")
            badges = fetch_credly_badges(username)
    else:
        print("Error: Provide either a username or --from-file option")
        sys.exit(1)

    if not badges:
        print("No badges found. Make sure the username is correct and the profile is public.")
        sys.exit(1)

    print(f"Found {len(badges)} badges!\n")

    for i, badge in enumerate(badges, start=1):
        print(f"{i}. {badge.get('name', 'Unknown')}")
        print(f"   Issuer: {badge.get('issuer', 'N/A')}")
        print(f"   URL: {badge.get('url', 'N/A')}")
        print()

    # Option 1: Save to separate file
    if output_file:
        output_path = os.path.join(ROOT, output_file)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(badges, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved raw badges to {output_file}")

    # Option 2: Auto-add to achievements.json
    if auto_add:
        try:
            with open(ACHIEVEMENTS_PATH, "r", encoding="utf-8") as f:
                achievements = json.load(f)
        except FileNotFoundError:
            achievements = []

        # Convert badges to achievements
        new_achievements = [convert_badge_to_achievement(b, i) for i, b in enumerate(badges, start=1)]
        
        # Append (or you could merge/deduplicate)
        achievements.extend(new_achievements)

        with open(ACHIEVEMENTS_PATH, "w", encoding="utf-8") as f:
            json.dump(achievements, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Added {len(new_achievements)} badges to achievements.json")
        print("\nRun 'python scripts/generate_readme.py' to regenerate README.md with badges.")


if __name__ == "__main__":
    main()
