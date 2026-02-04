from app.v2.config.master_config import BuildingType

CONFIG = (
    BuildingType.HOSPITALITY,
    {
        "ground_up": {
            "total_months": 30,
            "milestones": [
                {
                    "id": "groundbreaking",
                    "label": "Groundbreaking",
                    "offset_months": 0,
                },
                {
                    "id": "structure_complete",
                    "label": "Structure Complete",
                    "offset_months": 14,
                },
                {
                    "id": "substantial_completion",
                    "label": "Substantial Completion",
                    "offset_months": 24,
                },
                {
                    "id": "grand_opening",
                    "label": "Grand Opening",
                    "offset_months": 30,
                },
            ],
        },
    },
)
