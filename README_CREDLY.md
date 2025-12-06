# Credly Integration Guide

Your repository now supports pulling Credly badges into your achievements list!

## How to add Credly badges

### Option 1: Manual JSON (Recommended for now)

Since Credly's frontend is JavaScript-heavy, the easiest approach is manual entry:

1. **Copy the template:**
   ```powershell
   copy scripts\credly_template.json scripts\my_badges.json
   ```

2. **Fill in your badges:** Edit `scripts/my_badges.json` with your badge details from https://www.credly.com/users/rajnish8987

   For each badge, get:
   - `name`: Badge title
   - `issuer`: Issuing organization (e.g., "Google Cloud")
   - `image_url`: URL to badge image (right-click badge → Copy image link)
   - `url`: Full badge URL
   - `issued_date`: Date earned (YYYY-MM-DD format)

3. **Auto-import to achievements:**
   ```powershell
   python scripts/fetch_credly.py --from-file scripts/my_badges.json --auto-add
   ```

4. **Regenerate README:**
   ```powershell
   python scripts/generate_readme.py
   ```

### Option 2: Direct Username (Experimental)

If Credly's HTML structure changes or unlocks, try:
```powershell
python scripts/fetch_credly.py rajnish8987 --auto-add
python scripts/generate_readme.py
```

## Example JSON Entry

```json
{
  "name": "Google Cloud Professional Cloud Architect",
  "issuer": "Google Cloud",
  "image_url": "https://images.credly.com/...",
  "url": "https://www.credly.com/badges/...",
  "issued_date": "2025-06-05"
}
```

## Full Workflow

```powershell
# 1. Prepare your badges file
copy scripts\credly_template.json scripts\my_badges.json

# 2. Edit scripts/my_badges.json with your badges

# 3. Import into achievements
python scripts/fetch_credly.py --from-file scripts/my_badges.json --auto-add

# 4. Regenerate README
python scripts/generate_readme.py

# 5. (Optional) Commit
git add achievements.json README.md
git commit -m "Add Credly badges"
```

## Commands Reference

```powershell
# Load from file and auto-add to achievements
python scripts/fetch_credly.py --from-file scripts/my_badges.json --auto-add

# Load from file and save output
python scripts/fetch_credly.py --from-file scripts/my_badges.json --output credly_badges.json

# Try fetching directly from username (may not work due to JS rendering)
python scripts/fetch_credly.py rajnish8987
```

## Tips

- Badge images work best if hosted on Credly's CDN (images.credly.com)
- Dates should be in `YYYY-MM-DD` format for proper sorting
- Use `null` or empty string for missing fields
- Run `python scripts/generate_readme.py` after any changes to see updated README

---

Questions? Check the main README.md for the full achievements workflow!
