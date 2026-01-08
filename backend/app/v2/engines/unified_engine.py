"""
The single engine that handles ALL calculations.
This replaces: engine.py, clean_engine_v2.py, cost_engine.py, 
clean_scope_engine.py, owner_view_engine.py, engine_selector.py
"""

from datetime import datetime, date
from app.config.regional_multipliers import resolve_location_context
from app.v2.config.master_config import (
    MASTER_CONFIG,
    BuildingType,
    ProjectClass,
    OwnershipType,
    PROJECT_CLASS_MULTIPLIERS,
    PROJECT_TIMELINES,
    get_building_config,
    get_effective_modifiers,
    get_margin_pct,
    get_target_roi,
    detect_building_type_with_method,
    resolve_quality_factor,
    validate_project_class,
    infer_finish_level,
    get_building_profile,
)
from app.v2.config.construction_schedule import (
    CONSTRUCTION_SCHEDULES,
    CONSTRUCTION_SCHEDULE_FALLBACKS,
)
# from app.v2.services.financial_analyzer import FinancialAnalyzer  # TODO: Implement this
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import asdict, replace
import logging

logger = logging.getLogger(__name__)


def _add_months(base_date: date, months: int) -> date:
    """Add months to a date without relying on external libs."""
    month = base_date.month - 1 + months
    year = base_date.year + month // 12
    month = month % 12 + 1
    day = min(base_date.day, 28)  # avoid month-end overflow
    return date(year, month, day)


def _month_to_quarter_string(d: date) -> str:
    """Convert a date to a quarter string like 'Q1 2025'."""
    quarter = (d.month - 1) // 3 + 1
    return f"Q{quarter} {d.year}"


def build_construction_schedule(building_type: BuildingType) -> Dict[str, Any]:
    """
    Build the construction schedule payload (total duration + phase timings)
    for the Construction Schedule card.
    """
    schedule_config = CONSTRUCTION_SCHEDULES.get(building_type)
    if not schedule_config:
        fallback_type = CONSTRUCTION_SCHEDULE_FALLBACKS.get(building_type)
        if fallback_type:
            schedule_config = CONSTRUCTION_SCHEDULES.get(fallback_type)
    if not schedule_config:
        schedule_config = CONSTRUCTION_SCHEDULES.get(BuildingType.OFFICE, {})

    total_months = int(schedule_config.get("total_months", 0) or 0)
    phases_payload: List[Dict[str, Any]] = []
    for phase in schedule_config.get("phases", []):
        start_month = int(phase.get("start_month", 0) or 0)
        duration = int(phase.get("duration", 0) or 0)
        end_month = start_month + duration
        if total_months:
            end_month = min(end_month, total_months)
        phase_payload = {
            "id": phase.get("id"),
            "label": phase.get("label"),
            "start_month": start_month,
            "duration_months": duration,
            "end_month": end_month,
        }
        color = phase.get("color")
        if color:
            phase_payload["color"] = color
        phases_payload.append(phase_payload)

    return {
        "building_type": building_type.value if isinstance(building_type, BuildingType) else building_type,
        "total_months": total_months,
        "phases": phases_payload,
    }


def build_project_timeline(building_type: BuildingType, start_date: Optional[date] = None) -> Dict[str, str]:
    """
    Build a project timeline dictionary for the Executive View "Key Milestones" card.
    Returns milestone names mapped to quarter strings (e.g., 'Q1 2025').
    """
    base_date = start_date or date(2025, 1, 1)

    config = PROJECT_TIMELINES.get(building_type)
    milestones = None
    timeline_details: List[Dict[str, str]] = []
    if config:
        ground_up = config.get("ground_up", {})
        milestones = ground_up.get("milestones")

    timeline: Dict[str, str] = {}
    if isinstance(milestones, dict):
        iterable = milestones.items()
        for key, offset_months in iterable:
            milestone_date = _add_months(base_date, int(offset_months))
            timeline[key] = _month_to_quarter_string(milestone_date)
    elif isinstance(milestones, list):
        for entry in milestones:
            if not isinstance(entry, dict):
                continue
            milestone_id = entry.get("id") or entry.get("key")
            offset_value = entry.get("offset_months")
            if offset_value is None:
                offset_value = entry.get("month")
            if milestone_id is None or offset_value is None:
                continue
            milestone_date = _add_months(base_date, int(offset_value))
            quarter_label = _month_to_quarter_string(milestone_date)
            timeline[milestone_id] = quarter_label
            label = entry.get("label")
            if label:
                timeline_details.append({
                    "id": milestone_id,
                    "label": label,
                    "date": quarter_label,
                })
    else:
        defaults = {
            "groundbreaking": 0,
            "structure_complete": 8,
            "substantial_completion": 18,
            "grand_opening": 24,
        }
        for key, offset_months in defaults.items():
            milestone_date = _add_months(base_date, int(offset_months))
            timeline[key] = _month_to_quarter_string(milestone_date)

    if timeline_details:
        timeline["_details"] = timeline_details

    return timeline

class UnifiedEngine:
    def _normalize_project_class(self, value: Any) -> str:
        """
        Map various project_type/project_class inputs into the string values
        expected by ProjectClass enums (e.g. 'ground_up').
        """
        raw = value
        if isinstance(value, dict):
            raw = (
                value.get("project_type")
                or value.get("projectType")
                or value.get("project_class")
                or value.get("projectClass")
            )
        if not raw:
            return "ground_up"

        s = str(raw).strip().lower().replace("-", "_").replace(" ", "_")
        if s in ("groundup", "ground_up", "ground"):
            return "ground_up"
        if s in ("renovation", "reno", "remodel"):
            return "renovation"
        if s in ("addition", "add", "expansion"):
            return "addition"
        if s in ("tenant_improvement", "tenant", "ti"):
            return "tenant_improvement"
        return "ground_up"
    """
    One engine to rule them all.
    Single source of truth for all cost calculations.
    """
    
    def __init__(self):
        """Initialize the unified engine"""
        self.config = MASTER_CONFIG
        self.calculation_trace = []  # Track every calculation for debugging
        # self.financial_analyzer = FinancialAnalyzer()  # TODO: Add financial analyzer
        
    def calculate_project(self, 
                         building_type: BuildingType,
                         subtype: str,
                         square_footage: float,
                         location: str,
                         project_class: ProjectClass = ProjectClass.GROUND_UP,
                         floors: int = 1,
                         ownership_type: OwnershipType = OwnershipType.FOR_PROFIT,
                         finish_level: Optional[str] = None,
                         special_features: List[str] = None,
                         finish_level_source: Optional[str] = None,
                         parsed_input_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        The master calculation method.
        Everything goes through here.
        
        Args:
            building_type: Type from BuildingType enum
            subtype: Specific subtype (e.g., 'hospital', 'class_a')
            square_footage: Total square footage
            location: City/location for regional multiplier
            project_class: Ground-up, renovation, etc.
            floors: Number of floors
            ownership_type: For-profit, non-profit, etc.
            finish_level: Optional finish quality override
            special_features: List of special features to add
            finish_level_source: Trace provenance for finish level selection
            parsed_input_overrides: Optional parsed input dict for scope overrides
            
        Returns:
            Comprehensive cost breakdown dictionary
        """
        
        # Normalize project class input if provided as a raw string
        if isinstance(project_class, str):
            normalized_class = self._normalize_project_class(project_class)
            try:
                project_class = ProjectClass(normalized_class)
            except ValueError:
                project_class = ProjectClass.GROUND_UP
        self._log_trace("project_class_normalized", {
            'project_class': project_class.value if isinstance(project_class, ProjectClass) else str(project_class),
        })
        try:
            raw_project_type = None
            if isinstance(special_features, dict):  # not likely, but guard
                raw_project_type = special_features.get("project_type")
            if raw_project_type is None:
                raw_project_type = getattr(project_class, "value", project_class)
            print("[SpecSharp][UnifiedEngine] project_class=", raw_project_type)
        except Exception:
            pass

        # Clear trace for new calculation
        self.calculation_trace = []
        self._log_trace("calculation_start", {
            'building_type': building_type.value,
            'subtype': subtype,
            'square_footage': square_footage,
            'location': location
        })

        normalized_finish_level = finish_level.lower().strip() if isinstance(finish_level, str) and finish_level.strip() else None
        inferred_source = finish_level_source if finish_level_source in {'explicit', 'description', 'default'} else None

        if inferred_source == 'explicit':
            finish_source = 'explicit'
        elif inferred_source == 'description':
            finish_source = 'description'
        elif inferred_source == 'default':
            finish_source = 'default'
        elif normalized_finish_level:
            finish_source = 'explicit'
        else:
            finish_source = 'default'

        if not normalized_finish_level:
            normalized_finish_level = 'standard'

        self._log_trace("finish_level_source", {
            'source': finish_source,
            'finish_level': normalized_finish_level or 'standard'
        })
        quality_factor = resolve_quality_factor(normalized_finish_level, building_type, subtype)
        self._log_trace("quality_factor_resolved", {
            'finish_level': normalized_finish_level or 'standard',
            'quality_factor': round(quality_factor, 4)
        })

        city_only_warning_logged = False

        def _city_only_warning():
            nonlocal city_only_warning_logged
            if not city_only_warning_logged:
                self._log_trace("warning", {
                    'message': 'City-only location used default regional multiplier'
                })
                city_only_warning_logged = True
        
        # Get configuration
        if isinstance(subtype, dict):
            subtype = (
                subtype.get("id")
                or subtype.get("key")
                or subtype.get("value")
                or subtype.get("subtype")
            )
        logger.info(
            "[SUBTYPE_TRACE][engine_entry] building_type=%s subtype_raw=%s subtype_normalized=%s",
            getattr(building_type, "value", building_type),
            subtype,
            (subtype.lower().strip() if isinstance(subtype, str) else subtype),
        )
        building_config = get_building_config(building_type, subtype)
        if not building_config:
            raise ValueError(f"No configuration found for {building_type.value}/{subtype}")
        
        # Validate and adjust project class if incompatible
        original_class = project_class
        project_class = validate_project_class(building_type, subtype, project_class)
        if project_class != original_class:
            self._log_trace("project_class_adjusted", {
                'original': original_class.value,
                'adjusted': project_class.value,
                'reason': 'Incompatible with building type'
            })
        
        # Base construction cost calculation with finish level adjustment
        original_base_cost_per_sf = building_config.base_cost_per_sf

        # Height premium for office towers: add modest multipliers for taller structures
        height_factor = 1.0
        if building_type == BuildingType.OFFICE:
            try:
                floor_count = int(floors or building_config.typical_floors or 1)
            except (TypeError, ValueError):
                floor_count = 1

            extra_premium = 0.0
            if floor_count > 4:
                extra_premium += max(0, min(floor_count, 8) - 4) * 0.02  # 2% per floor from 5-8
            if floor_count > 8:
                extra_premium += max(0, min(floor_count, 12) - 8) * 0.01  # 1% per floor from 9-12

            height_factor = 1.0 + min(extra_premium, 0.20)  # Cap at +20%

        base_cost_per_sf = original_base_cost_per_sf * height_factor
        self._log_trace("base_cost_retrieved", {
            'base_cost_per_sf': original_base_cost_per_sf,
            'quality_factor': round(quality_factor, 4),
            'height_factor': round(height_factor, 4),
            'adjusted_base_cost_per_sf': round(base_cost_per_sf, 4)
        })
        
        # Apply project class multiplier (treated as complexity factor)
        class_multiplier = PROJECT_CLASS_MULTIPLIERS[project_class]
        complexity_factor = class_multiplier
        cost_after_complexity = base_cost_per_sf * complexity_factor
        self._log_trace("project_class_multiplier_applied", {
            'multiplier': complexity_factor,
            'adjusted_cost_per_sf': round(cost_after_complexity, 4)
        })

        modifiers = get_effective_modifiers(
            building_type,
            subtype,
            normalized_finish_level,
            location,
            warning_callback=_city_only_warning
        )
        margin_pct_override = None
        try:
            cfg_margin = getattr(building_config, 'operating_margin_base', None)
            if cfg_margin is not None:
                margin_pct_override = float(cfg_margin)
        except (TypeError, ValueError):
            margin_pct_override = None
        if (
            building_type == BuildingType.HEALTHCARE
            and subtype == 'medical_office'
            and margin_pct_override is not None
        ):
            modifiers = {**modifiers, 'margin_pct': margin_pct_override}

        self._log_trace("finish_cost_applied", {
            'finish_level': normalized_finish_level or 'standard',
            'factor': round(modifiers.get('finish_cost_factor', 1.0), 4)
        })

        finish_cost_factor = modifiers.get('finish_cost_factor', 1.0)
        if not finish_cost_factor:
            finish_cost_factor = 1.0
        cost_factor = modifiers['cost_factor']
        if finish_cost_factor:
            regional_multiplier_effective = cost_factor / finish_cost_factor
        else:
            regional_multiplier_effective = cost_factor

        cost_after_regional = cost_after_complexity * regional_multiplier_effective
        regional_context = resolve_location_context(location)
        final_cost_per_sf = cost_after_regional * finish_cost_factor
        self._log_trace("modifiers_applied", {
            'finish_level': normalized_finish_level or 'standard',
            'cost_factor': round(cost_factor, 4),
            'regional_multiplier': round(regional_multiplier_effective, 4),
            'revenue_factor': round(modifiers['revenue_factor'], 4),
            'margin_pct': round(modifiers['margin_pct'], 4)
        })
        
        # Calculate base construction cost
        construction_cost = final_cost_per_sf * square_footage
        
        # Calculate equipment cost with finish/regional adjustments
        equipment_multiplier = modifiers.get('finish_cost_factor', 1.0)
        equipment_cost = building_config.equipment_cost_per_sf * equipment_multiplier * square_footage
        
        # Add special features if any
        special_features_cost = 0
        if special_features and building_config.special_features:
            for feature in special_features:
                if isinstance(feature, dict):
                    continue
                if feature in building_config.special_features:
                    feature_cost = building_config.special_features[feature] * square_footage
                    special_features_cost += feature_cost
                    self._log_trace("special_feature_applied", {
                        'feature': feature,
                        'cost_per_sf': building_config.special_features[feature],
                        'total_cost': feature_cost
                    })
        
        # Calculate trade breakdown
        trades = self._calculate_trades(construction_cost, building_config.trades)
        
        # Build scope items (per trade) where supported
        scope_context = self._resolve_scope_context(special_features)
        def _extract_scenario_key(source: Optional[Dict[str, Any]]) -> Optional[str]:
            if not isinstance(source, dict):
                return None
            for key in ("scenario", "scenario_key", "scenarioName", "scenarioKey"):
                value = source.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip().lower()
            nested = source.get('__parsed_input__')
            if isinstance(nested, dict):
                nested_value = _extract_scenario_key(nested)
                if nested_value:
                    return nested_value
            parsed_nested = source.get('parsed_input') or source.get('parsedInput')
            if isinstance(parsed_nested, dict):
                nested_value = _extract_scenario_key(parsed_nested)
                if nested_value:
                    return nested_value
            return None
        scenario_key = None
        for candidate in (parsed_input_overrides, scope_context):
            scenario_key = _extract_scenario_key(candidate)
            if scenario_key:
                break
        scenario_key_normalized = (scenario_key or '').strip().lower() if scenario_key else None
        if isinstance(parsed_input_overrides, dict):
            # Merge parsed_input so explicit overrides (e.g. dock_doors) are honored downstream
            scope_context = {**(scope_context or {}), **parsed_input_overrides}
        scope_items = self._build_scope_items(
            building_type=building_type,
            subtype=subtype,
            trades=trades,
            square_footage=square_footage,
            scope_context=scope_context
        )

        # Apply flex-specific finishes delta to rollups so office uplift affects totals
        if building_type == BuildingType.INDUSTRIAL:
            subtype_value = subtype.value if hasattr(subtype, "value") else subtype
            subtype_key = (subtype_value or "").lower().strip() if isinstance(subtype_value, str) else str(subtype_value or "").lower().strip()
            if subtype_key == "flex_space":
                finishes_item = next((item for item in scope_items if item.get("trade") == "Finishes"), None)
                systems = finishes_item.get("systems", []) if isinstance(finishes_item, dict) else []
                finishes_total_effective = sum(float(system.get("total_cost", 0.0) or 0.0) for system in systems)
                baseline_finishes = float(trades.get("finishes", 0.0) or 0.0)
                if finishes_total_effective > 0 and finishes_total_effective != baseline_finishes:
                    delta = finishes_total_effective - baseline_finishes
                    trades["finishes"] = finishes_total_effective
                    construction_cost += delta
                    if square_footage > 0:
                        final_cost_per_sf = construction_cost / square_footage

        # Calculate soft costs (after any flex adjustments)
        soft_costs = self._calculate_soft_costs(construction_cost, building_config.soft_costs)
        
        # For healthcare facilities, equipment is a soft cost (medical equipment)
        # For other building types, it's part of hard costs
        if building_type == BuildingType.HEALTHCARE:
            soft_costs['medical_equipment'] = equipment_cost
            total_hard_costs = construction_cost + special_features_cost
            total_soft_costs = sum(soft_costs.values())
        else:
            total_hard_costs = construction_cost + equipment_cost + special_features_cost
            total_soft_costs = sum(soft_costs.values())
        
        total_project_cost = total_hard_costs + total_soft_costs
        
        # Validate restaurant costs are within reasonable ranges
        if building_type == BuildingType.RESTAURANT:
            cost_per_sf = total_project_cost / square_footage
            min_cost = 250  # Minimum reasonable restaurant cost
            max_cost = 700  # Maximum reasonable restaurant cost (except fine dining)
            
            if cost_per_sf < min_cost:
                self._log_trace("restaurant_cost_clamp", {
                    'mode': 'minimum',
                    'original_cost_per_sf': cost_per_sf,
                    'target_cost_per_sf': min_cost
                })
                # Adjust costs proportionally
                adjustment_factor = (min_cost * square_footage) / total_project_cost
                total_hard_costs *= adjustment_factor
                total_soft_costs *= adjustment_factor
                total_project_cost = min_cost * square_footage
            elif cost_per_sf > max_cost and subtype != 'fine_dining':
                self._log_trace("restaurant_cost_clamp", {
                    'mode': 'maximum',
                    'original_cost_per_sf': cost_per_sf,
                    'target_cost_per_sf': max_cost
                })
                # Cap costs proportionally
                adjustment_factor = (max_cost * square_footage) / total_project_cost
                total_hard_costs *= adjustment_factor
                total_soft_costs *= adjustment_factor
                total_project_cost = max_cost * square_footage
        
        # Calculate ownership/financing analysis with enhanced financial metrics
        ownership_analysis = None
        revenue_data = None
        flex_revenue_per_sf = None
        if ownership_type in building_config.ownership_types:
            # Calculate comprehensive revenue analysis using master_config
            revenue_data = self.calculate_ownership_analysis({
                'building_type': building_type.value,
                'subtype': subtype,
                'square_footage': square_footage,
                'total_cost': total_project_cost,
                'subtotal': construction_cost,  # Construction cost before contingency
                'modifiers': modifiers,
                'quality_factor': quality_factor,
                'finish_level': normalized_finish_level,
                'regional_context': regional_context,
                'location': location,
                'scenario': scenario_key,
            })

            # Get basic ownership metrics (prefer revenue-derived NOI when available)
            revenue_analysis_for_financing = revenue_data.get('revenue_analysis') if revenue_data else None
            if revenue_data:
                flex_metric = revenue_data.get('flex_revenue_per_sf')
                if isinstance(flex_metric, (int, float)):
                    flex_revenue_per_sf = flex_metric
            ownership_analysis = self._calculate_ownership(
                total_project_cost,
                building_config.ownership_types[ownership_type],
                revenue_analysis=revenue_analysis_for_financing
            )
            
            # Merge revenue analysis into ownership analysis
            if revenue_data and 'revenue_analysis' in revenue_data:
                ownership_analysis['revenue_analysis'] = revenue_data['revenue_analysis']
                ownership_analysis['return_metrics'].update(revenue_data['return_metrics'])
                ownership_analysis['roi_analysis'] = {
                    'financial_metrics': {
                        'annual_revenue': revenue_data['revenue_analysis']['annual_revenue'],
                        'operating_margin': revenue_data['revenue_analysis']['operating_margin'],
                        'net_income': revenue_data['revenue_analysis']['net_income']
                    }
                }
                # Add the new metrics from our enhanced analysis
                ownership_analysis['revenue_requirements'] = revenue_data.get('revenue_requirements', {})
                ownership_analysis['operational_efficiency'] = revenue_data.get('operational_efficiency', {})
                ownership_analysis['operational_metrics'] = revenue_data.get('operational_metrics', {})
                if 'sensitivity_analysis' in revenue_data:
                    ownership_analysis['sensitivity_analysis'] = revenue_data.get('sensitivity_analysis')
                if 'yield_on_cost' in revenue_data:
                    ownership_analysis['yield_on_cost'] = revenue_data.get('yield_on_cost')
                if 'market_cap_rate' in revenue_data:
                    ownership_analysis['market_cap_rate'] = revenue_data.get('market_cap_rate')
                if 'cap_rate_spread_bps' in revenue_data:
                    ownership_analysis['cap_rate_spread_bps'] = revenue_data.get('cap_rate_spread_bps')
                
                actual_noi = (
                    revenue_data.get('return_metrics', {}).get('estimated_annual_noi')
                    or revenue_data['revenue_analysis'].get('net_income')
                )
                debt_metrics = ownership_analysis.get('debt_metrics') or {}
                annual_debt_service = debt_metrics.get('annual_debt_service', 0)
                if actual_noi is not None:
                    recalculated_dscr = actual_noi / annual_debt_service if annual_debt_service else 0
                    debt_metrics['calculated_dscr'] = recalculated_dscr
                    debt_metrics['dscr_meets_target'] = recalculated_dscr >= debt_metrics.get('target_dscr', 0)
                    ownership_analysis['debt_metrics'] = debt_metrics
                    ownership_analysis['return_metrics']['estimated_annual_noi'] = actual_noi
                    self._log_trace("dscr_recalculated_from_revenue", {
                        'actual_noi': actual_noi,
                        'annual_debt_service': annual_debt_service,
                        'calculated_dscr': recalculated_dscr
                    })
        
        # Financial requirements removed - was only partially implemented for hospital
        
        # Generate cost DNA for transparency
        cost_dna = {
            'base_cost': base_cost_per_sf,
            'finish_adjustment': finish_cost_factor,
            'regional_adjustment': regional_multiplier_effective,
            'complexity_factor': complexity_factor,
            'final_cost': final_cost_per_sf,
            'location': location,
            'market_name': location.split(',')[0] if location else 'Nashville',  # Extract city name
            'building_type': building_type.value if hasattr(building_type, 'value') else str(building_type),
            'subtype': subtype,
            'detected_factors': [],  # Will be populated with special features
            'applied_adjustments': {
                'base': base_cost_per_sf,
                'after_finish': cost_after_complexity,
                'after_class': cost_after_complexity,
                'after_complexity': cost_after_complexity,
                'after_finish_factor': final_cost_per_sf,
                'after_regional': cost_after_regional,
                'final': final_cost_per_sf
            },
            'market_context': {
                'market': location.split(',')[0] if location else 'Nashville',
                'index': modifiers.get('market_factor', 1.0),
                'comparison': 'above national average' if modifiers.get('market_factor', 1.0) > 1.0 else 'below national average' if modifiers.get('market_factor', 1.0) < 1.0 else 'at national average',
                'percentage_difference': round((modifiers.get('market_factor', 1.0) - 1.0) * 100, 1)
            }
        }
        
        # Add special features if present
        if special_features:
            cost_dna['detected_factors'] = list(special_features) if isinstance(special_features, (list, dict)) else [special_features]

        cost_build_up = [
            {
                'label': 'Base Cost',
                'value_per_sf': base_cost_per_sf
            },
            {
                'label': 'Regional',
                'multiplier': regional_multiplier_effective
            },
            {
                'label': 'Complexity',
                'multiplier': complexity_factor
            }
        ]

        display_finish_level = (normalized_finish_level or 'standard').lower()
        if display_finish_level != 'standard':
            cost_build_up.append({
                'label': 'Finish Level',
                'multiplier': finish_cost_factor
            })
        
        # Ensure the build-up array always has something meaningful so frontend visuals don't break
        fallback_cost_build_up = cost_build_up if cost_build_up else [
            {'label': 'Base Cost', 'value_per_sf': original_base_cost_per_sf},
            {'label': 'Regional', 'multiplier': regional_multiplier_effective},
            {'label': 'Complexity', 'multiplier': complexity_factor},
        ]
        if not cost_build_up and display_finish_level != 'standard':
            fallback_cost_build_up.append({'label': 'Finish Level', 'multiplier': finish_cost_factor})

        profile = get_building_profile(building_type)

        # Surface sensitivity analysis for frontend quick sensitivity tiles
        sensitivity_analysis = None
        if ownership_analysis and isinstance(ownership_analysis, dict):
            # For healthcare (outpatient / urgent care) this will contain a base object
            # and a scenarios list. For other types it may be missing or None.
            sensitivity_analysis = ownership_analysis.get('sensitivity_analysis')

        city_value = regional_context.get('city')
        state_value = regional_context.get('state')
        pretty_location = None
        if city_value and state_value:
            pretty_location = f"{city_value.title()}, {state_value}"
        elif city_value:
            pretty_location = city_value.title()
        regional_cost_factor = regional_context.get('cost_factor')
        regional_market_factor = regional_context.get('market_factor', 1.0)
        regional_payload = {
            'city': city_value.title() if city_value else None,
            'state': state_value,
            'source': regional_context.get('source'),
            'multiplier': regional_multiplier_effective,
            'cost_factor': regional_cost_factor if regional_cost_factor is not None else regional_multiplier_effective,
            'market_factor': regional_market_factor,
            'location_display': pretty_location or regional_context.get('location_display') or location
        }

        # Build comprehensive response - FLATTENED structure to match frontend expectations
        totals_payload = {
            'hard_costs': total_hard_costs,
            'soft_costs': total_soft_costs,
            'total_project_cost': total_project_cost,
            'cost_per_sf': total_project_cost / square_footage if square_footage > 0 else 0
        }
        if scenario_key:
            totals_payload['scenario_key'] = scenario_key

        if (
            flex_revenue_per_sf is not None
            and building_type == BuildingType.INDUSTRIAL
            and isinstance(subtype, str)
            and subtype.strip().lower() == 'flex_space'
            and square_footage > 0
        ):
            totals_payload['revenue_per_sf'] = flex_revenue_per_sf
            totals_payload['annual_revenue'] = flex_revenue_per_sf * float(square_footage)

        result = {
            'project_info': {
                'building_type': building_type.value,
                'subtype': subtype,
                'display_name': building_config.display_name,
                'project_class': project_class.value,
                'square_footage': square_footage,
                'location': location,
                'floors': floors,
                'typical_floors': building_config.typical_floors,
                'finish_level': normalized_finish_level or 'standard',
                'finish_level_source': finish_source,
                'available_special_features': list(building_config.special_features.keys()) if building_config.special_features else []
            },
            'profile': {
                'building_type': building_type.value,
                'market_cap_rate': profile.get('market_cap_rate'),
                'target_yield': profile.get('target_yield'),
                'target_dscr': profile.get('target_dscr'),
            },
            'modifiers': modifiers,
            'regional': regional_payload,
            # Flatten calculations to top level to match frontend CalculationResult interface
            'construction_costs': {
                'base_cost_per_sf': base_cost_per_sf,
                'original_base_cost_per_sf': original_base_cost_per_sf,
                'class_multiplier': class_multiplier,
                'regional_multiplier': regional_multiplier_effective,
                'finish_cost_factor': finish_cost_factor,
                'cost_factor': cost_factor,
                'quality_factor': quality_factor,
                'final_cost_per_sf': final_cost_per_sf,
                'construction_total': construction_cost,
                'equipment_total': equipment_cost,
                'special_features_total': special_features_cost,
                'cost_build_up': fallback_cost_build_up
            },
            'cost_dna': cost_dna,  # Add cost DNA for transparency
            'trade_breakdown': trades,
            'scope_items': scope_items,
            'soft_costs': soft_costs,
            'totals': totals_payload,
            'ownership_analysis': ownership_analysis,
            # Add revenue_analysis at top level for easy access
            'revenue_analysis': ownership_analysis.get('revenue_analysis', {}) if ownership_analysis else {},
            # Add revenue_requirements at top level for easy access
            'revenue_requirements': ownership_analysis.get('revenue_requirements', {}) if ownership_analysis else {},
            # Add roi_analysis at top level for frontend compatibility
            'roi_analysis': ownership_analysis.get('roi_analysis', {}) if ownership_analysis else {},
            # Add operational efficiency at top level
            'operational_efficiency': ownership_analysis.get('operational_efficiency', {}) if ownership_analysis else {},
            # Add return metrics at top level for investment visibility
            'return_metrics': ownership_analysis.get('return_metrics', {}) if ownership_analysis else {},
            # Add roi metrics at top level for investment analysis
            'roi_metrics': ownership_analysis.get('roi_metrics', {}) if ownership_analysis else {},
            # Add department and operational metrics at top level for easy frontend access
            'department_allocation': ownership_analysis.get('department_allocation', []) if ownership_analysis else [],
            'operational_metrics': ownership_analysis.get('operational_metrics', {}) if ownership_analysis else {},
            # Expose sensitivity analysis at the top level for the v2 frontend
            'sensitivity_analysis': sensitivity_analysis,
            'regional_applied': True,
            'calculation_trace': self.calculation_trace,
            'timestamp': datetime.now().isoformat()
        }

        revenue_block = result.get('revenue_analysis')
        if isinstance(revenue_block, dict):
            revenue_block.setdefault('market_factor', regional_market_factor)
        if ownership_analysis and isinstance(ownership_analysis, dict):
            nested_revenue = ownership_analysis.get('revenue_analysis')
            if isinstance(nested_revenue, dict):
                nested_revenue.setdefault('market_factor', regional_market_factor)

        facility_metrics_payload = None
        if building_type == BuildingType.RESTAURANT:
            total_sf = float(square_footage) if square_footage else 0.0
            revenue_block = result.get('revenue_analysis') or {}
            return_block = result.get('return_metrics') or {}
            totals_block = result.get('totals') or {}
            annual_revenue_value = revenue_block.get('annual_revenue')
            annual_noi_value = return_block.get('estimated_annual_noi')
            total_cost_value = totals_block.get('total_project_cost')

            def _per_sf(value: Optional[float]) -> float:
                if not value or not total_sf:
                    return 0.0
                try:
                    return float(value) / float(total_sf)
                except (TypeError, ZeroDivisionError):
                    return 0.0

            facility_metrics_payload = {
                'type': 'restaurant',
                'metrics': [
                    {
                        'id': 'sales_per_sf',
                        'label': 'Sales per SF',
                        'value': _per_sf(annual_revenue_value),
                        'unit': '$/SF'
                    },
                    {
                        'id': 'noi_per_sf',
                        'label': 'NOI per SF',
                        'value': _per_sf(annual_noi_value),
                        'unit': '$/SF'
                    },
                    {
                        'id': 'cost_per_sf',
                        'label': 'All-in Cost per SF',
                        'value': _per_sf(total_cost_value),
                        'unit': '$/SF'
                    }
                ],
                'total_square_feet': total_sf
            }
        elif building_type == BuildingType.HEALTHCARE and subtype in ('outpatient_clinic', 'urgent_care', 'imaging_center', 'surgical_center', 'medical_office', 'dental_office'):
            financial_metrics_cfg = getattr(building_config, 'financial_metrics', {}) or {}
            units_per_sf_value = financial_metrics_cfg.get('units_per_sf')
            primary_unit_label = financial_metrics_cfg.get('primary_unit', 'Units')
            revenue_per_unit_cfg = financial_metrics_cfg.get('revenue_per_unit_annual')
            computed_units = 0
            if units_per_sf_value and square_footage:
                try:
                    computed_units = max(1, int(round(float(square_footage) * float(units_per_sf_value))))
                except (TypeError, ValueError):
                    computed_units = 1
            if computed_units <= 0:
                computed_units = 1
            cost_per_unit = total_project_cost / computed_units if computed_units else 0
            revenue_per_unit = revenue_per_unit_cfg if revenue_per_unit_cfg else (
                annual_revenue / computed_units if computed_units else 0
            )
            facility_metrics_payload = {
                'type': 'healthcare',
                'units': computed_units,
                'unit_label': primary_unit_label,
                'cost_per_unit': cost_per_unit,
                'revenue_per_unit': revenue_per_unit
            }

        if facility_metrics_payload:
            result['facility_metrics'] = facility_metrics_payload
        
        # Financial requirements removed - was only partially implemented
        
        self._log_trace("calculation_end", {
            'total_project_cost': total_project_cost,
            'cost_per_sf': total_project_cost / square_footage
        })

        try:
            building_type_name = building_type.name if hasattr(building_type, 'name') else str(building_type)
        except Exception:
            building_type_name = str(building_type)
        if isinstance(building_type_name, str) and (
            'HOSPITALITY' in building_type_name.upper() or 'HOTEL' in building_type_name.upper()
        ):
            hospitality_metrics = None
            if revenue_data and isinstance(revenue_data, dict):
                hospitality_metrics = revenue_data.get('hospitality_financials')
            if not hospitality_metrics and ownership_analysis:
                hospitality_metrics = ownership_analysis.get('hospitality_financials')
            if not hospitality_metrics:
                hospitality_metrics = result.get('hospitality_financials')
            if hospitality_metrics:
                key_map = {
                    'rooms': 'rooms',
                    'adr': 'adr',
                    'occupancy': 'occupancy',
                    'revpar': 'revpar',
                    'cost_per_key': 'cost_per_key'
                }
                for source_key, dest_key in key_map.items():
                    metric_value = hospitality_metrics.get(source_key)
                    if metric_value is None:
                        continue
                    try:
                        result[dest_key] = float(metric_value)
                    except (TypeError, ValueError):
                        result[dest_key] = metric_value
                if 'cost_per_key' not in result or result['cost_per_key'] in (None, 0):
                    rooms_metric = hospitality_metrics.get('rooms') or result.get('rooms')
                    if rooms_metric not in (None, 0):
                        try:
                            result['cost_per_key'] = float(total_project_cost) / float(rooms_metric)
                        except (TypeError, ValueError, ZeroDivisionError):
                            pass
                result['hospitality_financials'] = hospitality_metrics
        
        return result
    
    def _calculate_trades(self, construction_cost: float, trades_config: Any) -> Dict[str, float]:
        """Calculate trade breakdown costs"""
        trades = {}
        trades_dict = asdict(trades_config)
        
        for trade, percentage in trades_dict.items():
            trades[trade] = construction_cost * percentage
            
        self._log_trace("trade_breakdown_calculated", {
            'total': construction_cost,
            'trades': len(trades)
        })
        
        return trades
    
    def _calculate_soft_costs(self, construction_cost: float, soft_costs_config: Any) -> Dict[str, float]:
        """Calculate soft costs"""
        soft_costs = {}
        soft_costs_dict = asdict(soft_costs_config)
        
        for cost_type, rate in soft_costs_dict.items():
            soft_costs[cost_type] = construction_cost * rate
            
        self._log_trace("soft_costs_calculated", {
            'base': construction_cost,
            'total_soft': sum(soft_costs.values())
        })
        
        return soft_costs
    
    def _resolve_scope_context(self, special_features: Optional[Any]) -> Optional[Dict[str, Any]]:
        """
        Attempt to derive a context dictionary for scope generation overrides.
        Accepts dict-like special_features or any embedded dicts within the list.
        """
        context: Dict[str, Any] = {}
        
        if isinstance(special_features, dict):
            context.update(special_features)
            nested = special_features.get("__parsed_input__")
            if isinstance(nested, dict):
                context.update(nested)
        elif isinstance(special_features, list):
            for feature in special_features:
                if isinstance(feature, dict):
                    context.update(feature)
                    nested = feature.get("__parsed_input__")
                    if isinstance(nested, dict):
                        context.update(nested)
        
        return context or None

    def _build_scope_items(
        self,
        building_type: BuildingType,
        subtype: str,
        trades: Dict[str, float],
        square_footage: float,
        scope_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Build a simple, deterministic scope_items structure from the trade breakdown.
        For now, we only generate rich scope for industrial warehouses.
        """
        scope_items: List[Dict[str, Any]] = []

        if not trades or square_footage <= 0:
            return scope_items

        subtype_key = (subtype or "").lower().strip()

        industrial_shell_subtypes = {
            "warehouse",
            "distribution_warehouse",
            "distribution_center",
            "class_a_distribution_warehouse",
            "class_a_distribution",
            "flex_space",
            "cold_storage",
        }

        if building_type == BuildingType.INDUSTRIAL and subtype_key in industrial_shell_subtypes:
            sf = float(square_footage)
            is_flex = subtype_key == "flex_space"
            is_cold_storage = subtype_key == "cold_storage"

            def _safe_unit_cost(total: float, qty: float) -> float:
                if not qty:
                    return 0.0
                try:
                    return float(total) / float(qty)
                except (TypeError, ValueError, ZeroDivisionError):
                    return 0.0
            
            override_sources: List[Dict[str, Any]] = []
            if isinstance(scope_context, dict):
                override_sources.append(scope_context)
                potential_nested_keys = [
                    "parsed_input",
                    "parsedInput",
                    "request_data",
                    "requestData",
                    "input_overrides",
                    "overrides",
                    "scope_overrides",
                    "context",
                ]
                for key in potential_nested_keys:
                    nested_value = scope_context.get(key)
                    if isinstance(nested_value, dict):
                        override_sources.append(nested_value)
                calculations_ctx = scope_context.get("calculations") if isinstance(scope_context, dict) else None
                if isinstance(calculations_ctx, dict):
                    for calc_key in ("parsed_input", "parsedInput", "request_data", "requestData"):
                        calc_nested = calculations_ctx.get(calc_key)
                        if isinstance(calc_nested, dict):
                            override_sources.append(calc_nested)

            def _scope_has_keyword(value: Any, keyword_parts: List[str]) -> bool:
                if not value:
                    return False
                if isinstance(value, str):
                    lowered = value.lower()
                    return all(part in lowered for part in keyword_parts)
                if isinstance(value, list):
                    return any(_scope_has_keyword(item, keyword_parts) for item in value)
                if isinstance(value, dict):
                    return any(_scope_has_keyword(item, keyword_parts) for item in value.values())
                return False

            has_blast_freezer_feature = _scope_has_keyword(scope_context, ["blast", "freezer"])

            office_sf = 0.0
            warehouse_sf_for_flex = None

            def _coerce_number(value: Any) -> Optional[float]:
                if value is None:
                    return None
                if isinstance(value, bool):
                    return float(value)
                if isinstance(value, (int, float)):
                    return float(value)
                if isinstance(value, str):
                    stripped = value.strip()
                    if not stripped:
                        return None
                    cleaned = stripped.replace('%', '').replace(',', '')
                    try:
                        return float(cleaned)
                    except ValueError:
                        return None
                return None

            def _get_override(keys: List[str]) -> Optional[float]:
                for source in override_sources:
                    for key in keys:
                        if key in source:
                            number = _coerce_number(source.get(key))
                            if number is not None:
                                return number
                return None

            def _get_percent_override(keys: List[str]) -> Optional[float]:
                value = _get_override(keys)
                if value is None:
                    return None
                percent = float(value)
                if percent > 1.0:
                    percent = percent / 100.0
                return max(percent, 0.0)

            if is_flex:
                office_share_override = _get_percent_override([
                    "office_share",
                    "officeShare",
                    "office_split",
                    "officeSplit",
                ])
                if office_share_override is None:
                    office_share_value = 0.0
                else:
                    office_share_value = float(office_share_override)
                office_share_value = max(0.0, min(1.0, office_share_value))
                total_sf = float(sf)
                office_sf = round(total_sf * office_share_value, 2)
                warehouse_sf_for_flex = round(total_sf - office_sf, 2)
            else:
                office_sf_override = _get_override([
                    "office_sf",
                    "officeSquareFeet",
                    "office_space_sf",
                ])
                if office_sf_override is not None:
                    office_sf = max(0.0, float(office_sf_override))
                else:
                    office_pct_override = _get_percent_override([
                        "office_percent",
                        "office_pct",
                        "officePercent",
                        "officePct",
                    ])
                    if office_pct_override is not None:
                        office_sf = max(0.0, sf * office_pct_override)
                    else:
                        office_sf = max(1500.0, sf * 0.05)

            mezz_sf_override = _get_override([
                "mezzanine_sf",
                "mezz_sf",
                "mezzanineSquareFeet",
            ])
            if mezz_sf_override is not None:
                mezz_sf = max(0.0, float(mezz_sf_override))
            else:
                mezz_pct_override = _get_percent_override([
                    "mezzanine_percent",
                    "mezzanine_pct",
                    "mezzaninePercent",
                    "mezzaninePct",
                ])
                if mezz_pct_override is not None:
                    mezz_sf = max(0.0, sf * mezz_pct_override)
                else:
                    mezz_sf = 0.0

            dock_override = _get_override([
                "dock_doors",
                "dock_count",
                "dockDoors",
                "dockCount",
            ])
            if is_flex:
                dock_count = None
                if dock_override is not None:
                    dock_count = max(0, int(round(dock_override)))
            else:
                print(
                    "[SPECSHARP DEBUG][WAREHOUSE DOCKS]",
                    {
                        "ctx_dock_doors": scope_context.get("dock_doors") if scope_context else None,
                        "ctx_dock_count": scope_context.get("dock_count") if scope_context else None,
                        "sf": sf,
                    }
                )
                if dock_override is not None:
                    dock_count = max(0, int(round(dock_override)))
                else:
                    dock_count = max(4, int(round(sf / 10000.0)))
                print(
                    "[SPECSHARP DEBUG][WAREHOUSE DOCKS FINAL]",
                    {
                        "final_dock_count": dock_count
                    }
                )

            restroom_groups = max(1, int(round(sf / 25000.0)))

            structural_total = float(trades.get("structural", 0.0) or 0.0)
            if structural_total > 0:
                if is_flex:
                    include_docks = bool(dock_count and dock_count > 0)
                    slab_share = 0.45
                    shell_share = 0.25
                    foundations_share = 0.10
                    dock_share = 0.20 if include_docks else 0.0

                    if not include_docks:
                        base_total = slab_share + shell_share + foundations_share
                        if base_total > 0:
                            scale = 1.0 / base_total
                            slab_share *= scale
                            shell_share *= scale
                            foundations_share *= scale
                    mezz_share = 0.0

                    slab_total = structural_total * slab_share
                    shell_total = structural_total * shell_share
                    foundations_total = structural_total * foundations_share
                    docks_total = structural_total * dock_share if include_docks else 0.0

                    structural_systems = [
                        {
                            "name": 'Concrete slab on grade (6")',
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": _safe_unit_cost(slab_total, sf),
                            "total_cost": slab_total,
                        },
                        {
                            "name": "Tilt-wall panels / structural shell",
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": _safe_unit_cost(shell_total, sf),
                            "total_cost": shell_total,
                        },
                        {
                            "name": "Foundations, footings, and thickened slabs",
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": _safe_unit_cost(foundations_total, sf),
                            "total_cost": foundations_total,
                        },
                    ]

                    if include_docks and dock_count:
                        structural_systems.append({
                            "name": "Dock pits and loading aprons",
                            "quantity": dock_count,
                            "unit": "EA",
                            "unit_cost": _safe_unit_cost(docks_total, dock_count),
                            "total_cost": docks_total,
                        })

                    scope_items.append({
                        "trade": "Structural",
                        "systems": structural_systems,
                    })
                elif is_cold_storage:
                    structural_entries = [
                        ('Concrete slab on grade (conceptual)', 0.4),
                        ('Foundations & thickened slabs (conceptual)', 0.3),
                        ('Structural shell (conceptual)', 0.3),
                    ]
                    structural_systems = []
                    total_share = sum(entry[1] for entry in structural_entries)
                    for name, share in structural_entries:
                        portion = structural_total * (share / total_share if total_share else 0)
                        structural_systems.append({
                            "name": name,
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": _safe_unit_cost(portion, sf),
                            "total_cost": portion,
                            "notes": "Conceptual / pre-design"
                        })

                    scope_items.append({
                        "trade": "Structural",
                        "systems": structural_systems,
                    })
                else:
                    slab_share = 0.45
                    shell_share = 0.25
                    foundations_share = 0.10
                    dock_share = 0.20

                    if mezz_sf > 0:
                        mezz_share = 0.10
                        base_total = slab_share + shell_share + foundations_share + dock_share
                        scale = (1.0 - mezz_share) / base_total
                        slab_share *= scale
                        shell_share *= scale
                        foundations_share *= scale
                        dock_share *= scale
                    else:
                        mezz_share = 0.0

                    slab_total = structural_total * slab_share
                    shell_total = structural_total * shell_share
                    foundations_total = structural_total * foundations_share
                    docks_total = structural_total * dock_share
                    mezz_total = structural_total * mezz_share

                    structural_systems = [
                        {
                            "name": 'Concrete slab on grade (6")',
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": _safe_unit_cost(slab_total, sf),
                            "total_cost": slab_total,
                        },
                        {
                            "name": "Tilt-wall panels / structural shell",
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": _safe_unit_cost(shell_total, sf),
                            "total_cost": shell_total,
                        },
                        {
                            "name": "Foundations, footings, and thickened slabs",
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": _safe_unit_cost(foundations_total, sf),
                            "total_cost": foundations_total,
                        },
                        {
                            "name": "Dock pits and loading aprons",
                            "quantity": dock_count,
                            "unit": "EA",
                            "unit_cost": _safe_unit_cost(docks_total, dock_count),
                            "total_cost": docks_total,
                        },
                    ]

                    if mezz_sf > 0 and mezz_total > 0:
                        structural_systems.append({
                            "name": "Mezzanine structure (framing, deck, stairs)",
                            "quantity": mezz_sf,
                            "unit": "SF",
                            "unit_cost": _safe_unit_cost(mezz_total, mezz_sf),
                            "total_cost": mezz_total,
                        })

                    scope_items.append({
                        "trade": "Structural",
                        "systems": structural_systems,
                    })

            mechanical_total = float(trades.get("mechanical", 0.0) or 0.0)
            if mechanical_total > 0:
                if is_cold_storage:
                    mechanical_entries: List[Tuple[str, float]] = [
                        ("Industrial refrigeration system (conceptual)", 0.45),
                        ("Evaporators & condensers (conceptual)", 0.30),
                        ("Temperature zone controls (conceptual)", 0.25),
                    ]
                    if has_blast_freezer_feature:
                        mechanical_entries.append(("Blast freezer systems (conceptual)", 0.20))
                    total_share = sum(entry[1] for entry in mechanical_entries)
                    mechanical_systems = []
                    for name, share in mechanical_entries:
                        portion = mechanical_total * (share / total_share if total_share else 0)
                        mechanical_systems.append({
                            "name": name,
                            "quantity": 1,
                            "unit": "LS",
                            "unit_cost": _safe_unit_cost(portion, 1),
                            "total_cost": portion,
                            "notes": "Conceptual / pre-design"
                        })
                    scope_items.append({
                        "trade": "Mechanical",
                        "systems": mechanical_systems,
                    })
                else:
                    rtu_count = max(1, int(round(sf / 15000.0)))
                    exhaust_fans = max(1, int(round(sf / 40000.0)))

                    rtu_share = 0.50
                    exhaust_share = 0.20
                    distribution_share = 0.30

                    rtu_total = mechanical_total * rtu_share
                    exhaust_total = mechanical_total * exhaust_share
                    distribution_total = mechanical_total * distribution_share

                    mechanical_systems = [
                        {
                            "name": "Rooftop units (RTUs) & primary heating/cooling equipment",
                            "quantity": rtu_count,
                            "unit": "EA",
                            "unit_cost": _safe_unit_cost(rtu_total, rtu_count),
                            "total_cost": rtu_total,
                        },
                        {
                            "name": "Make-up air units and exhaust fans",
                            "quantity": exhaust_fans,
                            "unit": "EA",
                            "unit_cost": _safe_unit_cost(exhaust_total, exhaust_fans),
                            "total_cost": exhaust_total,
                        },
                        {
                            "name": "Ductwork, distribution, and ventilation",
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": _safe_unit_cost(distribution_total, sf),
                            "total_cost": distribution_total,
                        },
                    ]

                    scope_items.append({
                        "trade": "Mechanical",
                        "systems": mechanical_systems,
                    })

            electrical_total = float(trades.get("electrical", 0.0) or 0.0)
            if electrical_total > 0:
                if is_cold_storage:
                    electrical_entries = [
                        ("High-capacity power distribution (conceptual)", 0.45),
                        ("Controls & monitoring systems (conceptual)", 0.30),
                        ("Backup power allowance (conceptual)", 0.25),
                    ]
                    total_share = sum(share for _, share in electrical_entries)
                    electrical_systems = []
                    for name, share in electrical_entries:
                        portion = electrical_total * (share / total_share if total_share else 0)
                        electrical_systems.append({
                            "name": name,
                            "quantity": 1,
                            "unit": "LS",
                            "unit_cost": _safe_unit_cost(portion, 1),
                            "total_cost": portion,
                            "notes": "Conceptual / pre-design"
                        })
                    scope_items.append({
                        "trade": "Electrical",
                        "systems": electrical_systems,
                    })
                else:
                    lighting_share = 0.45
                    power_share = 0.35
                    service_share = 0.20

                    lighting_total = electrical_total * lighting_share
                    power_total = electrical_total * power_share
                    service_total = electrical_total * service_share

                    electrical_systems = [
                        {
                            "name": "High-bay lighting & controls",
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": _safe_unit_cost(lighting_total, sf),
                            "total_cost": lighting_total,
                        },
                        {
                            "name": "Power distribution, panels, and branch circuits",
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": _safe_unit_cost(power_total, sf),
                            "total_cost": power_total,
                        },
                        {
                            "name": "Main electrical service and switchgear",
                            "quantity": 1,
                            "unit": "LS",
                            "unit_cost": _safe_unit_cost(service_total, 1),
                            "total_cost": service_total,
                        },
                    ]

                    scope_items.append({
                        "trade": "Electrical",
                        "systems": electrical_systems,
                    })

            plumbing_total = float(trades.get("plumbing", 0.0) or 0.0)
            if plumbing_total > 0:
                restroom_share = 0.50
                domestic_share = 0.20
                esfr_share = 0.30

                restroom_total = plumbing_total * restroom_share
                domestic_total = plumbing_total * domestic_share
                esfr_total = plumbing_total * esfr_share

                plumbing_systems = [
                    {
                        "name": "Restroom groups (fixtures, waste, vent)",
                        "quantity": restroom_groups,
                        "unit": "EA",
                        "unit_cost": _safe_unit_cost(restroom_total, restroom_groups),
                        "total_cost": restroom_total,
                    },
                    {
                        "name": "Domestic water, hose bibs, and roof drains",
                        "quantity": sf,
                        "unit": "SF",
                        "unit_cost": _safe_unit_cost(domestic_total, sf),
                        "total_cost": domestic_total,
                    },
                    {
                        "name": "Fire protection – ESFR sprinkler system",
                        "quantity": sf,
                        "unit": "SF",
                        "unit_cost": _safe_unit_cost(esfr_total, sf),
                        "total_cost": esfr_total,
                    },
                ]

                scope_items.append({
                    "trade": "Plumbing",
                    "systems": plumbing_systems,
                })

            finishes_total = float(trades.get("finishes", 0.0) or 0.0)
            if finishes_total > 0:
                if is_flex:
                    OFFICE_FINISHES_UPLIFT = 1.6
                    total_sf_value = float(sf)
                    office_area = office_sf
                    warehouse_area = warehouse_sf_for_flex if warehouse_sf_for_flex is not None else max(0.0, round(total_sf_value - office_area, 2))
                    finishes_systems: List[Dict[str, Any]] = []
                    base_unit_cost = _safe_unit_cost(finishes_total, total_sf_value) if total_sf_value > 0 else 0.0
                    office_unit_cost = base_unit_cost * OFFICE_FINISHES_UPLIFT if office_area > 0 else 0.0
                    warehouse_unit_cost = base_unit_cost

                    if office_area > 0:
                        office_total = office_unit_cost * office_area
                        finishes_systems.append({
                            "name": "Office/showroom interior buildout allowance (conceptual)",
                            "quantity": office_area,
                            "unit": "SF",
                            "unit_cost": office_unit_cost,
                            "total_cost": office_total,
                        })
                    if warehouse_area > 0:
                        warehouse_total = warehouse_unit_cost * warehouse_area
                        finishes_systems.append({
                            "name": "Warehouse interior fit-out allowance (conceptual)",
                            "quantity": warehouse_area,
                            "unit": "SF",
                            "unit_cost": warehouse_unit_cost,
                            "total_cost": warehouse_total,
                        })
                    if finishes_systems:
                        scope_items.append({
                            "trade": "Finishes",
                            "systems": finishes_systems,
                        })
                elif is_cold_storage:
                    finishes_entries = [
                        ("Insulated panel walls & ceilings (conceptual)", 0.6),
                        ("Sanitary / food-grade finishes (conceptual)", 0.4),
                    ]
                    total_share = sum(entry[1] for entry in finishes_entries)
                    finishes_systems = []
                    for name, share in finishes_entries:
                        portion = finishes_total * (share / total_share if total_share else 0)
                        finishes_systems.append({
                            "name": name,
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": _safe_unit_cost(portion, sf),
                            "total_cost": portion,
                            "notes": "Conceptual / pre-design"
                        })
                    scope_items.append({
                        "trade": "Finishes",
                        "systems": finishes_systems,
                    })
                else:
                    warehouse_sf = sf - office_sf if sf > office_sf else sf

                    office_share = 0.45
                    warehouse_finish_share = 0.40
                    misc_share = 0.15

                    office_total = finishes_total * office_share
                    warehouse_finish_total = finishes_total * warehouse_finish_share
                    misc_finishes_total = finishes_total * misc_share

                    finishes_systems = [
                        {
                            "name": "Office build-out (walls, ceilings, flooring)",
                            "quantity": office_sf,
                            "unit": "SF",
                            "unit_cost": _safe_unit_cost(office_total, office_sf),
                            "total_cost": office_total,
                        },
                        {
                            "name": "Warehouse floor sealers, striping, and protection",
                            "quantity": warehouse_sf,
                            "unit": "SF",
                            "unit_cost": _safe_unit_cost(warehouse_finish_total, warehouse_sf),
                            "total_cost": warehouse_finish_total,
                        },
                        {
                            "name": "Doors, hardware, and misc interior finishes",
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": _safe_unit_cost(misc_finishes_total, sf),
                            "total_cost": misc_finishes_total,
                        },
                    ]

                    scope_items.append({
                        "trade": "Finishes",
                        "systems": finishes_systems,
                    })

        return scope_items
    
    def _calculate_ownership(
        self,
        total_cost: float,
        financing_terms: Any,
        revenue_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculate ownership/financing metrics with DSCR tied to revenue NOI when available."""
        
        # Calculate debt and equity
        debt_amount = total_cost * financing_terms.debt_ratio
        equity_amount = total_cost * financing_terms.equity_ratio
        philanthropy_amount = total_cost * financing_terms.philanthropy_ratio
        grants_amount = total_cost * financing_terms.grants_ratio
        
        # Calculate debt service
        annual_debt_service = debt_amount * financing_terms.debt_rate
        monthly_debt_service = annual_debt_service / 12
        
        # Prefer NOI from revenue analysis when available so DSCR matches frontend revenue panel
        noi_from_revenue = None
        if revenue_analysis and isinstance(revenue_analysis.get('net_income'), (int, float)):
            noi_from_revenue = float(revenue_analysis['net_income'])
        
        fallback_noi = total_cost * getattr(financing_terms, 'noi_percentage', 0.08)
        estimated_annual_noi = noi_from_revenue if noi_from_revenue is not None else fallback_noi
        dscr = estimated_annual_noi / annual_debt_service if annual_debt_service > 0 else 0
        
        self._log_trace("noi_derived", {
            'total_project_cost': total_cost,
            'estimated_noi': estimated_annual_noi,
            'method': 'revenue_analysis' if noi_from_revenue is not None else 'fixed_percentage'
        })

        result = {
            'financing_sources': {
                'debt_amount': debt_amount,
                'equity_amount': equity_amount,
                'philanthropy_amount': philanthropy_amount,
                'grants_amount': grants_amount,
                'total_sources': debt_amount + equity_amount + philanthropy_amount + grants_amount
            },
            'debt_metrics': {
                'debt_rate': financing_terms.debt_rate,
                'annual_debt_service': annual_debt_service,
                'monthly_debt_service': monthly_debt_service,
                'target_dscr': financing_terms.target_dscr,
                'calculated_dscr': dscr,
                'dscr_meets_target': dscr >= financing_terms.target_dscr
            },
            'return_metrics': {
                'target_roi': financing_terms.target_roi,
                'estimated_annual_noi': estimated_annual_noi,
                'cash_on_cash_return': (estimated_annual_noi - annual_debt_service) / equity_amount if equity_amount > 0 else 0
            }
        }
        
        self._log_trace("ownership_analysis_calculated", {
            'total_project_cost': total_cost,
            'debt_ratio': financing_terms.debt_ratio,
            'dscr': dscr
        })
        
        return result
    
    def _log_trace(self, step: str, data: Dict[str, Any]):
        """Log calculation steps for debugging and transparency"""
        trace_entry = {
            'step': step,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self.calculation_trace.append(trace_entry)
        logger.debug(f"Calculation trace: {step} - {data}")
    
    def calculate_comparison(self, 
                           scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate and compare multiple scenarios
        
        Args:
            scenarios: List of scenario dictionaries with calculation parameters
            
        Returns:
            Comparison results with all scenarios
        """
        results = []
        
        for i, scenario in enumerate(scenarios):
            try:
                # Convert string types to enums
                building_type = BuildingType(scenario['building_type'])
                project_class = ProjectClass(scenario.get('project_class', 'ground_up'))
                ownership_type = OwnershipType(scenario.get('ownership_type', 'for_profit'))
                
                # Calculate scenario
                result = self.calculate_project(
                    building_type=building_type,
                    subtype=scenario['subtype'],
                    square_footage=scenario['square_footage'],
                    location=scenario['location'],
                    project_class=project_class,
                    floors=scenario.get('floors', 1),
                    ownership_type=ownership_type,
                    finish_level=scenario.get('finish_level') or scenario.get('finishLevel'),
                    special_features=scenario.get('special_features', [])
                )
                
                result['scenario_name'] = scenario.get('name', f'Scenario {i+1}')
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error calculating scenario {i+1}: {str(e)}")
                results.append({
                    'scenario_name': scenario.get('name', f'Scenario {i+1}'),
                    'error': str(e)
                })
        
        # Find best/worst scenarios
        valid_results = [r for r in results if 'error' not in r]
        if valid_results:
            lowest_cost = min(valid_results, key=lambda x: x['totals']['total_project_cost'])
            highest_cost = max(valid_results, key=lambda x: x['totals']['total_project_cost'])
        else:
            lowest_cost = highest_cost = None
        
        return {
            'scenarios': results,
            'summary': {
                'total_scenarios': len(scenarios),
                'successful_calculations': len(valid_results),
                'lowest_cost_scenario': lowest_cost['scenario_name'] if lowest_cost else None,
                'highest_cost_scenario': highest_cost['scenario_name'] if highest_cost else None,
                'cost_range': {
                    'min': lowest_cost['totals']['total_project_cost'] if lowest_cost else 0,
                    'max': highest_cost['totals']['total_project_cost'] if highest_cost else 0
                }
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_ownership_analysis(self, calculations: dict) -> dict:
        """Calculate ownership and revenue analysis using master_config data"""
        
        building_type = calculations.get('building_type')
        subtype = calculations.get('subtype')
        square_footage = calculations.get('square_footage', 0)
        total_cost = calculations.get('total_cost', 0)
        construction_cost = calculations.get('subtotal', 0)
        total_project_cost = total_cost
        
        # Get the config for this building/subtype
        building_enum = self._get_building_enum(building_type)
        if not building_enum or building_enum not in MASTER_CONFIG:
            return self._empty_ownership_analysis()
        
        subtype_config = MASTER_CONFIG[building_enum].get(subtype)
        if not subtype_config:
            return self._empty_ownership_analysis()
        
        scenario_value = (
            calculations.get('scenario')
            or calculations.get('scenario_key')
            or calculations.get('scenarioName')
            or calculations.get('scenarioKey')
        )
        scenario_key_normalized = (
            scenario_value.strip().lower()
            if isinstance(scenario_value, str) and scenario_value.strip()
            else None
        )
        provided_quality_factor = calculations.get('quality_factor')
        finish_level = calculations.get('finish_level')
        normalized_finish_level = finish_level.lower() if isinstance(finish_level, str) else None

        modifiers = calculations.get('modifiers') or {}
        revenue_factor = float(modifiers.get('revenue_factor', 1.0) or 1.0)
        margin_pct = float(modifiers.get('margin_pct', get_margin_pct(building_enum, subtype)))
        office_operating_expense_override = None
        office_cam_charges = None
        staffing_pct_pm = None
        staffing_pct_maintenance = None
        if building_enum == BuildingType.OFFICE:
            if getattr(subtype_config, 'operating_expense_per_sf', None) and square_footage > 0:
                office_operating_expense_override = square_footage * float(subtype_config.operating_expense_per_sf)
            if getattr(subtype_config, 'cam_charges_per_sf', None) and square_footage > 0:
                office_cam_charges = square_footage * float(subtype_config.cam_charges_per_sf)
            staffing_pct_pm = getattr(subtype_config, 'staffing_pct_property_mgmt', None)
            staffing_pct_maintenance = getattr(subtype_config, 'staffing_pct_maintenance', None)

        base_cost_psf = subtype_config.base_cost_per_sf
        if provided_quality_factor is not None:
            quality_factor = provided_quality_factor
        else:
            actual_cost_psf = construction_cost / square_footage if square_footage > 0 else base_cost_psf
            quality_factor = pow(actual_cost_psf / base_cost_psf, 0.5) if base_cost_psf > 0 else 1.0
            if quality_factor is None:
                quality_factor = 1.0

        if normalized_finish_level in ("premium", "luxury"):
            is_premium = True
        else:
            is_premium = quality_factor > 1.2

        # Industrial occupancy should follow config's base/premium rates.
        if building_enum == BuildingType.INDUSTRIAL:
            occ_base = getattr(subtype_config, "occupancy_rate_base", None)
            occ_premium = getattr(subtype_config, "occupancy_rate_premium", None)
            if is_premium and isinstance(occ_premium, (int, float)):
                occupancy_rate = float(occ_premium)
            elif isinstance(occ_base, (int, float)):
                occupancy_rate = float(occ_base)
            else:
                occupancy_rate = 0.95
        else:
            occupancy_rate = subtype_config.occupancy_rate_premium if is_premium else subtype_config.occupancy_rate_base
            if occupancy_rate is None:
                occupancy_rate = 0.85

        annual_revenue = self._calculate_revenue_by_type(
            building_enum, subtype_config, square_footage, quality_factor, occupancy_rate, calculations
        )
        
        # Apply revenue modifiers
        annual_revenue *= revenue_factor
        restaurant_full_service = (
            building_enum == BuildingType.RESTAURANT
            and isinstance(subtype, str)
            and subtype.strip().lower() == 'full_service'
        )
        if restaurant_full_service:
            finish_occ_override = calculations.get('restaurant_finish_occupancy_override')
            if isinstance(finish_occ_override, (int, float)):
                occupancy_rate = float(finish_occ_override)
            finish_margin_override = calculations.get('restaurant_finish_margin_override')
            if isinstance(finish_margin_override, (int, float)):
                margin_pct = float(finish_margin_override)
        hospitality_financials = calculations.get('hospitality_financials') if building_enum == BuildingType.HOSPITALITY else None
        hospitality_expense_pct = None
        if hospitality_financials:
            hospitality_financials['annual_revenue'] = annual_revenue
            derived_occupancy = hospitality_financials.get('occupancy')
            if isinstance(derived_occupancy, (int, float)):
                occupancy_rate = derived_occupancy
            expense_override = hospitality_financials.get('expense_pct')
            if isinstance(expense_override, (int, float)):
                hospitality_expense_pct = max(0.0, min(float(expense_override), 0.95))
        
        margin_pct = margin_pct if margin_pct else get_margin_pct(building_enum, subtype)
        if hospitality_expense_pct is not None:
            margin_pct = 1 - hospitality_expense_pct
        # For industrial, enforce the configured operating margin (NNN style).
        if building_enum == BuildingType.INDUSTRIAL:
            industrial_margin = getattr(subtype_config, "operating_margin_base", None)
            if isinstance(industrial_margin, (int, float)) and industrial_margin > 0:
                margin_pct = float(industrial_margin)
        utility_ratio = float(getattr(subtype_config, 'utility_cost_ratio', 0.0) or 0.0)
        tenant_paid_utilities = (
            building_enum == BuildingType.INDUSTRIAL
            and isinstance(subtype, str)
            and subtype.strip().lower() == 'cold_storage'
            and scenario_key_normalized in {'tenant_paid_utilities', 'nnn_utilities', 'cold_storage_nnn'}
        )
        if tenant_paid_utilities and utility_ratio > 0:
            margin_pct = min(0.995, margin_pct + utility_ratio)
        self._log_trace("margin_normalized", {
            'building_type': building_enum.value,
            'subtype': subtype,
            'margin_pct': round(margin_pct, 4)
        })
        office_financials = calculations.get('office_financials') if building_enum == BuildingType.OFFICE else None
        if hospitality_financials and hospitality_expense_pct is not None:
            total_expenses = round(annual_revenue * hospitality_expense_pct, 2)
        elif office_financials:
            annual_revenue = office_financials.get('egi', annual_revenue)
            total_expenses = round(
                office_financials.get('opex', 0.0)
                + office_financials.get('ti_amort', 0.0)
                + office_financials.get('lc_amort', 0.0),
                2
            )
            derived_margin = office_financials.get('noi_margin')
            if isinstance(derived_margin, (int, float)):
                margin_pct = float(derived_margin)
            elif annual_revenue > 0:
                margin_pct = max(0.05, min(0.65, 1 - (total_expenses / annual_revenue)))
        elif office_operating_expense_override is not None:
            total_expenses = round(office_operating_expense_override, 2)
            if annual_revenue > 0:
                margin_pct = max(0.05, min(0.65, 1 - (total_expenses / annual_revenue)))
        else:
            total_expenses = round(annual_revenue * (1 - margin_pct), 2)

        net_income = round(annual_revenue - total_expenses, 2)
        if hospitality_financials:
            hospitality_financials['total_operating_expenses'] = total_expenses
            hospitality_financials['annual_noi'] = net_income
            hospitality_financials['noi_margin'] = margin_pct
            rooms_value = hospitality_financials.get('rooms')
            adr_value = hospitality_financials.get('adr')
            occupancy_value = hospitality_financials.get('occupancy')
            revpar_value = hospitality_financials.get('revpar')
            if rooms_value is not None:
                calculations['rooms'] = float(rooms_value)
                total_cost_value = (
                    calculations.get('total_project_cost')
                    or calculations.get('total_cost')
                    or total_cost
                )
                if isinstance(total_cost_value, (int, float)) and total_cost_value > 0:
                    try:
                        calculations['cost_per_key'] = float(total_cost_value) / float(rooms_value)
                    except (TypeError, ValueError, ZeroDivisionError):
                        pass
            if adr_value is not None:
                calculations['adr'] = float(adr_value)
            if occupancy_value is not None:
                calculations['occupancy'] = float(occupancy_value)
                if adr_value is not None:
                    calculations['revpar'] = float(adr_value) * float(occupancy_value)
            elif revpar_value is not None:
                calculations['revpar'] = float(revpar_value)
            key_map = {
                'rooms': 'rooms',
                'adr': 'adr',
                'occupancy': 'occupancy',
                'revpar': 'revpar',
                'cost_per_key': 'cost_per_key'
            }
            for source_key, dest_key in key_map.items():
                hosp_value = hospitality_financials.get(source_key)
                if hosp_value is None:
                    continue
                try:
                    calculations[dest_key] = float(hosp_value)
                except (TypeError, ValueError):
                    calculations[dest_key] = hosp_value
        cam_charges_value = round(office_cam_charges, 2) if office_cam_charges is not None else round(float(calculations.get('cam_charges', 0) or 0), 2)
        market_cap_rate_config = getattr(subtype_config, 'market_cap_rate', None)
        yield_on_cost = net_income / total_cost if total_cost > 0 else 0
        cap_rate_spread_bps = None
        if isinstance(market_cap_rate_config, (int, float)):
            cap_rate_spread_bps = int(round((yield_on_cost - market_cap_rate_config) * 10000))

        property_mgmt_staff_cost = None
        maintenance_staff_cost = None
        if building_enum == BuildingType.OFFICE and total_expenses > 0:
            prop_pct = float(staffing_pct_pm or 0.06)
            maint_pct = float(staffing_pct_maintenance or 0.12)
            property_mgmt_staff_cost = round(total_expenses * prop_pct, 2)
            maintenance_staff_cost = round(total_expenses * maint_pct, 2)

        efficiency_config = subtype_config
        if tenant_paid_utilities and utility_ratio > 0:
            try:
                efficiency_config = replace(subtype_config, utility_cost_ratio=0.0)
            except TypeError:
                efficiency_config = subtype_config

        operational_efficiency = self.calculate_operational_efficiency(
            revenue=annual_revenue,
            config=efficiency_config,
            subtype=subtype,
            margin_pct=margin_pct,
            total_expenses_override=total_expenses
        )
        total_expenses = operational_efficiency.get('total_expenses', total_expenses)
        operating_margin = round(margin_pct, 3) if annual_revenue > 0 else 0
        expense_ratio = round(1 - margin_pct, 3) if annual_revenue > 0 else 0
        operational_efficiency['operating_margin'] = operating_margin
        operational_efficiency['expense_ratio'] = expense_ratio
        operational_efficiency['efficiency_score'] = round(margin_pct * 100, 1) if annual_revenue > 0 else 0
        if property_mgmt_staff_cost is not None:
            operational_efficiency['property_mgmt_staffing'] = property_mgmt_staff_cost
        if maintenance_staff_cost is not None:
            operational_efficiency['maintenance_staffing'] = maintenance_staff_cost
        operational_efficiency['cam_charges'] = cam_charges_value
        
        # Standard projection period for IRR calculation
        years = 10

        property_value = 0
        market_cap_rate = None
        exit_cap_rate, discount_rate = self.get_exit_cap_and_discount_rate(building_enum)

        if net_income <= 0 or total_cost <= 0:
            npv = -total_cost
            irr = 0.0
            market_cap_rate = exit_cap_rate
        else:
            market_cap_rate = exit_cap_rate
            terminal_value = net_income / exit_cap_rate if exit_cap_rate > 0 else 0
            property_value = terminal_value
            cashflows = self.build_unlevered_cashflows_with_exit(
                total_project_cost=total_cost,
                annual_noi=net_income,
                years=years,
                exit_cap_rate=exit_cap_rate
            )
            if not cashflows:
                npv = property_value - total_cost
                irr = 0.0
            else:
                try:
                    npv = self.calculate_npv(
                        initial_investment=total_cost,
                        annual_cash_flow=net_income,
                        years=years,
                        discount_rate=discount_rate,
                        cashflows=cashflows
                    )
                except OverflowError:
                    npv = property_value - total_cost

                try:
                    irr = self.calculate_irr(
                        initial_investment=total_cost,
                        annual_cash_flow=net_income,
                        years=years,
                        cashflows=cashflows
                    )
                except OverflowError:
                    irr = 0.0
        
        revenue_requirements = self.calculate_revenue_requirements(
            total_cost=total_cost,
            config=subtype_config,
            square_footage=square_footage,
            actual_annual_revenue=annual_revenue,
            actual_net_income=net_income,
            margin_pct=margin_pct
        )
        
        # Calculate payback period
        payback_period = round(total_cost / net_income, 1) if net_income > 0 else 999
        
        # Derive units for display/per-unit metrics when not provided.
        units = calculations.get('units')
        if not units:
            units = 0
            if (
                building_enum == BuildingType.MULTIFAMILY
                and hasattr(subtype_config, 'units_per_sf')
                and square_footage > 0
            ):
                try:
                    units_estimate = float(subtype_config.units_per_sf) * float(square_footage)
                    units = max(1, int(round(units_estimate)))
                except (TypeError, ValueError):
                    units = 0
            elif (
                building_enum == BuildingType.HEALTHCARE
                and subtype in ('outpatient_clinic', 'urgent_care', 'imaging_center', 'surgical_center', 'medical_office', 'dental_office')
                and hasattr(subtype_config, 'financial_metrics')
                and isinstance(subtype_config.financial_metrics, dict)
            ):
                fm = subtype_config.financial_metrics
                units_per_sf = fm.get('units_per_sf') or 0
                if square_footage and units_per_sf:
                    try:
                        units = max(1, int(round(float(square_footage) * float(units_per_sf))))
                    except (TypeError, ValueError):
                        units = 0
                if units:
                    calculations['units'] = units
                    unit_label_value = fm.get('primary_unit', 'units')
                    calculations['unit_label'] = unit_label_value
                    calculations['unit_type'] = unit_label_value
            if (
                units
                and building_enum == BuildingType.HEALTHCARE
                and subtype in ('outpatient_clinic', 'urgent_care', 'imaging_center', 'surgical_center', 'medical_office', 'dental_office')
                and hasattr(subtype_config, 'financial_metrics')
                and isinstance(subtype_config.financial_metrics, dict)
            ):
                fm = subtype_config.financial_metrics
                unit_label_value = fm.get('primary_unit', 'units')
                calculations.setdefault('unit_label', unit_label_value)
                calculations.setdefault('unit_type', unit_label_value)
                total_cost_value = total_cost
                annual_revenue_value = annual_revenue
                if units > 0:
                    calculations['cost_per_unit'] = total_cost_value / units if units else 0
                    calculations['revenue_per_unit'] = annual_revenue_value / units if units else 0
        
        # Calculate display-ready operational metrics
        operational_metrics = self.calculate_operational_metrics_for_display(
            building_type=building_type,
            subtype=subtype,
            operational_efficiency=operational_efficiency,
            square_footage=square_footage,
            annual_revenue=annual_revenue,
            units=units
        )
        
        # Surface per-unit data for downstream cards (MF heavy).
        operational_metrics.setdefault('per_unit', {})
        operational_metrics['per_unit'].setdefault('units', units or 0)
        if units and units > 0:
            cost_per_unit = total_cost / units
            annual_revenue_per_unit = annual_revenue / units
            monthly_revenue_per_unit = annual_revenue_per_unit / 12.0
            operational_metrics['per_unit'].update({
                'cost_per_unit': round(cost_per_unit, 2),
                'annual_revenue_per_unit': round(annual_revenue_per_unit, 2),
                'monthly_revenue_per_unit': round(monthly_revenue_per_unit, 2),
            })
        
        # Underwriting refinement metrics: yield gap, break-even occupancy, sensitivity
        building_profile = get_building_profile(building_enum)
        target_yield = building_profile.get('target_yield') if building_profile else None
        yield_gap_bps = None
        if isinstance(target_yield, (int, float)):
            try:
                yield_gap_bps = int(round((target_yield - yield_on_cost) * 10000))
            except (TypeError, ValueError):
                yield_gap_bps = None

        break_even_occupancy_for_yield = None
        if (
            isinstance(target_yield, (int, float))
            and yield_on_cost > 0
            and isinstance(occupancy_rate, (int, float))
        ):
            try:
                occ_required = occupancy_rate * (target_yield / yield_on_cost)
                break_even_occupancy_for_yield = max(0.0, min(1.0, float(occ_required)))
            except (TypeError, ValueError, ZeroDivisionError):
                break_even_occupancy_for_yield = None

        sensitivity_analysis = None
        if total_cost > 0:
            try:
                base_yoc = yield_on_cost
                subtype_normalized = subtype.strip().lower() if isinstance(subtype, str) else ''
                if (
                    building_enum == BuildingType.HEALTHCARE
                    and subtype_normalized in ('outpatient_clinic', 'urgent_care', 'surgical_center')
                ):
                    base_revenue = float(annual_revenue or 0)
                    base_margin = (float(net_income) / base_revenue) if base_revenue else 0.0
                    asc_mode = subtype_normalized == 'surgical_center'

                    def build_tile(label: str, scenario_yield: Optional[float]):
                        if scenario_yield is None:
                            return {'label': label, 'yield_on_cost': None, 'yield_delta': None}
                        delta = scenario_yield - base_yoc
                        return {
                            'label': label,
                            'yield_on_cost': round(scenario_yield, 4),
                            'yield_delta': round(delta, 4) if delta is not None else None,
                            'yield_delta_bps': int(round(delta * 10000)) if delta is not None else None
                        }

                    def yield_from_revenue(revenue_value: float, margin_value: float) -> Optional[float]:
                        if total_cost <= 0:
                            return None
                        noi_value = revenue_value * margin_value
                        return noi_value / total_cost if total_cost else None

                    visits_up_revenue = base_revenue * 1.05
                    visits_down_revenue = base_revenue * 0.95
                    reimbursement_up_revenue = base_revenue * 1.02
                    labor_margin = max(0.0, base_margin - 0.02)

                    visits_up_yield = yield_from_revenue(visits_up_revenue, base_margin)
                    visits_down_yield = yield_from_revenue(visits_down_revenue, base_margin)
                    reimbursement_yield = yield_from_revenue(reimbursement_up_revenue, base_margin)
                    labor_yield = yield_from_revenue(base_revenue, labor_margin)

                    sensitivity_analysis = {
                        'base': {'yield_on_cost': round(base_yoc, 4)},
                        'revenue_up_10': {
                            'yield_on_cost': round(visits_up_yield, 4) if visits_up_yield is not None else None,
                            'label': 'IF Case Volume +5%' if asc_mode else 'IF Visits / Day +5%'
                        },
                        'revenue_down_10': {
                            'yield_on_cost': round(visits_down_yield, 4) if visits_down_yield is not None else None,
                            'label': 'IF Case Volume -5%' if asc_mode else 'IF Visits / Day -5%'
                        },
                        'cost_up_10': {
                            'yield_on_cost': round(labor_yield, 4) if labor_yield is not None else None,
                            'label': 'IF Operating Costs +2 pts' if asc_mode else 'IF Labor Cost +2 pts'
                        },
                        'cost_down_10': {
                            'yield_on_cost': round(reimbursement_yield, 4) if reimbursement_yield is not None else None,
                            'label': 'IF Reimbursement +2%'
                        },
                        'scenarios': [
                            build_tile('IF Case Volume +5%' if asc_mode else 'IF Visits / Day +5%', visits_up_yield),
                            build_tile('IF Case Volume -5%' if asc_mode else 'IF Visits / Day -5%', visits_down_yield),
                            build_tile('IF Reimbursement +2%', reimbursement_yield),
                            build_tile('IF Operating Costs +2 pts' if asc_mode else 'IF Labor Cost +2 pts', labor_yield),
                        ]
                    }
                else:
                    noi_up = net_income * 1.10
                    noi_down = net_income * 0.90
                    total_cost_up = total_cost * 1.10
                    total_cost_down = total_cost * 0.90

                    sensitivity_analysis = {
                        'base': {'yield_on_cost': round(base_yoc, 4)},
                        'revenue_up_10': {
                            'yield_on_cost': round(noi_up / total_cost, 4)
                            if total_cost > 0 else None
                        },
                        'revenue_down_10': {
                            'yield_on_cost': round(noi_down / total_cost, 4)
                            if total_cost > 0 else None
                        },
                        'cost_up_10': {
                            'yield_on_cost': round(net_income / total_cost_up, 4)
                            if total_cost_up > 0 else None
                        },
                        'cost_down_10': {
                            'yield_on_cost': round(net_income / total_cost_down, 4)
                            if total_cost_down > 0 else None
                        },
                    }
            except Exception:
                sensitivity_analysis = None

        cash_on_cash_return_pct = round((net_income / total_cost) * 100, 2) if total_cost > 0 else 0
        cap_rate_pct = round((net_income / total_cost) * 100, 2) if total_cost > 0 else 0

        target_roi = get_target_roi(building_enum)
        feasible = (npv >= 0) and ((cash_on_cash_return_pct / 100) >= target_roi)

        self._log_trace("feasibility_evaluated", {
            'roi': cash_on_cash_return_pct,
            'target_roi': target_roi,
            'npv': npv,
            'feasible': feasible
        })

        default_vacancy_rate = 0.0
        if isinstance(occupancy_rate, (int, float)):
            default_vacancy_rate = max(0.0, min(1.0, 1.0 - occupancy_rate))

        underwriting = calculations.get('underwriting')
        if not underwriting:
            underwriting = {
                'effective_gross_income': round(annual_revenue, 2),
                'underwritten_operating_expenses': round(total_expenses, 2),
                'underwritten_noi': round(net_income, 2),
                'vacancy_rate': default_vacancy_rate,
                'collection_loss': 0.0,
                'management_fee': 0.0,
                'capex_reserve': 0.0,
            }

        project_timeline = build_project_timeline(building_enum, None)
        construction_schedule = build_construction_schedule(building_enum)

        return {
            'revenue_analysis': {
                'annual_revenue': round(annual_revenue, 2),
                'revenue_per_sf': round(annual_revenue / square_footage, 2) if square_footage > 0 else 0,
                'operating_margin': operating_margin,
                'net_income': round(net_income, 2),
                'underwritten_noi': round(underwriting.get('underwritten_noi', net_income), 2),
                'operating_expenses': round(total_expenses, 2),
                'cam_charges': cam_charges_value,
                'occupancy_rate': occupancy_rate,
                'quality_factor': round(quality_factor, 2),
                'is_premium': is_premium,
                'revenue_factor': round(revenue_factor, 4),
                'finish_revenue_factor': round(modifiers.get('finish_revenue_factor', 1.0), 4),
                'regional_multiplier': round(modifiers.get('market_factor', 1.0), 4)
            },
            'return_metrics': {
                'estimated_annual_noi': round(net_income, 2),
                'cash_on_cash_return': cash_on_cash_return_pct,
                'cap_rate': cap_rate_pct,
                'npv': npv,
                'irr': round(irr * 100, 2),  # Convert to percentage
                'payback_period': payback_period,
                'property_value': property_value,  # Always include the value
                'market_cap_rate': market_cap_rate,  # Always include the rate
                'is_multifamily': building_enum == BuildingType.MULTIFAMILY,  # Debug flag
                'feasible': feasible
            },
            'yield_on_cost': round(yield_on_cost, 4),
            'yield_gap_bps': yield_gap_bps,
            'break_even_occupancy_for_target_yield': break_even_occupancy_for_yield,
            'market_cap_rate': round(market_cap_rate_config, 4) if isinstance(market_cap_rate_config, (int, float)) else None,
            'cap_rate_spread_bps': cap_rate_spread_bps,
            'revenue_requirements': revenue_requirements,
            'operational_efficiency': operational_efficiency,  # Keep raw data
            'operational_metrics': operational_metrics,  # ADD formatted display data
            'underwriting': underwriting,
            'sensitivity_analysis': sensitivity_analysis,
            'project_timeline': project_timeline,
            'construction_schedule': construction_schedule,
            'hospitality_financials': calculations.get('hospitality_financials'),
            'flex_revenue_per_sf': calculations.get('flex_revenue_per_sf'),
        }

    def _calculate_revenue_by_type(self, building_enum, config, square_footage, quality_factor, occupancy_rate, calculation_context: Optional[Dict[str, Any]] = None):
        """Calculate revenue based on the specific building type's metrics"""
        
        # Initialize base_revenue to avoid uninitialized variable
        base_revenue = 0
        context = calculation_context or {}
        subtype_key = (str(context.get('subtype')) if context.get('subtype') is not None else '').strip().lower()
        finish_level_value = context.get('finish_level') or context.get('finishLevel') or 'standard'
        if isinstance(finish_level_value, str):
            finish_level_value = finish_level_value.strip().lower() or 'standard'
        else:
            finish_level_value = 'standard'
        regional_ctx = context.get('regional_context') or {}
        market_factor = regional_ctx.get('market_factor')
        if not isinstance(market_factor, (int, float)):
            modifiers_ctx = context.get('modifiers') or {}
            market_factor = modifiers_ctx.get('market_factor', 1.0)
        try:
            market_factor = float(market_factor)
        except (TypeError, ValueError):
            market_factor = 1.0
        if market_factor <= 0:
            market_factor = 1.0
        
        # Healthcare - uses beds, visits, procedures, or scans
        if building_enum == BuildingType.HEALTHCARE:
            if hasattr(config, 'base_revenue_per_bed_annual') and config.base_revenue_per_bed_annual and hasattr(config, 'beds_per_sf') and config.beds_per_sf:
                beds = square_footage * config.beds_per_sf
                base_revenue = beds * config.base_revenue_per_bed_annual
            elif hasattr(config, 'base_revenue_per_visit') and config.base_revenue_per_visit and hasattr(config, 'visits_per_day') and config.visits_per_day and hasattr(config, 'days_per_year') and config.days_per_year:
                annual_visits = config.visits_per_day * config.days_per_year
                base_revenue = annual_visits * config.base_revenue_per_visit
            elif hasattr(config, 'base_revenue_per_procedure') and config.base_revenue_per_procedure and hasattr(config, 'procedures_per_day') and config.procedures_per_day and hasattr(config, 'days_per_year') and config.days_per_year:
                annual_procedures = config.procedures_per_day * config.days_per_year
                base_revenue = annual_procedures * config.base_revenue_per_procedure
            elif hasattr(config, 'base_revenue_per_scan') and config.base_revenue_per_scan and hasattr(config, 'scans_per_day') and config.scans_per_day and hasattr(config, 'days_per_year') and config.days_per_year:
                annual_scans = config.scans_per_day * config.days_per_year
                base_revenue = annual_scans * config.base_revenue_per_scan
            elif hasattr(config, 'base_revenue_per_sf_annual') and config.base_revenue_per_sf_annual:
                base_revenue = square_footage * config.base_revenue_per_sf_annual
            else:
                # Fallback for healthcare with missing revenue config
                base_revenue = 0
            if subtype_key == 'medical_office':
                base_revenue_per_sf = getattr(config, 'base_revenue_per_sf_annual', None)
                operating_margin_base = getattr(config, 'operating_margin_base', None)
                annual_revenue = 0.0
                if base_revenue_per_sf and square_footage:
                    try:
                        annual_revenue = float(base_revenue_per_sf) * float(square_footage)
                    except (TypeError, ValueError):
                        annual_revenue = 0.0
                if operating_margin_base is not None and annual_revenue:
                    try:
                        noi = float(annual_revenue) * float(operating_margin_base)
                    except (TypeError, ValueError):
                        noi = 0.0
                else:
                    noi = 0.0
                adjusted_annual_revenue = annual_revenue * market_factor
                adjusted_noi = (noi * market_factor) if noi is not None else 0.0
                context['mob_revenue'] = {
                    'annual_revenue': adjusted_annual_revenue,
                    'operating_margin': operating_margin_base,
                    'net_operating_income': adjusted_noi
                }
                return adjusted_annual_revenue
        
        # Multifamily - uses monthly rent per unit
        elif building_enum == BuildingType.MULTIFAMILY:
            units = square_footage * config.units_per_sf
            monthly_rent = config.base_revenue_per_unit_monthly
            base_revenue = units * monthly_rent * 12
        
        # Hospitality - use ADR x occupancy x room count with expense profiling
        elif building_enum == BuildingType.HOSPITALITY:
            hospitality_financials = self._build_hospitality_financials(
                config=config,
                square_footage=square_footage,
                context=context
           )
            if hospitality_financials:
                context['hospitality_financials'] = hospitality_financials
                base_revenue = hospitality_financials.get('annual_room_revenue', 0)
                occupancy_rate = 1.0  # Occupancy already captured in the revenue model
            else:
                rooms = square_footage * getattr(config, 'rooms_per_sf', 0)
                base_revenue = rooms * getattr(config, 'base_revenue_per_room_annual', 0)
        
        # Office - leverage Class A profile for PGI/EGI/NOI
        elif building_enum == BuildingType.OFFICE:
            office_profile = {}
            profile_source = getattr(config, 'financial_metrics', None)
            if isinstance(profile_source, dict):
                office_profile = dict(profile_source)
            if office_profile:
                base_rent = office_profile.get('base_rent_per_sf')
                try:
                    if base_rent is not None:
                        office_profile['base_rent_per_sf'] = float(base_rent) * float(quality_factor or 1.0)
                except (TypeError, ValueError):
                    pass
                office_financials = self._build_office_financials(square_footage, office_profile)
            else:
                office_financials = {}
            if office_financials:
                context['office_financials'] = office_financials
                context['stabilized_revenue'] = office_financials.get('egi')
                context['stabilized_noi'] = office_financials.get('noi')
                context['rent_per_sf'] = office_financials.get('rent_per_sf')
                context['noi_per_sf'] = office_financials.get('noi_per_sf')
                context['operating_margin'] = office_financials.get('noi_margin')
                context['office_total_expenses'] = (
                    office_financials.get('opex', 0.0)
                    + office_financials.get('ti_amort', 0.0)
                    + office_financials.get('lc_amort', 0.0)
                )
                context['office_pgi'] = office_financials.get('pgi')
                context['office_vacancy_and_credit_loss'] = office_financials.get('vacancy_and_credit_loss')
            base_revenue = office_financials.get('egi', square_footage * getattr(config, 'base_revenue_per_sf_annual', 0))
            quality_factor = 1.0
            occupancy_rate = 1.0
        
        # Educational - uses revenue per student
        elif building_enum == BuildingType.EDUCATIONAL:
            students = square_footage * config.students_per_sf
            base_revenue = students * config.base_revenue_per_student_annual
        
        # Parking - uses revenue per space
        elif building_enum == BuildingType.PARKING:
            if hasattr(config, 'base_revenue_per_space_monthly'):
                spaces = square_footage * config.spaces_per_sf
                base_revenue = spaces * config.base_revenue_per_space_monthly * 12
            else:
                base_revenue = 0
        
        # Recreation - special handling for stadium
        elif building_enum == BuildingType.RECREATION:
            if hasattr(config, 'base_revenue_per_seat_annual'):
                seats = square_footage * config.seats_per_sf
                base_revenue = seats * config.base_revenue_per_seat_annual
            else:
                base_revenue = square_footage * config.base_revenue_per_sf_annual
        
        # Civic - no revenue (government funded)
        elif building_enum == BuildingType.CIVIC:
            return 0
        
        # Default - uses revenue per SF (Office, Retail, Restaurant, etc.)
        else:
            # Industrial revenue is tied directly to square footage rents (NNN).
            if building_enum == BuildingType.INDUSTRIAL:
                base_psf = getattr(config, 'base_revenue_per_sf_annual', None)
                if base_psf is None:
                    # Fallback if config missing: assume ~$12/SF EGI at 95% occ.
                    base_psf = 11.5

                if subtype_key == 'flex_space':
                    OFFICE_RENT_UPLIFT = 1.35

                    office_share_value = None
                    parsed_input_candidates: List[Dict[str, Any]] = []

                    parsed_input_direct = context.get('parsed_input') or context.get('parsedInput')
                    if isinstance(parsed_input_direct, dict):
                        parsed_input_candidates.append(parsed_input_direct)

                    request_payload = context.get('request_payload') or context.get('requestPayload')
                    if isinstance(request_payload, dict):
                        nested_parsed = request_payload.get('parsed_input') or request_payload.get('parsedInput')
                        if isinstance(nested_parsed, dict):
                            parsed_input_candidates.append(nested_parsed)

                    for candidate in parsed_input_candidates:
                        if 'office_share' in candidate:
                            office_share_value = candidate.get('office_share')
                            break

                    flex_office_share = None
                    if office_share_value is not None:
                        try:
                            flex_office_share = float(office_share_value)
                        except (TypeError, ValueError):
                            flex_office_share = None
                    if flex_office_share is not None:
                        flex_office_share = max(0.0, min(1.0, flex_office_share))
                        office_psf = base_psf * OFFICE_RENT_UPLIFT
                        blended_psf = ((1.0 - flex_office_share) * base_psf) + (flex_office_share * office_psf)
                        base_psf = blended_psf
                        context['flex_revenue_per_sf'] = blended_psf

                base_revenue = square_footage * base_psf
            else:
                base_revenue = square_footage * config.base_revenue_per_sf_annual

        # Apply finish-level revenue/margin adjustments for full-service restaurants
        if building_enum == BuildingType.RESTAURANT and subtype_key == 'full_service':
            finish_rev_multiplier_map = {
                'standard': 1.00,
                'premium': 1.18,
                'luxury': 1.32,
            }
            finish_occupancy_map = {
                'standard': 0.80,
                'premium': 0.82,
                'luxury': 0.86,
            }
            finish_margin_map = {
                'standard': 0.10,
                'premium': 0.11,
                'luxury': 0.12,
            }
            finish_rev_multiplier = finish_rev_multiplier_map.get(finish_level_value, 1.00)
            adjusted_occupancy = finish_occupancy_map.get(finish_level_value, occupancy_rate)
            adjusted_margin = finish_margin_map.get(finish_level_value)
            base_revenue *= finish_rev_multiplier
            occupancy_rate = adjusted_occupancy
            if adjusted_margin is not None:
                context['restaurant_finish_margin_override'] = adjusted_margin
            context['restaurant_finish_occupancy_override'] = occupancy_rate

        # Apply quality factor and occupancy
        # Ensure no None values
        base_revenue = (base_revenue or 0) * market_factor
        quality_factor = quality_factor or 1.0
        occupancy_rate = occupancy_rate or 0.85
        
        adjusted_revenue = base_revenue * quality_factor * occupancy_rate
        
        return adjusted_revenue

    def _build_office_financials(self, square_footage: float, office_profile: Optional[Dict[str, float]]) -> Dict[str, float]:
        """
        Build a simple Class A office underwriting model using configured profile inputs.
        Returns PGI/EGI/NOI plus the major expense components so downstream callers
        can keep NOI, rent-per-SF, and margin in sync with the UI.
        """
        if not square_footage or not office_profile:
            return {}

        try:
            sf = float(square_footage)
        except (TypeError, ValueError):
            return {}
        if sf <= 0:
            return {}

        def _to_float(name: str, default: float = 0.0) -> float:
            value = office_profile.get(name, default)
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        base_rent_per_sf = _to_float("base_rent_per_sf")
        stabilized_occupancy = _to_float("stabilized_occupancy")
        vacancy_credit_pct = _to_float("vacancy_and_credit_loss_pct")
        opex_pct = _to_float("opex_pct_of_egi")

        ti_per_sf = _to_float("ti_per_sf")
        ti_amort_years = int(office_profile.get("ti_amort_years", 10) or 10)
        lc_pct_of_lease_value = _to_float("lc_pct_of_lease_value")
        lc_amort_years = int(office_profile.get("lc_amort_years", 10) or 10)

        pgi = base_rent_per_sf * sf * stabilized_occupancy
        vacancy_and_credit_loss = vacancy_credit_pct * pgi
        egi = pgi - vacancy_and_credit_loss

        opex = opex_pct * egi
        ti_amort = 0.0
        if ti_per_sf > 0 and ti_amort_years > 0:
            ti_amort = (ti_per_sf * sf) / ti_amort_years

        lc_amort = 0.0
        if lc_pct_of_lease_value > 0 and lc_amort_years > 0:
            assumed_lease_term_years = 10
            total_commissions = lc_pct_of_lease_value * pgi * assumed_lease_term_years
            lc_amort = total_commissions / lc_amort_years

        total_expenses = opex + ti_amort + lc_amort
        noi = egi - total_expenses
        noi_margin = (noi / egi) if egi > 0 else 0.0

        rent_per_sf = (pgi / sf) if sf > 0 else 0.0
        noi_per_sf = (noi / sf) if sf > 0 else 0.0

        return {
            "pgi": pgi,
            "vacancy_and_credit_loss": vacancy_and_credit_loss,
            "egi": egi,
            "opex": opex,
            "ti_amort": ti_amort,
            "lc_amort": lc_amort,
            "noi": noi,
            "noi_margin": noi_margin,
            "rent_per_sf": rent_per_sf,
            "noi_per_sf": noi_per_sf,
        }

    def _build_hospitality_financials(self, config, square_footage: float, context: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """Derive select-service hotel revenue + expense assumptions from config."""
        modifiers = context.get('modifiers') or {}

        def _first_number(*candidates) -> Optional[float]:
            for candidate in candidates:
                if candidate is None:
                    continue
                try:
                    value = float(candidate)
                except (TypeError, ValueError):
                    continue
                return value
            return None

        rooms_override = _first_number(
            context.get('rooms'),
            context.get('room_count'),
            context.get('keys'),
            modifiers.get('rooms'),
            modifiers.get('room_count'),
            modifiers.get('keys')
        )
        rooms_per_sf = getattr(config, 'rooms_per_sf', None)
        if rooms_override is not None:
            rooms = max(0.0, rooms_override)
        elif rooms_per_sf and square_footage:
            try:
                rooms = max(0.0, float(rooms_per_sf) * float(square_footage))
            except (TypeError, ValueError):
                rooms = 0.0
        else:
            rooms = 0.0

        adr_override = _first_number(
            context.get('adr'),
            context.get('average_daily_rate'),
            context.get('room_rate'),
            context.get('hotel_adr'),
            modifiers.get('adr'),
            modifiers.get('adr_override')
        )
        occupancy_override = _first_number(
            context.get('hotel_occupancy'),
            context.get('occupancy'),
            context.get('occupancy_rate_override'),
            context.get('occupancy_rate'),
            modifiers.get('occupancy'),
            modifiers.get('hotel_occupancy')
        )

        base_adr = None
        base_adr_by_market = getattr(config, 'base_adr_by_market', None)
        if isinstance(base_adr_by_market, dict):
            base_adr = (
                base_adr_by_market.get('primary')
                or next(iter(base_adr_by_market.values()), None)
            )
        base_occupancy = None
        base_occ_by_market = getattr(config, 'base_occupancy_by_market', None)
        if isinstance(base_occ_by_market, dict):
            base_occupancy = (
                base_occ_by_market.get('primary')
                or next(iter(base_occ_by_market.values()), None)
            )
        if base_occupancy is None:
            base_occupancy = getattr(config, 'occupancy_rate_base', None)

        if base_adr is None:
            annual_room_rev = getattr(config, 'base_revenue_per_room_annual', None)
            if annual_room_rev and base_occupancy:
                try:
                    base_adr = float(annual_room_rev) / (365.0 * float(base_occupancy))
                except (TypeError, ValueError, ZeroDivisionError):
                    base_adr = None

        adr = float(adr_override) if adr_override is not None else float(base_adr or 0.0)

        if occupancy_override is not None:
            occupancy = float(occupancy_override)
        else:
            occupancy = float(base_occupancy or 0.0)
        if occupancy > 1 and occupancy <= 100:
            occupancy = occupancy / 100.0
        occupancy = max(0.0, min(occupancy, 1.0))

        if rooms <= 0 or adr <= 0 or occupancy <= 0:
            annual_room_revenue = 0.0
        else:
            annual_room_revenue = rooms * adr * occupancy * 365.0

        expense_percentages = getattr(config, 'expense_percentages', None) or {}
        total_expense_pct = 0.0
        if isinstance(expense_percentages, dict):
            for value in expense_percentages.values():
                if isinstance(value, (int, float)):
                    total_expense_pct += float(value)
        if total_expense_pct <= 0:
            fallback_margin = getattr(config, 'operating_margin_base', None)
            if isinstance(fallback_margin, (int, float)) and fallback_margin > 0:
                total_expense_pct = max(0.0, 1.0 - float(fallback_margin))
        total_expense_pct = max(0.0, min(total_expense_pct, 0.95))

        total_operating_expenses = annual_room_revenue * total_expense_pct
        annual_noi = annual_room_revenue - total_operating_expenses
        noi_margin = (annual_noi / annual_room_revenue) if annual_room_revenue > 0 else 0.0

        return {
            'rooms': rooms,
            'adr': adr,
            'occupancy': occupancy,
            'annual_room_revenue': annual_room_revenue,
            'total_operating_expenses': total_operating_expenses,
            'annual_noi': annual_noi,
            'noi_margin': noi_margin,
            'expense_pct': total_expense_pct
        }

    def _get_building_enum(self, building_type_str: str):
        """Convert string building type to BuildingType enum"""
        type_map = {
            'healthcare': BuildingType.HEALTHCARE,
            'multifamily': BuildingType.MULTIFAMILY,
            'office': BuildingType.OFFICE,
            'retail': BuildingType.RETAIL,
            'restaurant': BuildingType.RESTAURANT,
            'industrial': BuildingType.INDUSTRIAL,
            'hospitality': BuildingType.HOSPITALITY,
            'educational': BuildingType.EDUCATIONAL,
            'mixed_use': BuildingType.MIXED_USE,
            'specialty': BuildingType.SPECIALTY,
            'civic': BuildingType.CIVIC,
            'recreation': BuildingType.RECREATION,
            'parking': BuildingType.PARKING
        }
        return type_map.get(building_type_str.lower())

    def _empty_ownership_analysis(self):
        """Return empty ownership analysis structure"""
        return {
            'revenue_analysis': {
                'annual_revenue': 0,
                'revenue_per_sf': 0,
                'operating_margin': 0,
                'net_income': 0,
                'occupancy_rate': 0,
                'quality_factor': 1.0,
                'is_premium': False
            },
            'return_metrics': {
                'estimated_annual_noi': 0,
                'cash_on_cash_return': 0,
                'cap_rate': 0,
                'npv': 0,
                'irr': 0,
                'payback_period': 999
            },
            'revenue_requirements': {
                'required_value': 0,
                'metric_name': 'Annual Revenue Required',
                'target_roi': 0,
                'operating_margin': 0,
                'break_even_revenue': 0,
                'required_monthly': 0
            },
            'operational_efficiency': {
                'total_expenses': 0,
                'operating_margin': 0,
                'efficiency_score': 0,
                'expense_ratio': 0
            }
        }

    def get_exit_cap_and_discount_rate(self, building_type) -> Tuple[float, float]:
        """
        Simple fallback mapping for exit cap and discount rate by building type.
        This keeps assumptions centralized until we migrate them into master_config.
        """
        exit_cap = 0.07
        discount_rate = 0.08

        try:
            bt_name = building_type.name.upper()
        except AttributeError:
            bt_name = str(building_type).upper()

        if "MULTIFAMILY" in bt_name:
            exit_cap = 0.055
            discount_rate = 0.075
        elif "INDUSTRIAL" in bt_name or "WAREHOUSE" in bt_name:
            exit_cap = 0.0675
            discount_rate = 0.08
        elif "OFFICE" in bt_name:
            # Class A office assumptions calibrated for strong urban markets.
            exit_cap = 0.0675
            discount_rate = 0.0825
        elif "HOSPITALITY" in bt_name or "HOTEL" in bt_name:
            # Select-service hotel underwriting assumptions
            exit_cap = 0.085
            discount_rate = 0.10

        return exit_cap, discount_rate

    def build_unlevered_cashflows_with_exit(
        self,
        total_project_cost: float,
        annual_noi: float,
        years: int,
        exit_cap_rate: float,
    ) -> List[float]:
        """
        Build a standard unlevered cashflow stream for IRR/NPV with a terminal value.
        Year 0: negative total project cost
        Years 1..years-1: stabilized NOI
        Year `years`: NOI + sale proceeds (NOI / exit cap)
        """
        if total_project_cost is None or annual_noi is None:
            return []

        try:
            total_cost_value = float(total_project_cost)
            noi_value = float(annual_noi)
        except (TypeError, ValueError):
            return []

        try:
            years_int = int(years)
        except (TypeError, ValueError):
            years_int = 10

        years_int = years_int if years_int > 0 else 10

        cashflows: List[float] = [-total_cost_value]

        # Intermediate years receive stabilized NOI
        for _ in range(max(years_int - 1, 0)):
            cashflows.append(noi_value)

        terminal_value = noi_value / float(exit_cap_rate) if exit_cap_rate and exit_cap_rate > 0 else 0.0
        cashflows.append(noi_value + terminal_value)
        return cashflows
    
    def calculate_npv(self, initial_investment: float, annual_cash_flow: float, 
                      years: int, discount_rate: float, cashflows: Optional[List[float]] = None) -> float:
        """Calculate Net Present Value using discount rate from config"""
        if cashflows:
            npv = 0.0
            rate = discount_rate if isinstance(discount_rate, (int, float)) else 0.0
            for year, cashflow in enumerate(cashflows):
                if year == 0:
                    npv += cashflow
                else:
                    npv += cashflow / ((1 + rate) ** year)
            return round(npv, 2)

        npv = -initial_investment
        for year in range(1, years + 1):
            npv += annual_cash_flow / ((1 + discount_rate) ** year)
        return round(npv, 2)

    def calculate_irr(self, initial_investment: float, annual_cash_flow: float, 
                      years: int = 10, cashflows: Optional[List[float]] = None) -> float:
        """Calculate Internal Rate of Return using Newton-Raphson approximation"""
        if cashflows:
            rate = 0.1
            for _ in range(50):
                npv = 0.0
                dnpv = 0.0
                for year, cashflow in enumerate(cashflows):
                    if year == 0:
                        npv += cashflow
                        continue
                    npv += cashflow / ((1 + rate) ** year)
                    dnpv -= year * cashflow / ((1 + rate) ** (year + 1))
                if abs(npv) < 0.01:
                    break
                if dnpv == 0:
                    break
                rate = rate - npv / dnpv
                if rate < -0.99:
                    rate = -0.99
                elif rate > 10:
                    rate = 10
            return round(rate, 4)

        # Simple approximation for constant cash flows
        if annual_cash_flow <= 0 or initial_investment <= 0:
            return 0.0
        
        # Newton-Raphson method for IRR
        rate = 0.1  # Initial guess
        for _ in range(20):  # Max iterations
            npv = -initial_investment
            dnpv = 0
            for year in range(1, years + 1):
                npv += annual_cash_flow / ((1 + rate) ** year)
                dnpv -= year * annual_cash_flow / ((1 + rate) ** (year + 1))
            
            if abs(npv) < 0.01:  # Converged
                break
            
            rate = rate - npv / dnpv if dnpv != 0 else rate
        
        return round(rate, 4)
    
    def calculate_irr_with_terminal_value(self, initial_investment: float, annual_cash_flow: float,
                                         terminal_value: float, years: int = 10) -> float:
        """
        Calculate IRR including terminal value (property sale) at end of investment period.
        Used for real estate investments where property value is realized at exit.
        """
        if initial_investment <= 0:
            return 0.0

        try:
            total_cost_value = float(initial_investment)
            noi_value = float(annual_cash_flow)
            terminal_value = float(terminal_value) if terminal_value is not None else 0.0
        except (TypeError, ValueError):
            return 0.0

        try:
            years_int = int(years)
        except (TypeError, ValueError):
            years_int = 10

        years_int = years_int if years_int > 0 else 10
        cashflows = [-total_cost_value]
        for _ in range(max(years_int - 1, 0)):
            cashflows.append(noi_value)
        cashflows.append(noi_value + terminal_value)

        return self.calculate_irr(
            initial_investment=total_cost_value,
            annual_cash_flow=noi_value,
            years=years_int,
            cashflows=cashflows
        )

    def calculate_revenue_requirements(
        self,
        total_cost: float,
        config,
        square_footage: float,
        actual_annual_revenue: float = 0,
        actual_net_income: float = 0,
        margin_pct: Optional[float] = None
    ) -> dict:
        """
        Calculate revenue requirements comparing actual projected returns to required returns.
        This determines true feasibility based on whether the project meets ROI targets.
        """
        
        # Target ROI (use config if available, otherwise default)
        target_roi = getattr(config, 'target_roi', 0.08)
        
        # Calculate required annual return (what investor needs)
        required_annual_return = total_cost * target_roi
        
        # Use ACTUAL projected revenue and profit from the project
        # This is what the project will actually generate
        
        # For feasibility, compare actual profit to required return
        # NOT theoretical market capacity
        if actual_net_income > 0:
            gap = actual_net_income - required_annual_return
            gap_percentage = (gap / required_annual_return) * 100 if required_annual_return > 0 else 0
            
            # Feasibility based on whether actual returns meet requirements
            if gap >= 0:
                feasibility = 'Feasible'
            elif gap >= -required_annual_return * 0.2:  # Within 20% of target
                feasibility = 'Marginal'
            else:
                feasibility = 'Not Feasible'
        else:
            gap = -required_annual_return
            gap_percentage = -100
            feasibility = 'Not Feasible'
        
        # Normalize operating margin using provided margin or config hints
        normalized_margin = margin_pct
        if normalized_margin is None and getattr(config, 'operating_margin_base', None) is not None:
            normalized_margin = getattr(config, 'operating_margin_base')
        if normalized_margin is None and getattr(config, 'financial_metrics', None):
            normalized_margin = config.financial_metrics.get('operating_margin')
        if normalized_margin is None and getattr(config, 'operating_margin_premium', None) is not None:
            normalized_margin = getattr(config, 'operating_margin_premium')
        if normalized_margin is None:
            normalized_margin = 0.20
        normalized_margin = max(0.05, min(0.40, normalized_margin))
        operating_margin = normalized_margin
        
        # Simple payback calculation using actual net income
        simple_payback_years = round(total_cost / actual_net_income, 1) if actual_net_income > 0 else 999
        
        # ALWAYS return this exact structure
        # The Revenue Requirements card expects these exact fields
        return {
            # Core fields for Revenue Requirements card
            'required_value': round(required_annual_return, 2),
            'market_value': round(actual_annual_revenue, 2),  # Now shows actual projected revenue
            'feasibility': feasibility,
            'gap': round(gap, 2),
            'gap_percentage': round(gap_percentage, 1),
            
            # Additional fields for debugging/clarity
            'actual_net_income': round(actual_net_income, 2),
            
            # Additional display fields
            'metric_name': 'Annual Return Required',
            'required_revenue_per_sf': round(required_annual_return / square_footage, 2) if square_footage > 0 else 0,
            'actual_revenue_per_sf': round(actual_annual_revenue / square_footage, 2) if square_footage > 0 else 0,
            'target_roi': target_roi,
            'operating_margin': round(operating_margin, 3),
            'break_even_revenue': round(total_cost * 0.1, 2),  # Simple 10% of cost
            'required_monthly': round(required_annual_return / 12, 2),
            
            # Simple payback for the card
            'simple_payback_years': simple_payback_years,
            
            # Detailed feasibility for additional context
            'feasibility_detail': {
                'status': feasibility,
                'gap': round(gap, 2),
                'recommendation': self._get_revenue_feasibility_recommendation(gap, square_footage)
            }
        }

    def calculate_operational_metrics_for_display(self, building_type: str, subtype: str, 
                                                 operational_efficiency: dict, 
                                                 square_footage: float, 
                                                 annual_revenue: float, 
                                                 units: int = 0) -> dict:
        """
        Calculate display-ready operational metrics based on building type.
        Returns formatted metrics ready for frontend display.
        """
        
        # Base metrics all building types have
        operational_metrics = {
            'staffing': [],
            'revenue': {},
            'kpis': []
        }
        
        # SAFETY CHECK - Handle None/empty operational_efficiency
        if not operational_efficiency:
            return operational_metrics
        
        # SAFETY CHECK - Ensure numeric values aren't None
        annual_revenue = float(annual_revenue or 0)
        square_footage = float(square_footage or 1)  # Avoid division by zero
        units = int(units or 0)
        
        # Get data from operational_efficiency with safe defaults
        labor_cost = float(operational_efficiency.get('labor_cost', 0) or 0)
        total_expenses = float(operational_efficiency.get('total_expenses', 0) or 0)
        operating_margin = float(operational_efficiency.get('operating_margin', 0) or 0)
        efficiency_score = float(operational_efficiency.get('efficiency_score', 0) or 0)
        expense_ratio = float(operational_efficiency.get('expense_ratio', 0) or 0)
        
        # Building-type specific metrics
        if building_type == 'restaurant':
            food_cost = float(operational_efficiency.get('food_cost', 0) or 0)
            beverage_cost = float(operational_efficiency.get('beverage_cost', 0) or 0)
            
            # Calculate restaurant-specific metrics
            food_cost_ratio = (food_cost / annual_revenue) if annual_revenue > 0 else 0
            labor_cost_ratio = (labor_cost / annual_revenue) if annual_revenue > 0 else 0
            prime_cost_ratio = food_cost_ratio + labor_cost_ratio
            
            operational_metrics['staffing'] = [
                {'label': 'Labor Cost', 'value': f'${labor_cost:,.0f}'},
                {'label': 'Labor % of Revenue', 'value': f'{labor_cost_ratio * 100:.1f}%'}
            ]
            
            operational_metrics['revenue'] = {
                'Food Cost': f'{food_cost_ratio * 100:.1f}%',
                'Beverage Cost': f'{(beverage_cost / annual_revenue * 100):.1f}%' if annual_revenue > 0 else '0%',
                'Labor Cost': f'{labor_cost_ratio * 100:.1f}%',
                'Operating Margin': f'{operating_margin * 100:.1f}%'
            }
            
            operational_metrics['kpis'] = [
                {
                    'label': 'Food Cost Ratio',
                    'value': f'{food_cost_ratio * 100:.0f}%',
                    'color': 'green' if (food_cost_ratio or 0) < 0.28 else 'yellow' if (food_cost_ratio or 0) < 0.32 else 'red'
                },
                {
                    'label': 'Prime Cost',
                    'value': f'{prime_cost_ratio * 100:.0f}%',
                    'color': 'green' if (prime_cost_ratio or 0) < 0.60 else 'yellow' if (prime_cost_ratio or 0) < 0.65 else 'red'
                },
                {
                    'label': 'Efficiency',
                    'value': f'{efficiency_score:.0f}%',
                    'color': 'green' if (efficiency_score or 0) > 15 else 'yellow' if (efficiency_score or 0) > 10 else 'red'
                }
            ]
            
        elif building_type == 'healthcare':
            subtype_value = (
                operational_efficiency.get('building_subtype')
                or operational_efficiency.get('subtype')
                or subtype
            )
            if subtype_value in ('outpatient_clinic', 'urgent_care'):
                is_urgent_care = subtype_value == 'urgent_care'
                exam_rooms = units
                if not exam_rooms:
                    if square_footage and square_footage > 0:
                        if is_urgent_care:
                            exam_rooms = max(1, round(square_footage / 450))
                        else:
                            exam_rooms = max(1, round(square_footage / 650))
                    else:
                        exam_rooms = 1
                avg_reimbursement = 150.0 if is_urgent_care else 120.0
                visits_per_year = annual_revenue / avg_reimbursement if annual_revenue and avg_reimbursement else 0
                visits_per_day = visits_per_year / 260 if visits_per_year else 0
                providers = max(1, round(visits_per_day / 20)) if visits_per_day else 1
                support_staff = providers
                room_capacity_per_day = 14.0 if is_urgent_care else 10.0
                max_visits_capacity = exam_rooms * room_capacity_per_day if exam_rooms else 0
                utilization_pct = (visits_per_day / max_visits_capacity * 100.0) if max_visits_capacity else 0
                
                operational_metrics['staffing'] = [
                    {'label': 'Providers (MD/DO/NP/PA)', 'value': str(providers)},
                    {'label': 'Support Staff (MAs)', 'value': str(support_staff)},
                    {'label': 'Exam Rooms', 'value': str(exam_rooms)}
                ]
                
                revenue_per_provider = annual_revenue / providers if providers else None
                revenue_per_room = annual_revenue / exam_rooms if exam_rooms else None
                revenue_per_sf = annual_revenue / square_footage if square_footage else None
                labor_ratio_pct = (labor_cost / annual_revenue * 100.0) if annual_revenue else None
                revenue_block = {}
                if revenue_per_provider is not None:
                    revenue_block['Revenue per Provider'] = f'${revenue_per_provider:,.0f}'
                if revenue_per_room is not None:
                    revenue_block['Revenue per Exam Room'] = f'${revenue_per_room:,.0f}'
                if revenue_per_sf is not None:
                    revenue_block['Revenue per SF'] = f'${revenue_per_sf:,.0f}'
                if labor_ratio_pct is not None:
                    revenue_block['Labor Cost Ratio'] = f'{labor_ratio_pct:.0f}%'
                revenue_block['Operating Margin'] = f'{operating_margin * 100:.1f}%'
                operational_metrics['revenue'] = revenue_block
                
                kpis = []
                if visits_per_day:
                    kpis.append({
                        'label': 'Total Visits / Day',
                        'value': f'{visits_per_day:,.1f}',
                        'color': 'green' if visits_per_day > 60 else 'yellow'
                    })
                if providers and visits_per_day:
                    visits_per_provider = visits_per_day / providers
                    kpis.append({
                        'label': 'Visits / Provider / Day',
                        'value': f'{visits_per_provider:,.1f}',
                        'color': 'green' if 18 <= visits_per_provider <= 24 else 'yellow'
                    })
                kpis.append({
                    'label': 'Exam Room Utilization',
                    'value': f'{utilization_pct:.0f}%',
                    'color': 'green' if utilization_pct >= 75 else 'yellow' if utilization_pct >= 60 else 'red'
                })
                operational_metrics['kpis'] = kpis
            else:
                beds = round(square_footage / 600)
                nursing_fte = round(labor_cost * 0.4 / 75000) if labor_cost > 0 else 1
                total_fte = round(labor_cost / 60000) if labor_cost > 0 else 1
                operational_metrics['staffing'] = [
                    {'label': 'Total FTEs Required', 'value': str(total_fte)},
                    {'label': 'Beds per Nurse', 'value': f'{beds / nursing_fte:.1f}' if nursing_fte > 0 else 'N/A'}
                ]
                operational_metrics['revenue'] = {
                    'Revenue per Employee': f'${annual_revenue / total_fte:,.0f}' if total_fte > 0 else 'N/A',
                    'Revenue per Bed': f'${annual_revenue / beds:,.0f}' if beds > 0 else 'N/A',
                    'Labor Cost Ratio': f'{(labor_cost / annual_revenue * 100):.0f}%' if annual_revenue > 0 else 'N/A',
                    'Operating Margin': f'{operating_margin * 100:.1f}%'
                }
                operational_metrics['kpis'] = [
                    {'label': 'ALOS Target', 'value': '3.8 days', 'color': 'green'},
                    {'label': 'Occupancy', 'value': '85%', 'color': 'green'},
                    {'label': 'Efficiency', 'value': f'{efficiency_score:.0f}%',
                     'color': 'green' if (efficiency_score or 0) > 20 else 'yellow' if (efficiency_score or 0) > 15 else 'red'}
                ]
            
        elif building_type == 'multifamily':
            # Use units if provided, otherwise estimate
            if units == 0:
                units = round(square_footage / 1000)  # Average apartment size
            
            units_per_manager = 50  # Industry standard
            maintenance_staff = max(1, round(units / 30))  # 1 per 30 units
            
            operational_metrics['staffing'] = [
                {'label': 'Units per Manager', 'value': str(units_per_manager)},
                {'label': 'Maintenance Staff', 'value': str(maintenance_staff)}
            ]
            
            operational_metrics['revenue'] = {
                'Revenue per Unit': f'${annual_revenue / units:,.0f}/yr' if units > 0 else 'N/A',
                'Average Rent': f'${annual_revenue / units / 12:,.0f}/mo' if units > 0 else 'N/A',
                'Occupancy Target': '93%',
                'Operating Margin': f'{operating_margin * 100:.1f}%'
            }
            
            operational_metrics['kpis'] = [
                {
                    'label': 'NOI Margin',
                    'value': f'{operating_margin * 100:.0f}%',
                    'color': 'green' if (operating_margin or 0) > 0.60 else 'yellow' if (operating_margin or 0) > 0.50 else 'red'
                },
                {
                    'label': 'Expense Ratio',
                    'value': f'{expense_ratio * 100:.0f}%',
                    'color': 'green' if (expense_ratio or 0) < 0.40 else 'yellow' if (expense_ratio or 0) < 0.50 else 'red'
                }
            ]
            
        elif building_type == 'office':
            property_mgmt_staffing = float(
                operational_efficiency.get('property_mgmt_staffing', operational_efficiency.get('management_fee', 0)) or 0
            )
            maintenance_staffing = float(
                operational_efficiency.get('maintenance_staffing', operational_efficiency.get('maintenance_cost', 0)) or 0
            )
            cam_charges = float(operational_efficiency.get('cam_charges', 0) or 0)
            rent_per_sf = (annual_revenue / square_footage) if square_footage > 0 else 0
            operating_expenses_per_sf = (total_expenses / square_footage) if square_footage > 0 else 0
            cam_per_sf = (cam_charges / square_footage) if square_footage > 0 else 0

            operational_metrics['staffing'] = [
                {'label': 'Property Mgmt', 'value': f'${property_mgmt_staffing:,.0f}'},
                {'label': 'Maintenance', 'value': f'${maintenance_staffing:,.0f}'}
            ]
            
            operational_metrics['revenue'] = {
                'Rent per SF': f'${rent_per_sf:.2f}/yr' if square_footage > 0 else 'N/A',
                'Operating Expenses': f'${total_expenses:,.0f} (${operating_expenses_per_sf:.2f}/SF)',
                'CAM Charges': (
                    f'${cam_charges:,.0f} (${cam_per_sf:.2f}/SF)' if cam_charges > 0 and square_footage > 0 else 'Included in lease'
                ),
                'Operating Margin': f'{operating_margin * 100:.1f}%'
            }
            
            operational_metrics['kpis'] = [
                {
                    'label': 'Efficiency',
                    'value': f'{efficiency_score:.0f}%',
                    'color': 'green' if (efficiency_score or 0) > 15 else 'yellow' if (efficiency_score or 0) > 10 else 'red'
                },
                {
                    'label': 'Expense/SF',
                    'value': f'${operating_expenses_per_sf:.2f}' if square_footage > 0 else 'N/A',
                    'color': 'yellow'
                }
            ]
            
        else:
            # Generic metrics for other building types
            operational_metrics['staffing'] = [
                {'label': 'Labor Cost', 'value': f'${labor_cost:,.0f}'},
                {'label': 'Management', 'value': f'${operational_efficiency.get("management_fee", 0):,.0f}'}
            ]
            
            operational_metrics['revenue'] = {
                'Total Expenses': f'${total_expenses:,.0f}',
                'Operating Margin': f'{operating_margin * 100:.1f}%',
                'Efficiency Score': f'{efficiency_score:.0f}%'
            }
            
            operational_metrics['kpis'] = [
                {
                    'label': 'Expense Ratio',
                    'value': f'{expense_ratio * 100:.0f}%',
                    'color': 'green' if (expense_ratio or 0) < 0.80 else 'yellow' if (expense_ratio or 0) < 0.90 else 'red'
                }
            ]
        
        return operational_metrics

    def calculate_operational_efficiency(
        self,
        revenue: float,
        config,
        subtype: str = None,
        margin_pct: Optional[float] = None,
        total_expenses_override: Optional[float] = None
    ) -> dict:
        """Calculate operational efficiency metrics from config ratios and normalized margin."""
        result = {
            'total_expenses': 0,
            'operating_margin': 0,
            'efficiency_score': 0,
            'expense_ratio': 0
        }
        
        # For manufacturing, separate facility expenses from business operations
        exclude_from_facility_opex = []
        if subtype == 'manufacturing':
            # These are business operations, not real estate facility expenses
            exclude_from_facility_opex = ['labor_cost_ratio', 'raw_materials_ratio']
        
        # Calculate each expense category from config
        expense_mappings = [
            ('labor_cost', 'labor_cost_ratio'),
            ('utility_cost', 'utility_cost_ratio'),
            ('maintenance_cost', 'maintenance_cost_ratio'),
            ('management_fee', 'management_fee_ratio'),
            ('insurance_cost', 'insurance_cost_ratio'),
            ('property_tax', 'property_tax_ratio'),
            ('supply_cost', 'supply_cost_ratio'),
            ('food_cost', 'food_cost_ratio'),
            ('beverage_cost', 'beverage_cost_ratio'),
            ('franchise_fee', 'franchise_fee_ratio'),
            ('equipment_lease', 'equipment_lease_ratio'),
            ('marketing_cost', 'marketing_ratio'),
            ('reserves', 'reserves_ratio'),
            ('security', 'security_ratio'),
            ('supplies', 'supplies_ratio'),
            ('janitorial', 'janitorial_ratio'),
            ('rooms_operations', 'rooms_operations_ratio'),
            ('food_beverage', 'food_beverage_ratio'),
            ('sales_marketing', 'sales_marketing_ratio'),
            ('floor_plan_interest', 'floor_plan_interest_ratio'),
            ('materials', 'materials_ratio'),
            ('raw_materials', 'raw_materials_ratio'),  # Added this mapping
            ('program_costs', 'program_costs_ratio'),
            ('equipment', 'equipment_ratio'),
            ('chemicals', 'chemicals_ratio'),
            ('event_costs', 'event_costs_ratio'),
            ('software_fees', 'software_fees_ratio'),
            ('other_expenses', 'other_expenses_ratio'),
            ('monitoring_cost', 'monitoring_cost_ratio'),  # Added for cold storage
            ('connectivity', 'connectivity_ratio'),  # Added for data center
        ]
        
        # Calculate expenses
        expense_details = {}
        raw_total_expenses = 0
        for name, attr in expense_mappings:
            # Skip business operation expenses for manufacturing
            if attr in exclude_from_facility_opex:
                continue
                
            if hasattr(config, attr):
                ratio = getattr(config, attr)
                if ratio and ratio > 0:
                    cost = revenue * ratio
                    expense_details[name] = cost
                    raw_total_expenses += cost

        # Determine target expenses based on provided overrides or margin
        if total_expenses_override is not None:
            target_total_expenses = round(total_expenses_override, 2)
        elif margin_pct is not None and revenue > 0:
            target_total_expenses = round(revenue * (1 - margin_pct), 2)
        else:
            target_total_expenses = round(raw_total_expenses, 2)

        # Scale detailed expenses to match the normalized total
        if raw_total_expenses > 0 and target_total_expenses > 0:
            scale_factor = target_total_expenses / raw_total_expenses
            scaled_sum = 0
            for key, value in expense_details.items():
                scaled_value = round(value * scale_factor, 2)
                expense_details[key] = scaled_value
                scaled_sum += scaled_value

            # Adjust for rounding drift by applying difference to the first key
            adjustment = round(target_total_expenses - scaled_sum, 2)
            if adjustment and expense_details:
                first_key = next(iter(expense_details))
                expense_details[first_key] = round(expense_details[first_key] + adjustment, 2)
        elif not expense_details and target_total_expenses > 0:
            # If no detailed breakdown but expenses exist, record as generic operating expense
            expense_details['operating_expenses'] = target_total_expenses

        result.update({key: value for key, value in expense_details.items()})
        result['total_expenses'] = target_total_expenses

        if revenue > 0:
            normalized_margin = margin_pct if margin_pct is not None else (1 - (target_total_expenses / revenue))
            normalized_margin = max(0.0, normalized_margin)
            result['operating_margin'] = round(normalized_margin, 3)
            result['efficiency_score'] = round(normalized_margin * 100, 1)
            result['expense_ratio'] = round(1 - normalized_margin, 3)
        else:
            result['operating_margin'] = round(margin_pct or 0, 3) if margin_pct is not None else 0
            result['efficiency_score'] = 0
            result['expense_ratio'] = 0
        
        return result
    
    def get_available_building_types(self) -> Dict[str, List[str]]:
        """
        Get all available building types and their subtypes
        
        Returns:
            Dictionary mapping building types to their subtypes
        """
        available = {}
        for building_type in BuildingType:
            if building_type in self.config:
                available[building_type.value] = list(self.config[building_type].keys())
        return available
    
    def get_building_details(self, building_type: BuildingType, subtype: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed configuration for a specific building type/subtype
        
        Args:
            building_type: Type from BuildingType enum
            subtype: Specific subtype
            
        Returns:
            Building configuration details or None if not found
        """
        config = get_building_config(building_type, subtype)
        if not config:
            return None
            
        # Convert to dictionary for easier consumption
        return {
            'display_name': config.display_name,
            'base_cost_per_sf': config.base_cost_per_sf,
            'cost_range': config.cost_range,
            'equipment_cost_per_sf': config.equipment_cost_per_sf,
            'typical_floors': config.typical_floors,
            'trades': asdict(config.trades),
            'soft_costs': asdict(config.soft_costs),
            'ownership_types': list(config.ownership_types.keys()),
            'special_features': list(config.special_features.keys()) if config.special_features else [],
            'nlp_keywords': config.nlp.keywords,
            'regional_multipliers': config.regional_multipliers
        }
    
    def estimate_from_description(self, 
                                 description: str,
                                 square_footage: float,
                                 location: str = "Nashville",
                                 finish_level: Optional[str] = None) -> Dict[str, Any]:
        """
        Estimate costs from a natural language description
        
        Args:
            description: Natural language project description
            square_footage: Total square footage
            location: City/location for regional multiplier
            finish_level: Optional explicit finish level override
            
        Returns:
            Cost estimate with detected building type
        """
        # Detect building type from description
        detection = detect_building_type_with_method(description)

        if not detection:
            return {
                'error': 'Could not detect building type from description',
                'description': description
            }
        
        building_type, subtype, detection_method = detection
        
        # Detect project class from keywords
        description_lower = description.lower()
        if 'renovation' in description_lower or 'remodel' in description_lower:
            project_class = ProjectClass.RENOVATION
        elif 'addition' in description_lower or 'expansion' in description_lower:
            project_class = ProjectClass.ADDITION
        elif 'tenant improvement' in description_lower or 'ti' in description_lower:
            project_class = ProjectClass.TENANT_IMPROVEMENT
        else:
            project_class = ProjectClass.GROUND_UP
        
        inferred_finish_level, explicit_factor = infer_finish_level(description)
        finish_source = 'default'
        finish_for_calculation: Optional[str] = None

        if finish_level:
            finish_for_calculation = finish_level
            finish_source = 'explicit'
        elif inferred_finish_level:
            finish_for_calculation = inferred_finish_level
            finish_source = 'description'

        # Calculate with detected parameters
        result = self.calculate_project(
            building_type=building_type,
            subtype=subtype,
            square_footage=square_footage,
            location=location,
            project_class=project_class,
            finish_level=finish_for_calculation,
            finish_level_source=finish_source
        )

        self._log_trace("nlp_detected", {
            'building_type': building_type.value,
            'subtype': subtype,
            'method': detection_method
        })

        if inferred_finish_level or explicit_factor is not None:
            self._log_trace("finish_level_inferred", {
                'from': 'description',
                'finish_level': inferred_finish_level,
                'explicit_factor': explicit_factor
            })
        if explicit_factor is not None:
            self._log_trace("finish_factor_inferred", {
                'factor': explicit_factor
            })
        
        # Add detection info
        result['detection_info'] = {
            'detected_type': building_type.value,
            'detected_subtype': subtype,
            'detected_class': project_class.value,
            'original_description': description,
            'method': detection_method
        }
        
        return result
    
    # REMOVED DUPLICATE calculate_revenue_requirements - using the one at line 710
    # REMOVED DUPLICATE calculate_operational_efficiency - using the one at line 977
    
    def get_market_rate(self, building_type: str, subtype: str, location: str, 
                        rate_type: str, default_rate: float) -> float:
        """
        Get market-specific rates based on location.
        """
        context = resolve_location_context(location or "")
        multiplier = context.get('market_factor', context.get('multiplier', 1.0))
        
        # Apply multiplier to default rate
        adjusted_rate = default_rate * multiplier
        
        # Add some variance based on building quality/class
        if 'luxury' in subtype.lower() or 'class_a' in subtype.lower():
            adjusted_rate *= 1.15
        elif 'affordable' in subtype.lower() or 'class_c' in subtype.lower():
            adjusted_rate *= 0.75
        
        return adjusted_rate
    
    def format_financial_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the financial requirements for display.
        Add visual indicators and recommendations.
        """
        if not requirements:
            return {}
        
        # Add visual status indicators
        feasibility = requirements.get('feasibility', {}).get('status', 'Unknown')
        
        if feasibility == 'Feasible':
            requirements['overall_status'] = {
                'status': 'success',
                'message': 'Market rates support project requirements',
                'icon': '✅'
            }
        elif 'Optimization' in feasibility:
            requirements['overall_status'] = {
                'status': 'warning',
                'message': 'Consider value engineering or phasing',
                'icon': '⚠️'
            }
        else:
            requirements['overall_status'] = {
                'status': 'error',
                'message': 'Significant gap between cost and market',
                'icon': '❌'
            }
        
        return requirements
    
    def _get_revenue_feasibility_recommendation(self, gap: float, square_footage: float) -> str:
        """Generate feasibility recommendations for revenue requirements."""
        if gap >= 0:
            return "Project meets market revenue expectations"
        elif abs(gap) < 1000000:
            return "Minor revenue optimization needed through operational efficiency"
        elif abs(gap) < 5000000:
            return "Consider phased development or value engineering to reduce costs"
        else:
            return "Significant restructuring required to achieve feasibility"
    
    def _get_feasibility_recommendation(self, gap: float, unit_type: str) -> str:
        """Generate feasibility recommendations based on gap analysis."""
        if gap <= 0:
            return f"Project is financially feasible at current market rates"
        elif gap < 1000000:
            return f"Minor optimization needed: Consider value engineering or phasing"
        elif gap < 5000000:
            return f"Moderate gap: Explore alternative financing or reduce scope"
        else:
            return f"Significant feasibility gap: Major restructuring required"
    
    def _get_efficiency_rating(self, score: float) -> str:
        """Convert efficiency score to rating."""
        if score >= 90:
            return 'Excellent'
        elif score >= 75:
            return 'Good'
        elif score >= 60:
            return 'Average'
        elif score >= 45:
            return 'Below Average'
        else:
            return 'Poor'
    
    def _get_efficiency_recommendations(self, score: float) -> List[str]:
        """Generate efficiency recommendations based on score."""
        recommendations = []
        
        if score < 60:
            recommendations.append("Consider operational improvements to increase efficiency")
            recommendations.append("Review staffing levels and automation opportunities")
        elif score < 75:
            recommendations.append("Explore revenue optimization strategies")
            recommendations.append("Benchmark against industry best practices")
        elif score < 90:
            recommendations.append("Minor optimizations could improve margins")
            recommendations.append("Consider premium service offerings")
        else:
            recommendations.append("Maintain current operational excellence")
            recommendations.append("Share best practices across portfolio")
        
        return recommendations

    # REMOVED calculate_financial_requirements - was only partially implemented for hospital
    # This feature should be rebuilt properly after launch based on user needs
    
    # REMOVED DUPLICATE get_market_rate - using the one at line 1134
    
    # REMOVED assess_feasibility - was part of financial requirements feature
    # This was only partially implemented and should be rebuilt properly after launch

# Create a singleton instance
unified_engine = UnifiedEngine()
