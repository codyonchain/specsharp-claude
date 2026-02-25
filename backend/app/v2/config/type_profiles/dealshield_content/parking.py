"""DealShield content profiles for parking subtypes."""


def _profile(
    *,
    profile_id: str,
    headline: str,
    revenue_label: str,
    unique_driver: dict,
    unique_mlw: dict,
    unique_questions: list[str],
    unique_red_flag: dict,
) -> dict:
    return {
        "version": "v1",
        "profile_id": profile_id,
        "fastest_change": {
            "headline": headline,
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Re-price hard-cost basis at +/-10%",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_revenue",
                    "label": revenue_label,
                    "tile_id": "revenue_minus_10",
                },
                unique_driver,
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": unique_driver["tile_id"],
                "text": unique_mlw["text"],
                "why": unique_mlw["why"],
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Utilization ramp is modeled as stable despite event, seasonality, and policy-driven demand swings.",
                "why": "Demand softening can delay stabilization and widen downside in conservative and ugly scenarios.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Allowance closeout assumes field conditions stay inside baseline with no late corrective scope.",
                "why": "Late discoveries on site systems can consume contingency faster than modeled.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which site and utility scopes are still allowance-based versus fully priced?",
                    "What unresolved owner standards can still increase hard costs before buyout?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What committed demand evidence supports current utilization assumptions?",
                    "How does NOI move if occupancy stabilizes one demand cycle later?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": unique_driver["tile_id"],
                "questions": unique_questions,
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": unique_red_flag["flag"],
                "action": unique_red_flag["action"],
            },
            {
                "id": "rf_2",
                "flag": "Scenario narrative does not tie utilization downside to explicit operating responses.",
                "action": "Publish a demand-response playbook with trigger points tied to occupancy thresholds.",
            },
            {
                "id": "rf_3",
                "flag": "Trade-risk assumptions are not linked to inspection and verification milestones.",
                "action": "Add milestone-owned validation checkpoints before procurement lock.",
            },
        ],
    }


DEALSHIELD_CONTENT_PROFILES = {
    "parking_surface_parking_v1": _profile(
        profile_id="parking_surface_parking_v1",
        headline="What changes this surface-parking decision fastest?",
        revenue_label="Re-cut utilization and turnover downside -10%",
        unique_driver={
            "id": "driver_surface_rework",
            "label": "Pressure-test drainage corrections and restriping turnover carry",
            "tile_id": "surface_lighting_and_drainage_rework_plus_8",
        },
        unique_mlw={
            "text": "Drainage and restriping scope assumes field conditions stay stable through turnover windows.",
            "why": "Localized ponding and striping rework can force phased closures and unplanned carry.",
        },
        unique_questions=[
            "Which drainage basins still rely on conceptual grading rather than field-verified slopes?",
            "What closure phasing assumptions support restriping and lighting rework productivity?",
        ],
        unique_red_flag={
            "flag": "Drainage and restriping scopes are grouped into contingency without phased closure plan.",
            "action": "Issue a lot-by-lot sequencing plan with corrective-scope triggers and revenue impacts.",
        },
    ),
    "parking_parking_garage_v1": _profile(
        profile_id="parking_parking_garage_v1",
        headline="What changes this parking-garage decision fastest?",
        revenue_label="Re-cut stall demand and collection downside -10%",
        unique_driver={
            "id": "driver_garage_rehab",
            "label": "Pressure-test post-tension remediation and deck coating scope",
            "tile_id": "garage_post_tension_and_coating_plus_11",
        },
        unique_mlw={
            "text": "Deck rehabilitation assumes limited tendon and coating repair without escalation from testing.",
            "why": "Higher-than-expected deterioration quickly expands structural repair windows and cost exposure.",
        },
        unique_questions=[
            "Which deck zones have completed intrusive testing and which remain assumption-based?",
            "How are closure windows sequenced if rehabilitation depth exceeds baseline carry?",
        ],
        unique_red_flag={
            "flag": "Rehabilitation basis does not separate verified repair zones from allowance zones.",
            "action": "Publish a deck-by-deck verification matrix linked to contingency release gates.",
        },
    ),
    "parking_underground_parking_v1": _profile(
        profile_id="parking_underground_parking_v1",
        headline="What changes this underground-parking decision fastest?",
        revenue_label="Re-cut utilization and downtime downside -10%",
        unique_driver={
            "id": "driver_underground_water",
            "label": "Pressure-test dewatering duty and ventilation hardening scope",
            "tile_id": "underground_dewatering_and_ventilation_plus_14",
        },
        unique_mlw={
            "text": "Water-table and ventilation assumptions are modeled as steady despite seasonal and site variability.",
            "why": "Unexpected inflow and ventilation load shifts can trigger resequencing and expensive system upgrades.",
        },
        unique_questions=[
            "What site monitoring confirms inflow and pump runtime assumptions in peak conditions?",
            "Which ventilation control sequences have been validated for contingency operating modes?",
        ],
        unique_red_flag={
            "flag": "Dewatering and ventilation basis is not tied to signed seasonal risk assumptions.",
            "action": "Issue a water and ventilation risk register with escalation actions by threshold breach.",
        },
    ),
    "parking_automated_parking_v1": _profile(
        profile_id="parking_automated_parking_v1",
        headline="What changes this automated-parking decision fastest?",
        revenue_label="Re-cut throughput and uptime downside -10%",
        unique_driver={
            "id": "driver_automation_controls",
            "label": "Pressure-test controls integration and redundancy commissioning scope",
            "tile_id": "automated_controls_and_redundancy_plus_16",
        },
        unique_mlw={
            "text": "Commissioning assumptions understate controls integration and redundancy test complexity.",
            "why": "Late software and controls defects can delay turnover and compress early operating uptime.",
        },
        unique_questions=[
            "Which retrieval and controls interfaces are still pending vendor integration verification?",
            "What recovery-mode tests are required to prove redundancy before turnover?",
        ],
        unique_red_flag={
            "flag": "Commissioning plan does not include explicit pass/fail criteria for retrieval uptime.",
            "action": "Approve a stage-gated FAT/SAT checklist tied to turnover readiness decisions.",
        },
    ),
}
