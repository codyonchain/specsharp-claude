import { describe, expect, it } from "vitest";

import {
  detectParkingSubtypeFromDescription,
  isCanonicalParkingSubtype,
  resolveParkingIntentFromDescription,
} from "../../../utils/buildingTypeDetection";

describe("parking intent detection", () => {
  it("demotes parking mentions when multifamily/hospitality/office are primary", () => {
    const multifamily = resolveParkingIntentFromDescription(
      "luxury apartments with parking garage"
    );
    expect(multifamily.shouldRouteToParking).toBe(false);
    expect(multifamily.subtype).toBe("parking_garage");
    expect(multifamily.detectionSource).toBe("buildingTypeDetection.parking_intent");
    expect(multifamily.conflictOutcome).toBe("parking_demoted_multifamily_primary");

    const hospitality = resolveParkingIntentFromDescription(
      "hotel with underground parking"
    );
    expect(hospitality.shouldRouteToParking).toBe(false);
    expect(hospitality.subtype).toBe("underground_parking");
    expect(hospitality.detectionSource).toBe("buildingTypeDetection.parking_intent");
    expect(hospitality.conflictOutcome).toBe("parking_demoted_hospitality_primary");

    const office = resolveParkingIntentFromDescription(
      "office tower with structured parking"
    );
    expect(office.shouldRouteToParking).toBe(false);
    expect(office.subtype).toBe("parking_garage");
    expect(office.detectionSource).toBe("buildingTypeDetection.parking_intent");
    expect(office.conflictOutcome).toBe("parking_demoted_office_primary");
  });

  it("routes standalone or parking-primary prompts to parking", () => {
    const standalone = resolveParkingIntentFromDescription(
      "new standalone parking garage"
    );
    expect(standalone.shouldRouteToParking).toBe(true);
    expect(standalone.subtype).toBe("parking_garage");
    expect(standalone.detectionSource).toBe("buildingTypeDetection.parking_intent");
    expect(standalone.conflictOutcome).toBe("parking_primary_standalone");

    const automated = resolveParkingIntentFromDescription(
      "automated parking structure"
    );
    expect(automated.shouldRouteToParking).toBe(true);
    expect(automated.subtype).toBe("automated_parking");
    expect(automated.detectionSource).toBe("buildingTypeDetection.parking_intent");
    expect(automated.conflictOutcome).toBe("parking_primary_asset_intent");

    const surfaceExpansion = resolveParkingIntentFromDescription(
      "surface parking lot expansion"
    );
    expect(surfaceExpansion.shouldRouteToParking).toBe(true);
    expect(surfaceExpansion.subtype).toBe("surface_parking");
    expect(surfaceExpansion.detectionSource).toBe("buildingTypeDetection.parking_intent");
    expect(surfaceExpansion.conflictOutcome).toBe("parking_primary_asset_intent");
  });

  it("preserves explicit unknown subtype behavior", () => {
    const subtype = detectParkingSubtypeFromDescription(
      "new parking facility with valet and EV chargers"
    );
    expect(subtype).toBeUndefined();

    const resolution = resolveParkingIntentFromDescription(
      "new parking facility with valet and EV chargers"
    );
    expect(resolution.shouldRouteToParking).toBe(true);
    expect(resolution.subtype).toBeUndefined();
    expect(resolution.detectionSource).toBe("buildingTypeDetection.parking_intent");
    expect(resolution.conflictOutcome).toBe("parking_primary_action");
  });

  it("keeps canonical subtype checks strict", () => {
    expect(isCanonicalParkingSubtype("surface_parking")).toBe(true);
    expect(isCanonicalParkingSubtype("parking_garage")).toBe(true);
    expect(isCanonicalParkingSubtype("unknown_parking_variant")).toBe(false);
  });
});
