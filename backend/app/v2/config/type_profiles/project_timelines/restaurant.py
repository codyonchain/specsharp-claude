from app.v2.config.master_config import BuildingType

CONFIG = (
    BuildingType.RESTAURANT,
    {
        "ground_up": {
            "total_months": 14,
            "milestones": [
                {
                    "id": "groundbreaking",
                    "label": "Groundbreaking / Site & Shell Start",
                    "offset_months": 0,
                },
                {
                    "id": "structure_complete",
                    "label": "Structure & Shell Complete",
                    "offset_months": 6,
                },
                {
                    "id": "kitchen_mep_rough_in",
                    "label": "Kitchen & MEP Rough-In Complete",
                    "offset_months": 9,
                },
                {
                    "id": "substantial_completion",
                    "label": "Health & Code Inspections + Final Punch",
                    "offset_months": 11,
                },
                {
                    "id": "grand_opening",
                    "label": "Soft / Grand Opening",
                    "offset_months": 13,
                },
            ],
        },
    },
)
