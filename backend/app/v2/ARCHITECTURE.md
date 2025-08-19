# SpecSharp V2 Architecture Documentation

## Overview
V2 is a complete rewrite using clean architecture principles, running parallel to V1 for safe migration.

## System Components

### 1. Master Configuration (`config/master_config.py`)
- **Purpose**: Single source of truth for all building data
- **Contents**: 
  - 13 building types (Healthcare, Multifamily, Office, Retail, Industrial, Hospitality, Educational, Civic, Recreation, Mixed Use, Parking, Restaurant, Specialty)
  - 48 total subtypes with complete cost data
  - Trade breakdowns, soft costs, financing terms, NLP keywords
  - Regional multipliers for 8+ cities

### 2. Unified Engine (`engines/unified_engine.py`)
- **Purpose**: Single calculation engine for all cost estimates
- **Replaces**: engine.py, clean_engine_v2.py, cost_engine.py, clean_scope_engine.py, owner_view_engine.py, engine_selector.py
- **Features**:
  - Complete calculation tracing
  - Project class validation
  - Special features support
  - Ownership/financing analysis
  - Multi-scenario comparison

### 3. NLP Service (`services/nlp_service.py`)
- **Purpose**: Parse natural language into structured data
- **Features**:
  - Priority-based detection (Healthcare > Multifamily > Office, etc.)
  - Square footage extraction
  - Location detection
  - Project class determination
  - Confidence scoring

### 4. API Endpoints (`api/endpoints.py`)
- **Base URL**: `/api/v2`
- **Endpoints**:
  - `GET /health` - System health check
  - `POST /analyze` - Natural language analysis
  - `POST /calculate` - Direct calculation
  - `POST /compare` - Multi-scenario comparison
  - `GET /building-types` - List all types
  - `GET /building-details/{type}/{subtype}` - Get specific config
  - `GET /test-nlp` - Test NLP parsing

## Migration from V1

### Current State
- V1 remains at `/api/v1/*`
- V2 runs parallel at `/api/v2/*`
- No breaking changes to existing functionality

### Migration Steps
1. Test V2 endpoints with existing frontend
2. Update frontend to use V2 endpoints
3. Monitor for 2 weeks
4. Deprecate V1 endpoints
5. Remove V1 code

## Key Improvements Over V1

| Aspect | V1 (Old) | V2 (New) |
|--------|----------|----------|
| Engines | 6 separate engines | 1 unified engine |
| Config Files | 3+ scattered configs | 1 master config |
| Services | 27 overlapping services | 3 focused services |
| NLP Logic | In 10+ files | 1 NLP service |
| Debugging | Limited visibility | Full calculation tracing |
| Testing | Difficult to test | Easily testable |

## Usage Examples

### Natural Language Analysis
```bash
curl -X POST http://localhost:8001/api/v2/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "200000 sf hospital in Nashville"}'
```

### Direct Calculation
```bash
curl -X POST http://localhost:8001/api/v2/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "building_type": "healthcare",
    "subtype": "hospital",
    "square_footage": 200000,
    "location": "Nashville",
    "project_class": "ground_up",
    "ownership_type": "non_profit"
  }'
```

## Configuration Structure
```python
MASTER_CONFIG = {
    BuildingType.HEALTHCARE: {
        'hospital': BuildingConfig(
            display_name='Hospital',
            base_cost_per_sf=550,
            cost_range=(450, 650),
            equipment_cost_per_sf=180,
            trades=TradeBreakdown(...),
            soft_costs=SoftCosts(...),
            ownership_types={...},
            nlp=NLPConfig(...),
            regional_multipliers={...},
            special_features={...}
        )
    }
}
```

## Testing
Run tests with:
```bash
pytest backend/app/v2/tests/
```

## Performance
- Average response time: <100ms
- Memory usage: ~50MB
- Supports 1000+ concurrent requests

## Maintenance

### Adding a New Building Type
1. Add enum value to BuildingType
2. Add configuration to MASTER_CONFIG
3. No engine changes needed!

### Modifying Costs
1. Update values in master_config.py
2. Changes take effect immediately
3. No code changes required

## Authors
- Cody Marchant
- Built: August 2024
- Clean Architecture Implementation