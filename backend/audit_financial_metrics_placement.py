import re

# Read the master_config file
with open('app/v2/config/master_config.py', 'r') as f:
    content = f.read()

# Find patterns where financial_metrics appears after a closing parenthesis
# Pattern: ),\nfinancial_metrics= or similar
misplaced_pattern = r'\),\s*financial_metrics\s*='
matches = re.findall(misplaced_pattern, content)

print(f"Found {len(matches)} misplaced financial_metrics blocks")

# Find all subtypes that have financial_metrics
all_financial_metrics = re.findall(r"'(\w+)':[^}]*financial_metrics", content)
print(f"Total subtypes with financial_metrics: {len(set(all_financial_metrics))}")

# Find subtypes that might have syntax errors
lines = content.split('\n')
error_locations = []
for i, line in enumerate(lines):
    if 'financial_metrics=' in line and i > 0:
        # Check if previous non-empty line ends with ),
        for j in range(i-1, max(0, i-10), -1):
            prev_line = lines[j].strip()
            if prev_line:
                if prev_line.endswith('),'):
                    error_locations.append((i+1, lines[i].strip()[:50]))
                break

print(f"\nLines with potential syntax errors:")
for line_num, preview in error_locations:
    print(f"  Line {line_num}: {preview}...")

# Check which subtypes are missing financial_metrics
expected_subtypes = [
    'public_safety', 'library', 'community_center', 'courthouse',
    'fitness_center', 'sports_complex', 'aquatic_center', 'recreation_center', 'stadium',
    'retail_residential', 'office_residential', 'hotel_retail', 'urban_mixed', 'transit_oriented',
    'surface_parking', 'parking_garage', 'underground_parking', 'automated_parking',
    'quick_service', 'full_service', 'bar_tavern', 'cafe',
    'data_center', 'laboratory', 'self_storage', 'car_dealership', 'broadcast_facility'
]

for subtype in expected_subtypes:
    if subtype not in all_financial_metrics:
        print(f"Missing financial_metrics: {subtype}")