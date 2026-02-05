SCOPE_ITEM_DEFAULTS = {}

SCOPE_ITEM_PROFILES = {
    "healthcare_urgent_care_structural_v1": {
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "foundations_slab_footings",
                        "label": "Foundations, slab, and footings",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.30},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "structural_frame",
                        "label": "Structural framing package",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.30},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "roof_structure_deck",
                        "label": "Roof structure and deck",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.20},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "misc_structural_supports",
                        "label": "Misc structural supports and allowances",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.20},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            }
        ],
    }
}
