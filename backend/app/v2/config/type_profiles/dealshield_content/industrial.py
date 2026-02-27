"""DealShield content profiles for industrial types."""


DEALSHIELD_CONTENT_PROFILES = {
    "industrial_warehouse_v1": {
        "version": "v1",
        "profile_id": "industrial_warehouse_v1",
        "fastest_change": {
            "headline": "What would change this decision fastest?",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Confirm sitework/civil allowances + utility routing",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_revenue",
                    "label": "Validate rent/SF and absorption (broker comps + active tenants)",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Confirm dock count/clear height as it affects rent",
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
                "text": "Lease-up is modeled smoothly; real absorption is lumpy (LOIs, TI decisions, broker cycles).",
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
                    "What share of NOI is backed by executed lease term and tenant credit, and what exit cap assumption is tied to that rent roll?",
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
    "industrial_distribution_center_v1": {
        "version": "v1",
        "profile_id": "industrial_distribution_center_v1",
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
                    "label": "Validate tenant revenue +/-10%",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Verify electrical/sortation infrastructure +10%",
                    "tile_id": "electrical_plus_10",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Sortation controls and tenant electrical loads are only partially carried in current pricing.",
                "why": "Distribution centers fail fast when power and controls scope is underwritten as a generic allowance.",
            },
            {
                "id": "mlw_2",
                "text": "Yard and dock sequencing assumptions understate civil and turnover friction.",
                "why": "Even moderate site inefficiency can degrade both lease-up schedule and stabilized economics.",
            },
            {
                "id": "mlw_3",
                "text": "Revenue ramp depends on concentrated tenant demand without fallback assumptions.",
                "why": "Revenue concentration can produce an abrupt downside when one tenant slips or reprices.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which civil, paving, and utility scopes are quoted vs allowance-based?",
                    "What off-site improvements are still pending jurisdictional review?",
                    "Where does contingency explicitly carry site and yard risk?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What share of projected income is backed by executed leases or binding LOIs?",
                    "Which assumptions rely on speculative absorption for remaining bays?",
                    "What downside leasing cadence has been tested in IC materials?",
                    "What weighted-average lease term and tenant-credit mix support base rent, and how does that map to the cap-rate assumption used for value?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "electrical_plus_10",
                "questions": [
                    "What tenant electrical density was assumed by bay and by use case?",
                    "Are switchgear lead times and temporary power costs reflected in baseline schedule?",
                    "What controls/sortation scope is owner furnished vs contractor furnished?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Electrical and controls basis is modeled as a placeholder, not a quoted package.",
                "action": "Require one-line electrical narrative with demand assumptions, gear list, and allowance ownership.",
            },
            {
                "id": "rf_2",
                "flag": "Dock and yard sequencing risk is not tied to tenant turnover milestones.",
                "action": "Add a dock/yard critical-path checkpoint list tied to lease commencement dates.",
            },
            {
                "id": "rf_3",
                "flag": "Revenue case has tenant concentration without tested fallback leasing plan.",
                "action": "Model concentration downside with one major tenant delay and validate DSCR resilience.",
            },
        ],
    },
    "industrial_manufacturing_v1": {
        "version": "v1",
        "profile_id": "industrial_manufacturing_v1",
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
                    "label": "Validate production revenue +/-10%",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Verify process MEP/utilities +10%",
                    "tile_id": "process_mep_plus_10",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Process ventilation, exhaust, and compressed-air assumptions are not fully locked to equipment schedule.",
                "why": "Manufacturing downside is often driven by utility and process-system scope drift, not shell cost alone.",
            },
            {
                "id": "mlw_2",
                "text": "Commissioning and qualification duration is shorter than historical startup cycles.",
                "why": "An optimistic ramp can overstate early NOI and understate covenant pressure.",
            },
            {
                "id": "mlw_3",
                "text": "Revenue plan assumes target throughput before staffing and process yield are proven.",
                "why": "Manufacturing cash flow sensitivity increases materially when throughput lags stabilization assumptions.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which line items are still carried as design allowance instead of vendor-backed pricing?",
                    "What utility interconnect scope is owner risk vs contractor risk?",
                    "What contingency is dedicated specifically to process-system integration?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What throughput assumptions are contract-backed vs modeled?",
                    "Which customer commitments support first-year production volumes?",
                    "What downside case was run for delayed line qualification?",
                    "Which offtake terms and customer credit actually back year-one revenue, and what cap-rate or exit-multiple assumption is IC using for valuation?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "process_mep_plus_10",
                "questions": [
                    "Are process HVAC, exhaust, and compressed-air loads validated by final equipment schedule?",
                    "What redundancy and controls assumptions are still unresolved?",
                    "How are long-lead MEP components protected in schedule float?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Process utilities are under-specified relative to production program.",
                "action": "Issue a process utility matrix linking each line/equipment package to design and pricing basis.",
            },
            {
                "id": "rf_2",
                "flag": "Commissioning curve is compressed and not reflected in underwriting downside.",
                "action": "Add staged commissioning assumptions to revenue ramp and retest debt coverage.",
            },
            {
                "id": "rf_3",
                "flag": "MEP lead-time and integration risk is not explicitly owned.",
                "action": "Assign owner/GC/vendor accountability per long-lead component with milestone dates.",
            },
        ],
    },
    "industrial_flex_space_v1": {
        "version": "v1",
        "profile_id": "industrial_flex_space_v1",
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
                    "label": "Validate blended rent revenue +/-10%",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Verify office/showroom finish scope +10%",
                    "tile_id": "office_finish_plus_10",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Office-to-warehouse mix is treated as static while tenant-fit requirements are still moving.",
                "why": "Flex deals reprice quickly when office/showroom percentage expands late in design.",
            },
            {
                "id": "mlw_2",
                "text": "Tenant improvement intensity is benchmarked to light industrial instead of true flex comps.",
                "why": "Misstated finish intensity can hide a large cost and schedule delta.",
            },
            {
                "id": "mlw_3",
                "text": "Blended rent assumptions overstate achievable premium on office-heavy bays.",
                "why": "Revenue downside is nonlinear when premium office bays lease slower than modeled.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "What portions of interior buildout remain allowance-based versus fully designed?",
                    "Which tenant-improvement obligations are pushed into landlord scope?",
                    "What contingency is reserved for office/showroom finishes and rework?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What comp-set evidence supports the blended rent assumption by bay type?",
                    "How much of projected income depends on office-heavy suites leasing on schedule?",
                    "What scenario was tested for slower lease-up of higher-finish bays?",
                    "What executed lease term and tenant-credit support exists for office-heavy bays, and what cap-rate assumption was applied to that blended mix?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "office_finish_plus_10",
                "questions": [
                    "What percent office/showroom was carried in pricing and in leasing assumptions?",
                    "Which finish packages can still shift due to tenant customization?",
                    "Are mezzanine and premium finish options isolated as explicit adders?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Office/showroom scope is drifting without synchronized lease assumptions.",
                "action": "Lock an office ratio basis and align both cost model and rent model to that same basis.",
            },
            {
                "id": "rf_2",
                "flag": "Finish-level contingency is not explicitly ring-fenced.",
                "action": "Create a TI/finish contingency bucket with owner sign-off triggers for release.",
            },
            {
                "id": "rf_3",
                "flag": "Blended rent case is unsupported by current flex leasing comps.",
                "action": "Refresh comps by bay mix and rerun downside with slower premium-bay absorption.",
            },
        ],
    },
    "industrial_cold_storage_v1": {
        "version": "v1",
        "profile_id": "industrial_cold_storage_v1",
        "fastest_change": {
            "headline": "What would change this decision fastest?",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Confirm refrigeration package scope + inclusions (vendor vs GC carry)",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_revenue",
                    "label": "Confirm utility commitment + backup power assumptions",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Validate ramp-to-stabilization assumptions (commissioning curve)",
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
                    "Which executed storage/service contract terms and counterparty credit support the ramp, and what cap-rate assumption is IC using on stabilized cash flow?",
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
