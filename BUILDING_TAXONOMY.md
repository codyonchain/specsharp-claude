# Building Type Taxonomy - Single Source of Truth

## Overview
This document describes the standardized building type taxonomy used throughout SpecSharp. All components MUST use this taxonomy to ensure consistency.

## Canonical Building Types

There are exactly **11 canonical building types**:

| Canonical Type | Display Name | Common Aliases | Base Cost/SF |
|---------------|--------------|----------------|--------------|
| `residential` | Residential | multifamily, apartments, multi_family | $375 |
| `healthcare` | Healthcare | medical, health | $550 |
| `educational` | Educational | education, school, academic | $295 |
| `commercial` | Commercial | office, business | $350 |
| `industrial` | Industrial | warehouse, manufacturing, logistics | $185 |
| `retail` | Retail | shopping, store, shop | $250 |
| `hospitality` | Hospitality | hotel, lodging, accommodation | $425 |
| `restaurant` | Restaurant | dining, food service, eatery | $375 |
| `civic` | Civic | government, municipal, public | $425 |
| `recreation` | Recreation | sports, fitness, entertainment | $325 |
| `parking` | Parking | garage, parking structure | $65 |

## Key Files

### 1. Source of Truth
- **Location**: `/shared/building_types.json`
- **Purpose**: Complete taxonomy definition with subtypes, keywords, and base costs
- **Format**: JSON

### 2. Python Enforcer
- **Location**: `/backend/app/core/building_taxonomy.py`
- **Key Functions**:
  ```python
  from app.core.building_taxonomy import (
      normalize_building_type,  # Convert any string to canonical
      validate_building_type,    # Validate type/subtype pair
      get_display_name,          # Get human-readable name
      get_base_cost              # Get base cost per SF
  )
  ```

### 3. TypeScript Enforcer
- **Location**: `/frontend/src/core/buildingTaxonomy.ts`
- **Key Functions**:
  ```typescript
  import { 
    BuildingTaxonomy,
    normalizeType,
    getDisplayName,
    validate
  } from '@/core/buildingTaxonomy';
  ```

## Migration Guide

### Old → New Mappings
| Old Value | Canonical Value |
|-----------|----------------|
| `multifamily` | `residential` |
| `multi_family` | `residential` |
| `multi_family_residential` | `residential` |
| `medical` | `healthcare` |
| `education` | `educational` |
| `office` | `commercial` |
| `warehouse` | `industrial` |
| `manufacturing` | `industrial` |
| `shopping` | `retail` |
| `hotel` | `hospitality` |

### Usage Examples

#### Python
```python
from app.core.building_taxonomy import normalize_building_type, validate_building_type

# Normalize any input
canonical = normalize_building_type("multifamily")  # Returns: "residential"
canonical = normalize_building_type("MEDICAL")      # Returns: "healthcare"

# Validate type/subtype
valid_type, valid_subtype = validate_building_type("office", "class a")
# Returns: ("commercial", "class_a")
```

#### TypeScript
```typescript
import { normalizeType, validate } from '@/core/buildingTaxonomy';

// Normalize any input
const canonical = normalizeType("multifamily");  // Returns: "residential"

// Validate type/subtype
const [validType, validSubtype] = validate("office", "class a");
// Returns: ["commercial", "class_a"]
```

## Common Subtypes

### Residential
- `luxury_apartments` - Luxury/Class A apartments ($425/SF)
- `market_rate_apartments` - Standard apartments ($375/SF)
- `affordable_housing` - Affordable/workforce housing ($325/SF)
- `student_housing` - Student dormitories ($350/SF)
- `senior_living` - Senior/assisted living ($400/SF)

### Healthcare
- `hospital` - Full-service hospital ($1150/SF)
- `medical_office` - Medical office building ($450/SF)
- `urgent_care` - Urgent care facility ($475/SF)
- `surgical_center` - Ambulatory surgery center ($750/SF)
- `specialty_clinic` - Specialty medical clinic ($550/SF)

### Educational
- `elementary_school` - Elementary school K-5 ($285/SF)
- `middle_school` - Middle school 6-8 ($295/SF)
- `high_school` - High school 9-12 ($310/SF)
- `university` - College/university ($425/SF)
- `vocational` - Trade/technical school ($275/SF)

### Commercial
- `class_a` - Premium office space ($450/SF)
- `class_b` - Standard office space ($350/SF)
- `class_c` - Economy office space ($275/SF)
- `corporate_campus` - Corporate headquarters ($500/SF)
- `coworking` - Shared workspace ($385/SF)

## Implementation Status

✅ **Completed**:
- Single source of truth JSON created
- Python taxonomy enforcer module
- TypeScript taxonomy enforcer
- V2 parser integration
- Comprehensive testing

## Rules for Developers

1. **NEVER** hardcode building types - always use the taxonomy
2. **ALWAYS** normalize user input through the taxonomy functions
3. **NEVER** create new building types without updating the taxonomy
4. **ALWAYS** use canonical types in database storage
5. **DISPLAY** names should come from `getDisplayName()` functions

## Testing

Run the taxonomy test suite:
```bash
cd backend
source venv/bin/activate
python test_taxonomy.py
```

Expected output: All tests should pass with proper normalization of all variations to canonical types.