"""DealShield content profiles for civic types."""


def _civic_content_profile(profile_id: str, subtype_label: str) -> dict:
    return {
        "version": "v1",
        "profile_id": profile_id,
        "fastest_change": {
            "headline": "What would change this feasibility decision fastest?",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Confirm hard-cost drivers +/-10%",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_mep",
                    "label": "Validate permitting and MEP complexity risk",
                    "tile_id": "mechanical_plus_10",
                },
                {
                    "id": "driver_procurement",
                    "label": "Validate procurement and power infrastructure risk",
                    "tile_id": "electrical_plus_10",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_site_conditions",
                "text": "Site conditions are assumed from early desktop inputs and may miss utility conflicts or geotechnical constraints.",
                "why": "If site unknowns are unresolved, total project cost can shift materially before GMP.",
            },
            {
                "id": "mlw_permitting",
                "text": "Permitting path and agency review depth are treated as stable while authority comments are still pending.",
                "why": "Schedule duration and permit-cycle variability are not modeled directly in this profile.",
            },
            {
                "id": "mlw_procurement",
                "text": "Long-lead procurement assumptions presume standard lead times for switchgear, controls, and life-safety devices.",
                "why": "Lead-time slippage is not modeled directly; it appears indirectly through cost pressure and resequencing.",
            },
            {
                "id": "mlw_mep_complexity",
                "text": "MEP complexity is treated as normal density even when renovation interfaces and compliance upgrades can stack.",
                "why": "Mechanical and electrical pressure are modeled; interface risk still requires explicit basis checks.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_program_confirmation",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    f"What program elements for {subtype_label} are fully confirmed versus still subject to stakeholder revision?",
                    "Which scope line items are allowance-based and what evidence supports each allowance?",
                    "Where are owner scope boundaries likely to migrate into contractor scope?",
                ],
            },
            {
                "id": "qb_security_compliance",
                "driver_tile_id": "mechanical_plus_10",
                "questions": [
                    "Which security and compliance requirements are pending final authority interpretation?",
                    "Any life-safety, ventilation, or envelope requirements still unresolved across design disciplines?",
                    "What agency comments are expected to alter the mechanical basis of design?",
                ],
            },
            {
                "id": "qb_stakeholder_constraints",
                "driver_tile_id": "electrical_plus_10",
                "questions": [
                    "Which stakeholder constraints (operations, community access, after-hours use) could force procurement or phasing changes?",
                    "What long-lead equipment is still missing approved alternates?",
                    "What power and controls assumptions are not yet confirmed with utilities or owner IT/security teams?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_scope_basis",
                "flag": "Program basis and stakeholder constraints are still moving.",
                "action": "Issue a single responsibility matrix with dated owner approvals on open program decisions.",
            },
            {
                "id": "rf_permit_path",
                "flag": "Permitting/compliance pathway has unresolved review risk.",
                "action": "Track unresolved authority comments weekly with cost and schedule owner for each item.",
            },
            {
                "id": "rf_procurement_mep",
                "flag": "MEP and electrical procurement assumptions are not quote-backed.",
                "action": "Request long-lead buyout status with alternates and associated cost deltas before approval.",
            },
        ],
    }


DEALSHIELD_CONTENT_PROFILES = {
    "civic_community_center_v1": _civic_content_profile(
        "civic_community_center_v1",
        "community center",
    ),
    "civic_courthouse_v1": _civic_content_profile(
        "civic_courthouse_v1",
        "courthouse",
    ),
    "civic_government_building_v1": _civic_content_profile(
        "civic_government_building_v1",
        "government building",
    ),
    "civic_library_v1": _civic_content_profile(
        "civic_library_v1",
        "library",
    ),
    "civic_public_safety_v1": _civic_content_profile(
        "civic_public_safety_v1",
        "public safety facility",
    ),
}
