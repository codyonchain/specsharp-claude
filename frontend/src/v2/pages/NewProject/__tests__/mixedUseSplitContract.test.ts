import {
  appendMixedUseSplitHintToDescription,
  detectMixedUseIntent,
  detectMixedUseSplitHintFromDescription,
  detectMixedUseSubtypeFromDescription,
  formatMixedUseSplitValue,
  resolveMixedUseSplitContract,
} from "../../../utils/buildingTypeDetection";

describe("mixed-use split contract detection", () => {
  it("detects all five canonical mixed_use subtypes from NewProject prompt language", () => {
    expect(
      detectMixedUseSubtypeFromDescription(
        "New 180000 sf office residential mixed-use tower in Nashville, TN"
      ).subtype
    ).toBe("office_residential");
    expect(
      detectMixedUseSubtypeFromDescription(
        "Mixed-use project with retail and residential over podium parking in Nashville, TN"
      ).subtype
    ).toBe("retail_residential");
    expect(
      detectMixedUseSubtypeFromDescription(
        "Hotel retail mixed-use program with arcade and spa in downtown Nashville, TN"
      ).subtype
    ).toBe("hotel_retail");
    expect(
      detectMixedUseSubtypeFromDescription(
        "Transit-oriented development with a station plaza and bike facility"
      ).subtype
    ).toBe("transit_oriented");
    expect(
      detectMixedUseSubtypeFromDescription(
        "Urban mixed vertical development with live-work-play uses"
      ).subtype
    ).toBe("urban_mixed");
  });

  it("maps hotel_residential aliases to hotel_retail with provenance", () => {
    const detected = detectMixedUseSubtypeFromDescription(
      "Mixed-use hotel residential tower with conference center and restaurants"
    );

    expect(detected.subtype).toBe("hotel_retail");
    expect(detected.aliasMapping).toBeDefined();
    expect(detected.aliasMapping?.from).toBe("hotel_residential");
    expect(detected.aliasMapping?.to).toBe("hotel_retail");
  });

  it("guards obvious non-mixed-use prompts from false-positive mixed_use intent", () => {
    expect(
      detectMixedUseIntent("New 140000 sf class_a office tower in Nashville, TN")
    ).toBe(false);
    expect(
      detectMixedUseIntent("Build a full service hotel with ballroom and spa")
    ).toBe(false);
    expect(
      detectMixedUseIntent("Mixed-use office and residential tower with amenity deck")
    ).toBe(true);
  });

  it("detects required split patterns in NewProject description prompts", () => {
    const ratioHint = detectMixedUseSplitHintFromDescription(
      "New mixed-use office and residential tower with a 60/40 split",
      "office_residential"
    );
    expect(ratioHint?.pattern).toBe("ratio_pair");

    const percentHint = detectMixedUseSplitHintFromDescription(
      "Mixed-use project with 70% office / 30% residential",
      "office_residential"
    );
    expect(percentHint?.pattern).toBe("component_percent");

    const mostlyHint = detectMixedUseSplitHintFromDescription(
      "Retail + residential mixed-use project that is mostly residential",
      "retail_residential"
    );
    expect(mostlyHint?.pattern).toBe("mostly_component");

    const heavyHint = detectMixedUseSplitHintFromDescription(
      "Mixed-use retail residential project with a retail-heavy program",
      "retail_residential"
    );
    expect(heavyHint?.pattern).toBe("heavy_component");

    const balancedHint = detectMixedUseSplitHintFromDescription(
      "Mixed-use office residential project with a balanced program",
      "office_residential"
    );
    expect(balancedHint?.pattern).toBe("balanced_pair");
  });

  it("normalizes and infers deterministic splits for user edits", () => {
    const inferred = resolveMixedUseSplitContract({
      subtype: "office_residential",
      userComponents: { office: 70 },
    });

    expect(inferred.source).toBe("user_input");
    expect(inferred.normalization_applied).toBe(true);
    expect(inferred.inference_applied).toBe(true);
    expect(inferred.value.office).toBe(70);
    expect(inferred.value.residential).toBe(30);

    const normalized = resolveMixedUseSplitContract({
      subtype: "office_residential",
      userComponents: { office: 1, residential: 1, retail: 1 },
    });
    const total = Object.values(normalized.value).reduce((sum, value) => sum + value, 0);
    expect(total).toBeCloseTo(100, 2);
    expect(normalized.normalization_applied).toBe(true);
  });

  it("keeps invalid mixes explicit with default fallback (no silent coercion)", () => {
    const invalid = resolveMixedUseSplitContract({
      subtype: "urban_mixed",
      userComponents: { unknown_component: 100 } as unknown as Record<string, number>,
    });

    expect(invalid.source).toBe("default");
    expect(invalid.invalid_mix?.reason).toBe("unsupported_component");
    expect(invalid.value.office).toBe(50);
    expect(invalid.value.residential).toBe(50);
  });

  it("serializes split hints into analysis handoff text without duplication", () => {
    const contract = resolveMixedUseSplitContract({
      subtype: "office_residential",
      userComponents: { office: 70, residential: 30 },
    });

    const withHint = appendMixedUseSplitHintToDescription(
      "Mixed-use office residential tower in Nashville, TN",
      contract
    );
    const withHintAgain = appendMixedUseSplitHintToDescription(withHint, contract);

    expect(withHint).toContain("[mixed_use_split:");
    expect(withHint).toContain("70% office / 30% residential");
    expect(withHintAgain).toBe(withHint);
    expect(formatMixedUseSplitValue(contract.value)).toBe("70% office / 30% residential");
  });

  it("uses explicit default split when no split cues are present", () => {
    const resolved = resolveMixedUseSplitContract({
      description: "New mixed-use office and residential tower in Nashville, TN",
      subtype: "office_residential",
    });

    expect(resolved.source).toBe("default");
    expect(resolved.value.office).toBe(50);
    expect(resolved.value.residential).toBe(50);
  });
});
