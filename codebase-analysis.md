# SpecSharp Codebase Analysis

## Statistics
- Total Python/TypeScript files: 211
- Backend engines: 6
- Backend services: 27
- Config files: 3 main configs

## Architecture Issues Found

### 1. Multiple Engines (Duplication)
- `engine.py` - Original engine
- `clean_engine_v2.py` - Newer clean version
- `clean_scope_engine.py` - Another scope engine
- `cost_engine.py` - Cost calculation engine
- `engine_selector.py` - Selects between engines
- `owner_view_engine.py` - Owner view specific

### 2. Service Proliferation
- 27 different services with overlapping responsibilities
- Multiple versions: `electrical_standards_service.py` vs `electrical_v2_service.py`
- Duplicate exports: `excel_export_service.py` vs `excel_export_service_v2.py`
- Specialized services that could be consolidated:
  - `healthcare_cost_service.py`
  - `restaurant_cost_service.py`
  - `cost_service.py`

### 3. Tenant Improvement Logic Scattered
Found in 10 different files across backend and frontend:
- Multiple implementations of TI logic
- No single source of truth

### 4. Config Fragmentation
- `config.py` - Main config
- `building_types_config.py` - Building types
- `owner_metrics_config.py` - Owner metrics
- Each could be part of a unified configuration system

## Recommendations for Clean Architecture

1. **Consolidate Engines** → Single engine with strategy pattern
2. **Merge Services** → Domain-driven service organization
3. **Centralize TI Logic** → Single module for project classifications
4. **Unify Configurations** → Single config module with sub-modules

