"""DealShield content profiles for industrial types."""


def _industrial_standard_content_profile(profile_id: str, subtype_label: str) -> dict:
    return {
        "version": "v1",
        "profile_id": profile_id,
        "fastest_change": {
            "headline": "What would change this decision fastest?",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Confirm hard costs +/-10%",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_revenue",
                    "label": "Validate revenue +/-10%",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Verify structural and envelope risk",
                    "tile_id": "structural_plus_10",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": f"{subtype_label.title()} site and civil basis may still carry unresolved scope.",
                "why": "Cost sensitivity is first-order in this profile, so unresolved site scope distorts the decision.",
            },
            {
                "id": "mlw_2",
                "text": "Revenue assumptions may be too linear relative to lease-up and demand volatility.",
                "why": "Revenue downside is a direct decision lever and needs a contract-backed ramp assumption.",
            },
            {
                "id": "mlw_3",
                "text": "Structural package risk may be understated before geotech and lateral assumptions are locked.",
                "why": "The ugly case explicitly loads structural pressure; confirm if that pressure is already in base.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Show the hard-cost inclusions and exclusions list signed by precon and design.",
                    "What sitework and utility assumptions remain open, and who owns each close-out date?",
                    "Which allowances are still provisional versus quoted?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "Which lease-up assumptions are committed in LOIs versus modeled from market averages?",
                    "What demand comps support the stated revenue run-rate, and when were they last updated?",
                    "What is the downside plan if absorption slips one leasing cycle?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "structural_plus_10",
                "questions": [
                    "Any long-span framing, slab thickness, or lateral scope not fully priced yet?",
                    "What geotech findings can still force a foundation redesign?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Geotech and civil basis is not locked.",
                "action": "Request the geotech summary, civil set status, and a line-item sitework allowance breakout.",
            },
            {
                "id": "rf_2",
                "flag": "Revenue case is anchored to narrative, not executed tenant paper.",
                "action": "Ask for LOI status by suite and a lease-up bridge from underwritten assumptions to signed terms.",
            },
            {
                "id": "rf_3",
                "flag": "Structural package value-engineering list is not closed.",
                "action": "Confirm open VE items with dollar impact and decision owner before investment committee sign-off.",
            },
        ],
    }


DEALSHIELD_CONTENT_PROFILES = {
    "industrial_warehouse_v1": {
        "version": "v1",
        "profile_id": "industrial_warehouse_v1",
        "fastest_change": {
            "headline": "What would change this decision fastest?",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Confirm hard costs +/-10%",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_revenue",
                    "label": "Validate revenue +/-10%",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Verify structural and envelope risk",
                    "tile_id": "structural_plus_10",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Sitework basis is too thin; utility routing and off-site requirements can move total cost quickly.",
                "why": "Cost sensitivity is first-order in this profile, so unresolved site scope distorts the decision.",
            },
            {
                "id": "mlw_2",
                "text": "Lease-up timing is treated as linear when tenant decision cycles are not.",
                "why": "Revenue downside is a direct decision lever and needs a contract-backed ramp assumption.",
            },
            {
                "id": "mlw_3",
                "text": "Structural procurement risk is understated until geotech and lateral assumptions are frozen.",
                "why": "The ugly case explicitly loads structural pressure; confirm if that pressure is already in base.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Show the hard-cost inclusions and exclusions list signed by precon and design.",
                    "What sitework and utility assumptions remain open, and who owns each close-out date?",
                    "Which allowances are still provisional versus quoted?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "Which lease-up assumptions are committed in LOIs versus modeled from market averages?",
                    "What demand comps support the stated revenue run-rate, and when were they last updated?",
                    "What is the downside plan if absorption slips one leasing cycle?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "structural_plus_10",
                "questions": [
                    "Any long-span framing, slab thickness, or lateral scope not fully priced yet?",
                    "What geotech findings can still force a foundation redesign?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Geotech and civil basis is not locked.",
                "action": "Request the geotech summary, civil set status, and a line-item sitework allowance breakout.",
            },
            {
                "id": "rf_2",
                "flag": "Revenue case is anchored to broker narrative, not executed tenant paper.",
                "action": "Ask for LOI status by suite and a lease-up bridge from underwritten assumptions to signed terms.",
            },
            {
                "id": "rf_3",
                "flag": "Structural package value-engineering list is not closed.",
                "action": "Confirm open VE items with dollar impact and decision owner before investment committee sign-off.",
            },
        ],
    },
    "industrial_distribution_center_v1": _industrial_standard_content_profile(
        "industrial_distribution_center_v1",
        "distribution center",
    ),
    "industrial_manufacturing_v1": _industrial_standard_content_profile(
        "industrial_manufacturing_v1",
        "manufacturing",
    ),
    "industrial_flex_space_v1": _industrial_standard_content_profile(
        "industrial_flex_space_v1",
        "flex space",
    ),
    "industrial_cold_storage_v1": {
        "version": "v1",
        "profile_id": "industrial_cold_storage_v1",
        "fastest_change": {
            "headline": "What would change this decision fastest?",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Confirm hard costs +/-10%",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_revenue",
                    "label": "Validate revenue +/-10%",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Verify refrigeration and equipment risk",
                    "tile_id": "equipment_plus_10",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Refrigeration and rack scope is not fully aligned between vendor proposals and GC carry.",
                "why": "Equipment sensitivity is explicit here; scope drift can reset both cost and schedule.",
            },
            {
                "id": "mlw_2",
                "text": "Electrical service and backup assumptions are treated as fixed before utility commitment.",
                "why": "Power upgrades are often late-breaking and can invalidate the current base case.",
            },
            {
                "id": "mlw_3",
                "text": "Revenue ramp assumes immediate throughput without a commissioning curve.",
                "why": "Revenue downside is already a core lever; commissioning lag must be reflected in operating assumptions.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "What is in or out of hard costs, and where are allowances still carrying unknown scope?",
                    "Any contingency reserved for utility interconnection, paving, and drainage surprises?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "Which contract terms and throughput assumptions support the revenue line?",
                    "What commissioning delay risk is not currently reflected in baseline operations?",
                    "What volume downside triggers a covenant discussion?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "equipment_plus_10",
                "questions": [
                    "Which refrigeration items are vendor-quoted versus allowance-based?",
                    "Any electrical service upgrade assumptions still unresolved with the utility?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Equipment package basis is not contract-backed.",
                "action": "Request vendor quotes with clear inclusions, exclusions, lead times, and utility loads.",
            },
            {
                "id": "rf_2",
                "flag": "Utility commitment timeline is not synchronized to construction sequencing.",
                "action": "Confirm utility milestones and attach schedule float impact to each unresolved milestone.",
            },
            {
                "id": "rf_3",
                "flag": "Operating model assumes full throughput too early.",
                "action": "Require a commissioning-to-stabilization ramp and test debt coverage under that ramp.",
            },
        ],
    },
}
