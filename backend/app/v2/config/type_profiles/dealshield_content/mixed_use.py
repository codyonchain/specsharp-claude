"""DealShield content profiles for mixed_use subtypes."""


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
                    "label": "Reconfirm hard-cost basis +/-10%",
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
                "text": "Absorption cadence assumes blended demand without a staged backfill plan.",
                "why": "A modest demand delay materially shifts the conservative and ugly scenarios.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Allowance closeout timing is treated as fixed before late trade clarifications.",
                "why": "Late basis changes can compress contingency faster than modeled.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which mixed-use scopes are still allowance-backed instead of quoted?",
                    "What unresolved owner standards can still move hard costs before buyout?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What signed tenant or operator paper supports near-term revenue ramp assumptions?",
                    "What downside absorption bridge is approved if demand slips one cycle?",
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
                "flag": "Revenue case depends on narrative assumptions without signed milestone evidence.",
                "action": "Publish a subtype-specific lease-up and operator commitment bridge.",
            },
            {
                "id": "rf_3",
                "flag": "Cross-program scope boundaries are not closed in procurement logs.",
                "action": "Issue a scope-boundary matrix with owner and GC accountability by package.",
            },
        ],
    }


DEALSHIELD_CONTENT_PROFILES = {
    "mixed_use_office_residential_v1": _profile(
        profile_id="mixed_use_office_residential_v1",
        headline="What would move the office-residential decision fastest?",
        revenue_label="Stress office lease-up and residential absorption downside -10%",
        unique_driver={
            "id": "driver_trade",
            "label": "Pressure-test amenity and vertical-core fit-out carry",
            "tile_id": "amenity_and_core_fitout_plus_12",
        },
        unique_mlw={
            "text": "Amenity and vertical-core fit-out is modeled as settled before tenant standards are finalized.",
            "why": "Late fit-out revisions affect both cost pressure and lease-up timing in this program mix.",
        },
        unique_questions=[
            "Which amenity and core packages are fully designed versus provisional?",
            "Where can office and residential fit-out standards still diverge from the base budget?",
        ],
        unique_red_flag={
            "flag": "Amenity/core fit-out scope is still open while underwriting assumes fixed carry.",
            "action": "Lock an amenity/core scope register with dollarized optionality and decision dates.",
        },
    ),
    "mixed_use_retail_residential_v1": _profile(
        profile_id="mixed_use_retail_residential_v1",
        headline="What would move the retail-residential decision fastest?",
        revenue_label="Stress ground-floor retail and residential rent downside -10%",
        unique_driver={
            "id": "driver_trade",
            "label": "Pressure-test retail frontage and podium structure carry",
            "tile_id": "retail_frontage_and_podium_plus_11",
        },
        unique_mlw={
            "text": "Retail frontage and podium assumptions are treated as fixed before tenant frontage requirements settle.",
            "why": "Late frontage and podium changes create nonlinear rework risk in mixed ground-floor programs.",
        },
        unique_questions=[
            "Which storefront and podium scope assumptions are tenant-driven versus base-building obligations?",
            "How are turnover sequencing and residential access constraints reflected in the budget?",
        ],
        unique_red_flag={
            "flag": "Podium and frontage package lacks a closed turnover interface plan.",
            "action": "Require a turnover interface matrix covering podium, storefront, and residential circulation impacts.",
        },
    ),
    "mixed_use_hotel_retail_v1": _profile(
        profile_id="mixed_use_hotel_retail_v1",
        headline="What would move the hotel-retail decision fastest?",
        revenue_label="Stress ADR/occupancy and retail tenancy downside -10%",
        unique_driver={
            "id": "driver_trade",
            "label": "Pressure-test guestrooms and F&B fit-out carry",
            "tile_id": "guestrooms_and_fnb_fitout_plus_14",
        },
        unique_mlw={
            "text": "Guestroom and F&B fit-out assumptions are modeled as stable before concept and operator standards lock.",
            "why": "Hospitality fit-out drift can overwhelm baseline contingency in mixed-use podium conditions.",
        },
        unique_questions=[
            "What operator standard packages are signed versus still in concept design?",
            "How are guestroom and F&B finish options bounded in procurement assumptions?",
        ],
        unique_red_flag={
            "flag": "Operator standard packages remain unsettled while fit-out carry is treated as fixed.",
            "action": "Publish an operator-standard reconciliation with approved alternates and cost deltas.",
        },
    ),
    "mixed_use_transit_oriented_v1": _profile(
        profile_id="mixed_use_transit_oriented_v1",
        headline="What would move the transit-oriented decision fastest?",
        revenue_label="Stress ridership-linked demand and tenancy downside -10%",
        unique_driver={
            "id": "driver_trade",
            "label": "Pressure-test station interface and circulation scope carry",
            "tile_id": "station_interface_and_circulation_plus_13",
        },
        unique_mlw={
            "text": "Station interface and circulation packages are underwritten as fixed before agency coordination closes.",
            "why": "Unresolved agency interfaces can shift structural and access scope late in design.",
        },
        unique_questions=[
            "Which station interface packages are approved by transit agencies versus pending?",
            "Where can circulation and access code revisions still add structural scope?",
        ],
        unique_red_flag={
            "flag": "Agency coordination milestones are missing from scope lock assumptions.",
            "action": "Gate investment approval on agency signoff milestones tied to scope freeze dates.",
        },
    ),
    "mixed_use_urban_mixed_v1": _profile(
        profile_id="mixed_use_urban_mixed_v1",
        headline="What would move the urban mixed-use decision fastest?",
        revenue_label="Stress blended tenancy and activation demand downside -10%",
        unique_driver={
            "id": "driver_trade",
            "label": "Pressure-test vertical mobility and public-realm systems carry",
            "tile_id": "vertical_mobility_and_public_realm_plus_12",
        },
        unique_mlw={
            "text": "Vertical mobility and public-realm systems are treated as stable before activation programming is finalized.",
            "why": "Late activation and circulation changes can cascade through MEP coordination and turnover sequencing.",
        },
        unique_questions=[
            "What public-realm activation scope is committed versus still optional?",
            "How are elevator/escalator and circulation assumptions bounded against tenant mix changes?",
        ],
        unique_red_flag={
            "flag": "Public-realm activation plan is not reconciled to vertical mobility design assumptions.",
            "action": "Issue a coordinated activation and mobility basis package before GMP lock.",
        },
    ),
}
