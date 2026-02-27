"""DealShield tile profiles for industrial types."""

DEALSHIELD_TILE_DEFAULTS = {
    "warehouse": "industrial_warehouse_v1",
    "distribution_center": "industrial_distribution_center_v1",
    "manufacturing": "industrial_manufacturing_v1",
    "flex_space": "industrial_flex_space_v1",
    "cold_storage": "industrial_cold_storage_v1",
}


INDUSTRIAL_DECISION_TABLE_COLUMNS = [
    {
        "id": "total_cost",
        "label": "Total Project Cost",
        "metric_ref": "totals.total_project_cost",
    },
    {
        "id": "annual_revenue",
        "label": "Annual Revenue",
        "metric_ref": "revenue_analysis.annual_revenue",
    },
    {
        "id": "noi",
        "label": "NOI",
        "metric_ref": "return_metrics.estimated_annual_noi",
    },
    {
        "id": "dscr",
        "label": "Debt Lens: DSCR",
        "metric_ref": "ownership_analysis.debt_metrics.calculated_dscr",
    },
    {
        "id": "yoc",
        "label": "Yield on Cost",
        "metric_ref": "ownership_analysis.yield_on_cost",
    },
]


DEALSHIELD_TILE_PROFILES = {
    "industrial_warehouse_v1": {
        "version": "v1",
        "decision_table_columns": INDUSTRIAL_DECISION_TABLE_COLUMNS,
        "tiles": [
            {
                "tile_id": "cost_plus_10",
                "label": "Cost +10%",
                "metric_ref": "totals.total_project_cost",
                "required": True,
                "transform": {"op": "mul", "value": 1.10},
            },
            {
                "tile_id": "revenue_minus_10",
                "label": "Revenue -10%",
                "metric_ref": "revenue_analysis.annual_revenue",
                "required": True,
                "transform": {"op": "mul", "value": 0.90},
            },
            {
                "tile_id": "structural_plus_10",
                "label": "Structural +10%",
                "metric_ref": "trade_breakdown.structural",
                "required": False,
                "transform": {"op": "mul", "value": 1.10},
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
                "plus_tiles": ["structural_plus_10"],
            },
        ],
        "provenance": {"notes": "Industrial warehouse tile profile v1."},
    },
    "industrial_distribution_center_v1": {
        "version": "v1",
        "decision_table_columns": INDUSTRIAL_DECISION_TABLE_COLUMNS,
        "tiles": [
            {
                "tile_id": "cost_plus_10",
                "label": "Cost +10%",
                "metric_ref": "totals.total_project_cost",
                "required": True,
                "transform": {"op": "mul", "value": 1.10},
            },
            {
                "tile_id": "revenue_minus_10",
                "label": "Revenue -10%",
                "metric_ref": "revenue_analysis.annual_revenue",
                "required": True,
                "transform": {"op": "mul", "value": 0.90},
            },
            {
                "tile_id": "electrical_plus_10",
                "label": "Electrical +10%",
                "metric_ref": "trade_breakdown.electrical",
                "required": False,
                "transform": {"op": "mul", "value": 1.10},
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
                "plus_tiles": ["electrical_plus_10"],
            },
        ],
        "provenance": {"notes": "Industrial distribution center tile profile v1."},
    },
    "industrial_manufacturing_v1": {
        "version": "v1",
        "decision_table_columns": INDUSTRIAL_DECISION_TABLE_COLUMNS,
        "tiles": [
            {
                "tile_id": "cost_plus_10",
                "label": "Cost +10%",
                "metric_ref": "totals.total_project_cost",
                "required": True,
                "transform": {"op": "mul", "value": 1.10},
            },
            {
                "tile_id": "revenue_minus_10",
                "label": "Revenue -10%",
                "metric_ref": "revenue_analysis.annual_revenue",
                "required": True,
                "transform": {"op": "mul", "value": 0.90},
            },
            {
                "tile_id": "process_mep_plus_10",
                "label": "Process MEP +10%",
                "metric_ref": "trade_breakdown.mechanical",
                "required": False,
                "transform": {"op": "mul", "value": 1.10},
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
                "plus_tiles": ["process_mep_plus_10"],
            },
        ],
        "provenance": {"notes": "Industrial manufacturing tile profile v1."},
    },
    "industrial_flex_space_v1": {
        "version": "v1",
        "decision_table_columns": INDUSTRIAL_DECISION_TABLE_COLUMNS,
        "tiles": [
            {
                "tile_id": "cost_plus_10",
                "label": "Cost +10%",
                "metric_ref": "totals.total_project_cost",
                "required": True,
                "transform": {"op": "mul", "value": 1.10},
            },
            {
                "tile_id": "revenue_minus_10",
                "label": "Revenue -10%",
                "metric_ref": "revenue_analysis.annual_revenue",
                "required": True,
                "transform": {"op": "mul", "value": 0.90},
            },
            {
                "tile_id": "office_finish_plus_10",
                "label": "Office/Finish Scope +10%",
                "metric_ref": "trade_breakdown.finishes",
                "required": False,
                "transform": {"op": "mul", "value": 1.10},
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
                "plus_tiles": ["office_finish_plus_10"],
            },
        ],
        "provenance": {"notes": "Industrial flex space tile profile v1."},
    },
    "industrial_cold_storage_v1": {
        "version": "v1",
        "decision_table_columns": INDUSTRIAL_DECISION_TABLE_COLUMNS,
        "tiles": [
            {
                "tile_id": "cost_plus_10",
                "label": "Cost +10%",
                "metric_ref": "totals.total_project_cost",
                "required": True,
                "transform": {"op": "mul", "value": 1.10},
            },
            {
                "tile_id": "revenue_minus_10",
                "label": "Revenue -10%",
                "metric_ref": "revenue_analysis.annual_revenue",
                "required": True,
                "transform": {"op": "mul", "value": 0.90},
            },
            {
                "tile_id": "equipment_plus_10",
                "label": "Equipment +10%",
                "metric_ref": "construction_costs.equipment_total",
                "required": False,
                "transform": {"op": "mul", "value": 1.10},
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
                "plus_tiles": ["equipment_plus_10"],
            },
        ],
        "provenance": {"notes": "Industrial cold storage tile profile v1."},
    },
}
