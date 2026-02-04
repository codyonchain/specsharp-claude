from app.v2.config.master_config import BuildingType

CONFIG = (
    BuildingType.HEALTHCARE,
    {
        "ground_up": {
            "total_months": 18,
            "milestones": [
                {
                    "id": "design_licensing",
                    "label": "Design & Licensing",
                    "offset_months": 0,
                },
                {
                    "id": "shell_mep_rough_in",
                    "label": "Shell & MEP Rough-In",
                    "offset_months": 4,
                },
                {
                    "id": "interior_buildout",
                    "label": "Interior Buildout & Finishes",
                    "offset_months": 8,
                },
                {
                    "id": "equipment_low_voltage",
                    "label": "Equipment & Low Voltage",
                    "offset_months": 12,
                },
                {
                    "id": "soft_opening",
                    "label": "Soft Opening & Ramp-Up",
                    "offset_months": 16,
                },
            ],
        },
    },
)
