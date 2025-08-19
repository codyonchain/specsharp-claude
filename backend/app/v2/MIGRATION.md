# V1 to V2 Migration Tracker

## Systems to Replace

### Engines (6 → 1)
- [ ] backend/app/core/engine.py
- [ ] backend/app/core/clean_scope_engine.py
- [ ] backend/app/core/cost_engine.py
- [ ] backend/app/services/clean_engine_v2.py
- [ ] backend/app/core/engine_selector.py
- [ ] backend/app/services/owner_view_engine.py
→ **Replaced by: v2/engines/unified_engine.py**

### Configs (3 → 1)
- [ ] backend/app/services/building_types_config.py
- [ ] backend/app/services/owner_metrics_config.py
- [ ] backend/app/core/config.py
→ **Replaced by: v2/config/master_config.py**

### Services (27 → ~8)
Priority services to consolidate:
- [ ] nlp_service.py → v2/services/nlp_service.py
- [ ] cost_service.py + healthcare_cost_service.py + restaurant_cost_service.py → v2/services/cost_service.py
- [ ] excel_export_service.py + excel_export_service_v2.py → v2/services/export_service.py
- [ ] electrical_standards_service.py + electrical_v2_service.py → Merged into unified engine

## Testing Checklist
- [ ] Hospital detection (not classified as TI)
- [ ] Multifamily calculations
- [ ] Owner view calculations
- [ ] Trade breakdowns
- [ ] Regional multipliers
- [ ] Export functionality

## Rollback Plan
If V2 has issues:
1. Frontend continues using /api/v1
2. No changes needed to rollback
3. V2 can be fixed without affecting production