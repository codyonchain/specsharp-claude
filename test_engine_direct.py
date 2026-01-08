import sys
sys.path.insert(0, 'backend')

from app.v2.engines.unified_engine import UnifiedEngine
from app.v2.config.master_config import BuildingType, ProjectClass

engine = UnifiedEngine()

# Test Nashville directly with the exact parameters the API uses
result = engine.calculate_project(
    building_type=BuildingType.OFFICE,
    subtype='class_b',  # API detects class_b for generic office
    square_footage=10000,
    location='Nashville, Tennessee',  # Exact string from API
    project_class=ProjectClass.GROUND_UP
)

print("Direct Engine Test:")
print(f"Location passed: Nashville, Tennessee")
print(f"Building: OFFICE/class_b")

# Check construction_costs
construction_costs = result.get('construction_costs', {})
print(f"\nRegional Multiplier: {construction_costs.get('regional_multiplier', 'MISSING')}")

# Check cost_dna
cost_dna = result.get('cost_dna', {})
if cost_dna:
    print(f"Cost DNA Regional: {cost_dna.get('regional_adjustment', 'MISSING')}")
    print(f"Market Name: {cost_dna.get('market_name', 'MISSING')}")
else:
    print("Cost DNA: MISSING")

# Test what get_regional_multiplier returns directly
from app.v2.config.master_config import get_regional_multiplier
direct_result = get_regional_multiplier(BuildingType.OFFICE, 'class_b', 'Nashville, Tennessee')
print(f"\nDirect function call: get_regional_multiplier(OFFICE, class_b, 'Nashville, Tennessee') = {direct_result}")