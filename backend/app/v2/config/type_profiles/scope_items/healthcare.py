SCOPE_ITEM_DEFAULTS = {
    "surgical_center": "healthcare_surgical_center_structural_v1",
    "imaging_center": "healthcare_imaging_center_structural_v1",
    "urgent_care": "healthcare_urgent_care_structural_v1",
    "outpatient_clinic": "healthcare_outpatient_clinic_structural_v1",
    "medical_office_building": "healthcare_medical_office_building_structural_v1",
    "dental_office": "healthcare_dental_office_structural_v1",
    "hospital": "healthcare_hospital_structural_v1",
    "medical_center": "healthcare_medical_center_structural_v1",
    "nursing_home": "healthcare_nursing_home_structural_v1",
    "rehabilitation": "healthcare_rehabilitation_structural_v1",
}


def _item(
    *,
    key: str,
    label: str,
    unit: str,
    share: float,
    quantity_type: str = "sf",
    quantity_params: dict = None,
) -> dict:
    return {
        "key": key,
        "label": label,
        "unit": unit,
        "allocation": {"type": "share_of_trade", "share": share},
        "quantity_rule": {"type": quantity_type, "params": quantity_params or {}},
    }


def _trade(trade_key: str, trade_label: str, items: list[dict]) -> dict:
    return {"trade_key": trade_key, "trade_label": trade_label, "items": items}


SCOPE_ITEM_PROFILES = {
    "healthcare_surgical_center_structural_v1": {
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(key="asc_foundation_and_slab", label="Surgical slab and reinforced foundations", unit="SF", share=0.40),
                    _item(key="asc_or_shell_framing", label="OR shell framing and roof steel", unit="SF", share=0.35),
                    _item(key="asc_mech_penthouse_support", label="Mechanical penthouse and equipment support", unit="SF", share=0.25),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(key="asc_or_ahus_and_pressurization", label="OR AHUs and pressure cascade controls", unit="LS", share=0.30, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="asc_sterile_core_hvac_distribution", label="Sterile-core HVAC distribution", unit="SF", share=0.25),
                    _item(key="asc_exhaust_and_heat_recovery", label="Procedure exhaust and heat recovery package", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="asc_post_op_humidity_and_reheat", label="Post-op humidity control and reheat loops", unit="LS", share=0.20, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(key="asc_isolated_power_and_panels", label="Isolated power and critical panels", unit="LS", share=0.30, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="asc_lighting_and_room_controls", label="Clinical lighting and room controls", unit="SF", share=0.25),
                    _item(key="asc_backup_transfer_and_ups", label="Transfer switching and UPS interfaces", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="asc_or_boom_and_equipment_power", label="OR boom/equipment whip power and grounding", unit="LS", share=0.20, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(key="asc_med_gas_backbone", label="Medical gas backbone and zone valves", unit="LS", share=0.30, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="asc_scrub_and_sterile_plumbing", label="Scrub sink and sterile-room plumbing", unit="SF", share=0.25),
                    _item(key="asc_domestic_sanitary_and_vacuum", label="Domestic sanitary and suction/vacuum rough-in", unit="SF", share=0.25),
                    _item(key="asc_ro_water_and_condensate_reclaim", label="RO water and condensate reclaim allowances", unit="LS", share=0.20, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(key="asc_or_wall_ceiling_systems", label="OR wall/ceiling cleanable systems", unit="SF", share=0.40),
                    _item(key="asc_clinical_flooring_and_transitions", label="Clinical flooring and sterile transitions", unit="SF", share=0.35),
                    _item(key="asc_casework_and_core_millwork", label="Sterile-core casework and specialty millwork", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
        ],
    },
    "healthcare_imaging_center_structural_v1": {
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(key="img_vibration_controlled_slab", label="Vibration-controlled modality slabs", unit="SF", share=0.34),
                    _item(key="img_rf_room_framing", label="RF room framing and envelope reinforcement", unit="SF", share=0.27),
                    _item(key="img_roof_and_screenwall_support", label="Roof support and equipment screenwalls", unit="SF", share=0.21),
                    _item(key="img_magnet_anchorage_and_penetration_frames", label="Magnet anchorage and shield-penetration support frames", unit="LS", share=0.18, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(key="img_modality_cooling_loops", label="Modality cooling and dedicated loops", unit="LS", share=0.24, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="img_exam_suite_air_distribution", label="Exam-suite air distribution", unit="SF", share=0.21),
                    _item(key="img_temperature_humidity_controls", label="Tight temperature/humidity controls", unit="LS", share=0.20, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="img_mri_quench_and_relief_air_path", label="MRI quench and relief air-path allowances", unit="LS", share=0.18, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="img_control_room_pressurization_backup", label="Control-room pressurization backup and failover dampers", unit="LS", share=0.17, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(key="img_power_quality_mitigation", label="Power quality mitigation and filtering", unit="LS", share=0.24, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="img_modality_distribution_panels", label="Modality distribution and dedicated panels", unit="LS", share=0.21, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="img_control_room_low_voltage", label="Control-room low voltage and data", unit="SF", share=0.19),
                    _item(key="img_equipment_grounding_and_shield_bonding", label="Equipment grounding and RF shield bonding", unit="LS", share=0.19, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="img_remote_shutdown_and_interlocks", label="Remote equipment shutdown interlocks and life-safety relay paths", unit="LS", share=0.17, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(key="img_procedure_sink_groups", label="Procedure and prep sink groups", unit="EA", share=0.24, quantity_type="restroom_groups", quantity_params={"sf_per_group": 5000.0, "minimum": 1}),
                    _item(key="img_domestic_and_sanitary_distribution", label="Domestic and sanitary distribution", unit="SF", share=0.21),
                    _item(key="img_shielded_room_drainage", label="Shielded-room drainage tie-ins", unit="LS", share=0.20, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="img_process_cooling_water_isolation", label="Process cooling-water isolation and bypass", unit="LS", share=0.19, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="img_hot_water_recirculation_and_tempering", label="Hot-water recirculation and tempering loops for prep/recovery", unit="LS", share=0.16, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(key="img_shielded_room_finishes", label="Shielded-room wall and door finish package", unit="SF", share=0.33),
                    _item(key="img_patient_corridor_finishes", label="Patient corridor and waiting finishes", unit="SF", share=0.27),
                    _item(key="img_control_room_casework", label="Control-room casework and consoles", unit="LS", share=0.22, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="img_privacy_glazing_and_acoustic_panels", label="Patient-privacy glazing and acoustic treatment package", unit="SF", share=0.18),
                ],
            ),
        ],
    },
    "healthcare_urgent_care_structural_v1": {
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(key="uc_foundations_and_thickened_slab", label="Foundations and thickened slab zones", unit="SF", share=0.32),
                    _item(key="uc_clinic_shell_and_roof_frame", label="Clinic shell framing and roof deck", unit="SF", share=0.27),
                    _item(key="uc_canopy_and_entry_reinforcement", label="Ambulance/drop-off canopy reinforcement", unit="SF", share=0.23),
                    _item(key="uc_afterhours_screenwall_support", label="After-hours generator/screenwall support framing", unit="LS", share=0.18, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(key="uc_exam_suite_hvac", label="Exam-suite HVAC and outside-air package", unit="SF", share=0.31),
                    _item(key="uc_isolation_exhaust_allowance", label="Isolation and treatment exhaust allowance", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="uc_controls_and_afterhours_modes", label="After-hours controls and setback modes", unit="LS", share=0.22, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="uc_pharmacy_med_room_temp_control", label="Pharmacy/med-room temperature control and alarm integration", unit="LS", share=0.22, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(key="uc_service_and_branch_distribution", label="Main service and branch distribution", unit="LS", share=0.31, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="uc_treatment_and_triage_lighting", label="Triage/treatment lighting and controls", unit="SF", share=0.26),
                    _item(key="uc_imaging_and_lab_power_allowance", label="Imaging and in-house lab power allowance", unit="LS", share=0.22, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="uc_critical_receptacle_and_generator_stub", label="Critical receptacle circuits and generator-ready backfeed stub", unit="LS", share=0.21, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(key="uc_domestic_and_sanitary", label="Domestic and sanitary plumbing distribution", unit="SF", share=0.31),
                    _item(key="uc_exam_sink_and_flush_groups", label="Exam-room sink and fixture groups", unit="EA", share=0.25, quantity_type="restroom_groups", quantity_params={"sf_per_group": 7000.0, "minimum": 1}),
                    _item(key="uc_lab_and_specimen_waste", label="Lab/specimen waste and cleanout allowances", unit="LS", share=0.23, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="uc_staff_support_clean_utility_plumbing", label="Staff support, clean utility, and decon sink rough-ins", unit="LS", share=0.21, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(key="uc_clinical_wall_and_ceiling_systems", label="Clinical wall and ceiling systems", unit="SF", share=0.31),
                    _item(key="uc_high_turnover_flooring", label="High-turnover flooring and wall protection", unit="SF", share=0.27),
                    _item(key="uc_reception_casework_and_triage", label="Reception, triage, and charting casework", unit="LS", share=0.23, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="uc_patient_privacy_and_wayfinding_package", label="Patient privacy film, sliding hardware, and wayfinding package", unit="LS", share=0.19, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
        ],
    },
    "healthcare_outpatient_clinic_structural_v1": {
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(key="opc_slab_and_foundation_work", label="Clinic slab and shallow foundation work", unit="SF", share=0.40),
                    _item(key="opc_shell_framing", label="Clinic shell framing package", unit="SF", share=0.35),
                    _item(key="opc_entry_and_corridor_structure", label="Entry canopy and corridor structural allowances", unit="SF", share=0.25),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(key="opc_exam_room_hvac", label="Exam-room HVAC and ventilation", unit="SF", share=0.40),
                    _item(key="opc_waiting_area_comfort_controls", label="Waiting-area comfort controls", unit="SF", share=0.35),
                    _item(key="opc_small_lab_exhaust", label="Small lab and medication-room exhaust", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(key="opc_service_and_distribution", label="Electrical service and distribution", unit="LS", share=0.40, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="opc_exam_and_admin_lighting", label="Exam/admin lighting and controls", unit="SF", share=0.35),
                    _item(key="opc_data_nurse_call_low_voltage", label="Data and nurse-call low-voltage package", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(key="opc_domestic_sanitary", label="Domestic and sanitary branch piping", unit="SF", share=0.40),
                    _item(key="opc_exam_room_fixture_groups", label="Exam-room and restroom fixture groups", unit="EA", share=0.35, quantity_type="restroom_groups", quantity_params={"sf_per_group": 9000.0, "minimum": 1}),
                    _item(key="opc_hot_water_and_mixing", label="Hot-water generation and mixing valves", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(key="opc_exam_room_partition_package", label="Exam-room partitions and doors", unit="SF", share=0.40),
                    _item(key="opc_resilient_clinical_flooring", label="Resilient clinical flooring package", unit="SF", share=0.35),
                    _item(key="opc_reception_and_charting_casework", label="Reception and charting casework", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
        ],
    },
    "healthcare_medical_office_building_structural_v1": {
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(key="mob_foundations_and_core", label="MOB foundations and core structure", unit="SF", share=0.32),
                    _item(key="mob_floor_framing_and_decks", label="Multi-floor framing and deck package", unit="SF", share=0.27),
                    _item(key="mob_shell_enclosure_support", label="Shell enclosure and canopy supports", unit="SF", share=0.23),
                    _item(key="mob_high_load_tenant_bay_reinforcement", label="High-load tenant bay reinforcement and slab depressions", unit="LS", share=0.18, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(key="mob_base_building_hvac", label="Base-building HVAC backbone", unit="SF", share=0.32),
                    _item(key="mob_tenant_ready_air_distribution", label="Tenant-ready air-distribution stubs", unit="SF", share=0.26),
                    _item(key="mob_future_specialty_capacity_allowance", label="Future specialty suite capacity allowance", unit="LS", share=0.22, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="mob_afterhours_tenant_controls_and_metering", label="After-hours tenant controls, VAV tracking, and metering package", unit="LS", share=0.20, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(key="mob_service_switchgear_and_risers", label="Service switchgear and vertical risers", unit="LS", share=0.31, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="mob_common_area_lighting", label="Common-area and shell lighting", unit="SF", share=0.25),
                    _item(key="mob_tenant_metering_and_data", label="Tenant metering and data rough-in", unit="LS", share=0.23, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="mob_critical_tenant_backfeed_paths", label="Critical tenant backfeed paths and emergency transfer sleeves", unit="LS", share=0.21, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(key="mob_domestic_and_sanitary_mains", label="Domestic/sanitary mains and branch tie-ins", unit="SF", share=0.30),
                    _item(key="mob_restroom_core_groups", label="Core restroom groups by floor", unit="EA", share=0.26, quantity_type="restroom_groups", quantity_params={"sf_per_group": 14000.0, "minimum": 1}),
                    _item(key="mob_future_wet_stack_allowance", label="Future wet-stack allowance for tenant suites", unit="LS", share=0.23, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="mob_medical_tenant_hot_water_recirculation", label="Medical tenant hot-water recirculation and balancing valves", unit="LS", share=0.21, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(key="mob_lobby_and_core_finishes", label="Lobby and core corridor finishes", unit="SF", share=0.31),
                    _item(key="mob_shell_corridor_protection", label="Shell corridor wall protection and paint", unit="SF", share=0.25),
                    _item(key="mob_public_toilet_casework", label="Public toilet and common-casework allowance", unit="LS", share=0.23, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="mob_tenant_ready_demising_and_acoustic_package", label="Tenant-ready demising, acoustic seals, and exam-suite prep finishes", unit="LS", share=0.21, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
        ],
    },
    "healthcare_dental_office_structural_v1": {
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(key="do_foundation_slab_and_thickening", label="Operatory slab and foundation thickening", unit="SF", share=0.40),
                    _item(key="do_roof_and_ceiling_support", label="Roof and overhead utility support framing", unit="SF", share=0.35),
                    _item(key="do_front_entry_and_canopy", label="Front-entry and canopy structural package", unit="SF", share=0.25),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(key="do_operatory_hvac_zones", label="Operatory HVAC zoning and balancing", unit="SF", share=0.40),
                    _item(key="do_sterilization_room_ventilation", label="Sterilization-room ventilation package", unit="LS", share=0.35, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="do_compressor_room_cooling", label="Compressor and equipment-room cooling", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(key="do_chairside_power_distribution", label="Chairside power distribution and drops", unit="LS", share=0.40, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="do_task_lighting_and_controls", label="Task lighting and dimming controls", unit="SF", share=0.35),
                    _item(key="do_imaging_and_low_voltage", label="Imaging equipment and low-voltage integration", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(key="do_vacuum_air_and_med_gas", label="Chairside vacuum, air, and med-gas lines", unit="LS", share=0.45, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="do_domestic_and_sanitary_runs", label="Domestic and sanitary branch runs", unit="SF", share=0.30),
                    _item(key="do_sterilization_and_lab_sinks", label="Sterilization and lab sink groups", unit="EA", share=0.25, quantity_type="restroom_groups", quantity_params={"sf_per_group": 5000.0, "minimum": 1}),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(key="do_operatory_partitions_and_glazing", label="Operatory partitions and clinical glazing", unit="SF", share=0.40),
                    _item(key="do_hygiene_flooring_and_wall_protection", label="Hygiene flooring and wall protection", unit="SF", share=0.35),
                    _item(key="do_reception_and_assistant_casework", label="Reception and assistant station casework", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
        ],
    },
    "healthcare_hospital_structural_v1": {
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(key="hosp_foundation_and_mat_packages", label="Tower mat foundations and podium structure", unit="SF", share=0.30),
                    _item(key="hosp_vertical_structure_and_core", label="Vertical frame and seismic core package", unit="SF", share=0.25),
                    _item(key="hosp_helipad_and_heavy_supports", label="Heavy equipment and helipad supports", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="hosp_or_and_imaging_vibration_isolation", label="OR/imaging vibration-isolation framing zones", unit="SF", share=0.20),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(key="hosp_central_plant_and_redundant_ahus", label="Central plant and redundant AHU package", unit="LS", share=0.24, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="hosp_critical_care_air_distribution", label="Critical-care air distribution", unit="SF", share=0.22),
                    _item(key="hosp_isolation_and_exhaust_systems", label="Isolation, lab, and OR exhaust systems", unit="LS", share=0.20, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="hosp_humidity_and_pressurization_sequences", label="Humidity control and room pressurization sequences", unit="LS", share=0.18, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="hosp_smoke_control_and_stair_pressurization", label="Smoke-control and stair-pressurization systems", unit="LS", share=0.16, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(key="hosp_main_switchgear_and_feeders", label="Main switchgear and feeder redundancy", unit="LS", share=0.24, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="hosp_critical_branch_distribution", label="Critical branch distribution and ATS", unit="LS", share=0.22, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="hosp_clinical_lighting_and_controls", label="Clinical lighting, controls, and nurse call", unit="SF", share=0.20),
                    _item(key="hosp_generator_paralleling_and_ems", label="Generator paralleling and emergency metering system", unit="LS", share=0.18, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="hosp_imaging_and_or_power_conditioning", label="Imaging/OR power conditioning and isolation transformers", unit="LS", share=0.16, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(key="hosp_med_gas_and_vacuum", label="Medical gas, vacuum, and alarm panels", unit="LS", share=0.30, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="hosp_domestic_and_sanitary_risers", label="Domestic/sanitary risers and branch networks", unit="SF", share=0.25),
                    _item(key="hosp_heavy_fixture_and_drainage", label="Heavy fixture groups and drainage allowances", unit="EA", share=0.25, quantity_type="restroom_groups", quantity_params={"sf_per_group": 18000.0, "minimum": 1}),
                    _item(key="hosp_lab_and_pharmacy_pretreatment", label="Lab/pharmacy pretreatment and specialty waste neutralization", unit="LS", share=0.20, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(key="hosp_clinical_wall_and_ceiling_systems", label="Clinical wall and ceiling system package", unit="SF", share=0.30),
                    _item(key="hosp_patient_room_finish_package", label="Patient room finish package", unit="SF", share=0.25),
                    _item(key="hosp_surgical_and_care_casework", label="Surgical/care casework and millwork", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="hosp_impact_protection_and_cleanability", label="Impact protection, corner guards, and cleanability detailing", unit="SF", share=0.20),
                ],
            ),
        ],
    },
    "healthcare_medical_center_structural_v1": {
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(key="mc_foundation_and_podium", label="Medical-center foundation and podium package", unit="SF", share=0.30),
                    _item(key="mc_multiwing_structure", label="Multi-wing structural frame", unit="SF", share=0.25),
                    _item(key="mc_specialty_suite_reinforcement", label="Specialty-suite reinforcement zones", unit="SF", share=0.25),
                    _item(key="mc_roof_mechanical_support_steel", label="Roof mechanical support steel and screen framing", unit="SF", share=0.20),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(key="mc_main_hvac_and_airside", label="Main HVAC and airside distribution", unit="SF", share=0.24),
                    _item(key="mc_specialty_suite_ventilation", label="Specialty-suite ventilation package", unit="LS", share=0.22, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="mc_controls_and_analytics", label="Building controls and analytics integration", unit="LS", share=0.20, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="mc_outpatient_exhaust_and_return_paths", label="Outpatient exhaust and dedicated return-air paths", unit="SF", share=0.18),
                    _item(key="mc_humidity_and_pressurization_controls", label="Humidity and room-pressurization controls", unit="LS", share=0.16, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(key="mc_switchgear_and_vertical_distribution", label="Switchgear and vertical distribution", unit="LS", share=0.24, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="mc_service_line_power_buildout", label="Service-line power buildout", unit="LS", share=0.22, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="mc_low_voltage_and_monitoring", label="Low-voltage and clinical monitoring tie-ins", unit="SF", share=0.20),
                    _item(key="mc_essential_power_transfer_scheme", label="Essential-power transfer and branch segregation", unit="LS", share=0.18, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="mc_clinical_lighting_and_controls", label="Clinical lighting scenes and occupancy controls", unit="SF", share=0.16),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(key="mc_medical_and_domestic_piping", label="Medical/domestic piping backbone", unit="SF", share=0.30),
                    _item(key="mc_multi_suite_fixture_groups", label="Multi-suite fixture groups", unit="EA", share=0.25, quantity_type="restroom_groups", quantity_params={"sf_per_group": 12000.0, "minimum": 1}),
                    _item(key="mc_sanitary_special_waste", label="Special waste and sanitary tie-ins", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="mc_hot_water_and_recirculation", label="Central hot-water generation and recirculation loops", unit="LS", share=0.20, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(key="mc_public_clinical_finishes", label="Public and clinical-area finish package", unit="SF", share=0.30),
                    _item(key="mc_specialty_suite_finishes", label="Specialty-suite finish upgrades", unit="SF", share=0.25),
                    _item(key="mc_reception_careteam_casework", label="Reception and care-team casework", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="mc_wall_protection_and_door_hardware", label="Wall protection, corner guards, and clinical hardware sets", unit="SF", share=0.20),
                ],
            ),
        ],
    },
    "healthcare_nursing_home_structural_v1": {
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(key="nh_foundation_and_slab", label="Resident-wing foundations and slab package", unit="SF", share=0.40),
                    _item(key="nh_lowrise_frame_and_roof", label="Low-rise frame and roof package", unit="SF", share=0.35),
                    _item(key="nh_common_space_structure", label="Common-space and activity-room structure", unit="SF", share=0.25),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(key="nh_resident_hvac_distribution", label="Resident-room HVAC distribution", unit="SF", share=0.40),
                    _item(key="nh_common_space_ventilation", label="Dining/common-space ventilation", unit="SF", share=0.35),
                    _item(key="nh_nursing_station_controls", label="Nursing-station controls integration", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(key="nh_service_and_panel_distribution", label="Service and panel distribution", unit="LS", share=0.40, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="nh_resident_room_lighting", label="Resident-room and corridor lighting", unit="SF", share=0.35),
                    _item(key="nh_life_safety_and_nurse_call", label="Life safety and nurse-call package", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(key="nh_domestic_hot_and_cold_distribution", label="Domestic hot/cold distribution", unit="SF", share=0.40),
                    _item(key="nh_bathroom_fixture_groups", label="Resident bathroom fixture groups", unit="EA", share=0.35, quantity_type="restroom_groups", quantity_params={"sf_per_group": 6000.0, "minimum": 1}),
                    _item(key="nh_laundry_and_service_plumbing", label="Laundry and service plumbing allowance", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(key="nh_resident_room_finishes", label="Resident-room finishes package", unit="SF", share=0.45),
                    _item(key="nh_corridor_and_common_area_finishes", label="Corridor/common-area finishes", unit="SF", share=0.30),
                    _item(key="nh_dining_and_activity_casework", label="Dining/activity area casework and protection", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
        ],
    },
    "healthcare_rehabilitation_structural_v1": {
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(key="rehab_foundation_and_floor_reinforcement", label="Therapy-floor reinforcement and foundations", unit="SF", share=0.40),
                    _item(key="rehab_large_span_gym_structure", label="Large-span gym and treatment hall structure", unit="SF", share=0.35),
                    _item(key="rehab_pool_support_and_decking", label="Hydrotherapy/pool support and deck structure", unit="SF", share=0.25),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(key="rehab_therapy_hvac_and_ventilation", label="Therapy-gym HVAC and ventilation", unit="SF", share=0.45),
                    _item(key="rehab_hydrotherapy_dehumidification", label="Hydrotherapy dehumidification package", unit="LS", share=0.30, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="rehab_space_controls_and_zoning", label="Treatment-space controls and zoning", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(key="rehab_main_distribution_and_panels", label="Main distribution and therapy panels", unit="LS", share=0.40, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="rehab_treatment_lighting_and_power", label="Treatment lighting and receptacle power", unit="SF", share=0.35),
                    _item(key="rehab_data_monitoring_and_av", label="Monitoring, data, and therapy AV support", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(key="rehab_domestic_and_sanitary_runs", label="Domestic and sanitary plumbing runs", unit="SF", share=0.40),
                    _item(key="rehab_hydrotherapy_plumbing_loop", label="Hydrotherapy plumbing loop and treatment", unit="LS", share=0.35, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="rehab_treatment_room_fixture_groups", label="Treatment-room fixture groups", unit="EA", share=0.25, quantity_type="restroom_groups", quantity_params={"sf_per_group": 8500.0, "minimum": 1}),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(key="rehab_therapy_flooring_and_walls", label="Therapy flooring and wall-impact protection", unit="SF", share=0.45),
                    _item(key="rehab_treatment_suite_finishes", label="Treatment-suite and exam finishes", unit="SF", share=0.30),
                    _item(key="rehab_assistive_casework_and_storage", label="Assistive casework and storage systems", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
        ],
    },
}
