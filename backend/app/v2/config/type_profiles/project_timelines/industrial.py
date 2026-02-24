from app.v2.config.master_config import BuildingType

CONFIG = (
    BuildingType.INDUSTRIAL,
    {
        "ground_up": {
            "total_months": 18,
            "milestones": [
                {
                    "id": "groundbreaking",
                    "label": "Groundbreaking",
                    "offset_months": 0,
                },
                {
                    "id": "structure_complete",
                    "label": "Structure Complete",
                    "offset_months": 8,
                },
                {
                    "id": "substantial_completion",
                    "label": "Substantial Completion",
                    "offset_months": 14,
                },
                {
                    "id": "grand_opening",
                    "label": "Grand Opening",
                    "offset_months": 18,
                },
            ],
        },
    },
)
