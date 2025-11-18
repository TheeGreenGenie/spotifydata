"""
Fix NaN values in JSON files
"""
import re

def fix_nan_in_json(file_path):
    """Replace NaN with null in JSON file"""
    print(f"Fixing {file_path}...")

    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count NaN occurrences
    nan_count = content.count(': NaN')
    print(f"  Found {nan_count} NaN values")

    # Replace NaN with null
    # Handle different NaN patterns
    content = re.sub(r':\s*NaN\s*([,\n\}])', r': null\1', content)

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  [OK] Fixed {nan_count} NaN values")

if __name__ == "__main__":
    # Fix both JSON files
    fix_nan_in_json('music-analytics-dashboard/public/data/artists-data.json')
    fix_nan_in_json('music-analytics-dashboard/public/data/predictions-data.json')
    print("\n[OK] All JSON files fixed!")
