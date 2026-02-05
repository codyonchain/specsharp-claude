SCOPE_ITEM_DEFAULTS = {}

SCOPE_ITEM_PROFILES = {
    "healthcare_medical_office_building_structural_v1": {
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "foundations_slab_footings",
                        "label": "Foundations, slab, and footings",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.30,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "structural_frame",
                        "label": "Structural frame (steel/wood)",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.30,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "roof_structure_deck",
                        "label": "Roof structure and deck",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.18,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "exterior_envelope_structural_allowance",
                        "label": "Exterior envelope structural allowances",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.12,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "misc_stairs_supports",
                        "label": "Misc. structural, stairs, and supports",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                ],
            },
        ],
    },
    "healthcare_urgent_care_structural_v1": {
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "concrete_slab_on_grade",
                        "label": "Concrete slab on grade (clinic baseline)",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.25,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "foundations_footings",
                        "label": "Foundations, footings, and thickened slabs",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "structural_framing",
                        "label": "Structural framing (steel or CMU bearing)",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.25,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "exterior_wall_envelope",
                        "label": "Exterior wall envelope and sheathing",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "roof_structure_system",
                        "label": "Roof structure and decking",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                ],
            },
        ],
    },
}
