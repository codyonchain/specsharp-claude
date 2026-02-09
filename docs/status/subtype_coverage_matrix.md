# Subtype Coverage Matrix

| building_type | subtype | wave1 | dealshield_tile_profile | dealshield_has_tile_profile | dealshield_has_content_profile | scope_items_profile | scope_items_overrides | facility_metrics_profile | has_special_features | subtype_doc_exists | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| civic | community_center | false | civic_baseline_v1 | false | false | civic_baseline_structural_v1 | false |  | true | true | 🟡 |
| civic | courthouse | false | civic_baseline_v1 | false | false | civic_baseline_structural_v1 | false |  | true | true | 🟡 |
| civic | government_building | false |  | false | false |  | false |  | true | false | 🔴 |
| civic | library | false |  | false | false |  | false |  | true | true | 🟡 |
| civic | public_safety | false | civic_baseline_v1 | false | false | civic_baseline_structural_v1 | false |  | true | true | 🟡 |
| educational | community_college | false |  | false | false |  | false |  | true | false | 🔴 |
| educational | elementary_school | false |  | false | false |  | false |  | true | false | 🔴 |
| educational | high_school | false |  | false | false |  | false |  | true | false | 🔴 |
| educational | middle_school | false |  | false | false |  | false |  | true | false | 🔴 |
| educational | university | false |  | false | false |  | false |  | true | false | 🔴 |
| healthcare | dental_office | false |  | false | false |  | false | healthcare_outpatient | true | false | 🔴 |
| healthcare | hospital | false |  | false | false |  | false |  | true | false | 🔴 |
| healthcare | imaging_center | false |  | false | false |  | false | healthcare_outpatient | true | false | 🔴 |
| healthcare | medical_center | false |  | false | false |  | false |  | true | false | 🔴 |
| healthcare | medical_office_building | true | healthcare_medical_office_building_v1 | true | true | healthcare_medical_office_building_structural_v1 | false | healthcare_outpatient | true | true | ✅ |
| healthcare | nursing_home | false |  | false | false |  | false |  | true | false | 🔴 |
| healthcare | outpatient_clinic | false |  | false | false |  | false | healthcare_outpatient | true | false | 🔴 |
| healthcare | rehabilitation | false |  | false | false |  | false |  | true | false | 🔴 |
| healthcare | surgical_center | false |  | false | false |  | false | healthcare_outpatient | true | false | 🔴 |
| healthcare | urgent_care | true | healthcare_urgent_care_v1 | true | true | healthcare_urgent_care_structural_v1 | false | healthcare_outpatient | true | true | ✅ |
| hospitality | full_service_hotel | false |  | false | false |  | false |  | true | false | 🔴 |
| hospitality | limited_service_hotel | true | hospitality_limited_service_hotel_v1 | true | true | hospitality_limited_service_hotel_structural_v1 | false |  | true | true | ✅ |
| industrial | cold_storage | true | industrial_cold_storage_v1 | true | true | industrial_cold_storage_structural_v1 | false |  | true | true | ✅ |
| industrial | distribution_center | false |  | false | false | industrial_warehouse_structural_v1 | false |  | true | true | 🟡 |
| industrial | flex_space | false |  | false | false |  | false |  | true | true | 🟡 |
| industrial | manufacturing | false |  | false | false |  | false |  | true | true | 🟡 |
| industrial | warehouse | true | industrial_warehouse_v1 | true | true | industrial_warehouse_structural_v1 | false |  | false | true | ✅ |
| mixed_use | hotel_retail | false |  | false | false |  | false |  | true | false | 🔴 |
| mixed_use | office_residential | false |  | false | false |  | false |  | true | false | 🔴 |
| mixed_use | retail_residential | false |  | false | false |  | false |  | true | false | 🔴 |
| mixed_use | transit_oriented | false |  | false | false |  | false |  | true | false | 🔴 |
| mixed_use | urban_mixed | false |  | false | false |  | false |  | true | false | 🔴 |
| multifamily | affordable_housing | false |  | false | false |  | false |  | false | false | 🔴 |
| multifamily | luxury_apartments | false |  | false | false |  | false |  | true | false | 🔴 |
| multifamily | market_rate_apartments | false |  | false | false |  | false |  | false | false | 🔴 |
| office | class_a | false |  | false | false |  | false |  | true | false | 🔴 |
| office | class_b | false |  | false | false |  | false |  | true | false | 🔴 |
| parking | automated_parking | false |  | false | false |  | false |  | true | false | 🔴 |
| parking | parking_garage | false |  | false | false |  | false |  | true | false | 🔴 |
| parking | surface_parking | false |  | false | false |  | false |  | true | false | 🔴 |
| parking | underground_parking | false |  | false | false |  | false |  | true | false | 🔴 |
| recreation | aquatic_center | false |  | false | false |  | false |  | true | false | 🔴 |
| recreation | fitness_center | false |  | false | false |  | false |  | true | false | 🔴 |
| recreation | recreation_center | false |  | false | false |  | false |  | true | false | 🔴 |
| recreation | sports_complex | false |  | false | false |  | false |  | true | false | 🔴 |
| recreation | stadium | false |  | false | false |  | false |  | true | false | 🔴 |
| restaurant | bar_tavern | false |  | false | false |  | false |  | true | false | 🔴 |
| restaurant | cafe | false |  | false | false |  | false |  | true | false | 🔴 |
| restaurant | fine_dining | false |  | false | false |  | false |  | true | false | 🔴 |
| restaurant | full_service | false |  | false | false |  | false |  | true | false | 🔴 |
| restaurant | quick_service | true | restaurant_quick_service_v1 | true | true | restaurant_quick_service_structural_v1 | false |  | true | true | ✅ |
| retail | big_box | false |  | false | false |  | false |  | true | false | 🔴 |
| retail | shopping_center | false |  | false | false |  | false |  | true | false | 🔴 |
| specialty | broadcast_facility | false |  | false | false |  | false |  | true | false | 🔴 |
| specialty | car_dealership | false |  | false | false |  | false |  | true | false | 🔴 |
| specialty | data_center | false |  | false | false |  | false |  | true | false | 🔴 |
| specialty | laboratory | false |  | false | false |  | false |  | true | false | 🔴 |
| specialty | self_storage | false |  | false | false |  | false |  | true | false | 🔴 |
