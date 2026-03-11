import { describe, expect, it } from 'vitest';

import { resolveNewProjectAutoDetection } from '../NewProject';

describe('NewProject auto-detection path', () => {
  it('does not emit the orphaned food_court feature id', () => {
    const result = resolveNewProjectAutoDetection({
      description: 'New shopping center with food court in Nashville, TN',
      parsedBuildingType: 'retail',
      parsedSubtype: 'shopping_center',
    });

    expect(result.rawDetectedFeatureIds).not.toContain('food_court');
    expect(result.filteredFeatureIds).not.toContain('food_court');
    expect(result.filteredFeatureIds).toEqual([]);
  });

  it.each([
    {
      name: 'educational gym and cafeteria fallbacks',
      description: 'New 68000 sf middle school with gym and cafeteria in Nashville, TN',
      parsedBuildingType: 'educational',
      parsedSubtype: 'middle_school',
      expectedAllowed: [
        'athletic_field',
        'auditorium',
        'cafeteria',
        'computer_lab',
        'gymnasium',
        'science_labs',
      ],
      expectedRaw: ['cafeteria', 'gymnasium'],
      expectedFiltered: ['cafeteria', 'gymnasium'],
    },
    {
      name: 'recreation pool fallback',
      description: 'New 42000 sf fitness center with pool in Nashville, TN',
      parsedBuildingType: 'recreation',
      parsedSubtype: 'fitness_center',
      expectedAllowed: [
        'basketball_court',
        'group_fitness',
        'juice_bar',
        'pool',
        'spa_area',
      ],
      expectedRaw: ['fitness_center', 'pool'],
      expectedFiltered: ['pool'],
    },
    {
      name: 'legacy residential parking garage and pool fallback',
      description: 'New residential tower with parking garage and pool in Nashville, TN',
      parsedBuildingType: 'residential',
      expectedAllowed: ['clubhouse', 'fitness', 'parking_garage', 'pool', 'rooftop'],
      expectedRaw: ['parking_garage', 'pool'],
      expectedFiltered: ['parking_garage', 'pool'],
    },
    {
      name: 'legacy commercial cafeteria fallback',
      description: 'New commercial campus with cafeteria in Nashville, TN',
      parsedBuildingType: 'commercial',
      expectedAllowed: ['cafeteria', 'conference', 'data_center', 'fitness', 'parking_deck'],
      expectedRaw: ['cafeteria'],
      expectedFiltered: ['cafeteria'],
    },
    {
      name: 'civic gymnasium detection now flows through shared civic detector coverage',
      description: 'New 38000 sf community center with gym in Nashville, TN',
      parsedBuildingType: 'civic',
      parsedSubtype: 'community_center',
      expectedAllowed: [
        'fitness_center',
        'gymnasium',
        'kitchen',
        'multipurpose_room',
        'outdoor_pavilion',
      ],
      expectedRaw: ['gymnasium'],
      expectedFiltered: ['gymnasium'],
    },
    {
      name: 'recreation gymnasium detection now flows through shared recreation detector coverage',
      description: 'Renovate a 60000 sf recreation center with gym in Nashville, TN',
      parsedBuildingType: 'recreation',
      parsedSubtype: 'recreation_center',
      expectedAllowed: [
        'craft_room',
        'dance_studio',
        'game_room',
        'gymnasium',
        'outdoor_courts',
      ],
      expectedRaw: ['gymnasium'],
      expectedFiltered: ['gymnasium'],
    },
  ])(
    'resolves raw, allowed, and filtered ids for $name',
    ({
      description,
      parsedBuildingType,
      parsedSubtype,
      expectedAllowed,
      expectedRaw,
      expectedFiltered,
    }) => {
      const result = resolveNewProjectAutoDetection({
        description,
        parsedBuildingType,
        parsedSubtype,
      });

      expect(result.effectiveBuildingType).toBe(parsedBuildingType);
      expect(result.resolvedSubtype).toBe(parsedSubtype);
      expect(result.rawDetectedFeatureIds.sort()).toEqual(expectedRaw.sort());
      expect(result.allowedFeatureIds.sort()).toEqual(expectedAllowed.sort());
      expect(result.filteredFeatureIds.sort()).toEqual(expectedFiltered.sort());
    }
  );

  it.each([
    {
      name: 'quick service double drive thru exact id',
      description: 'New 6,500 SF quick service restaurant with double drive thru in Nashville, TN',
      parsedBuildingType: 'restaurant',
      parsedSubtype: 'quick_service',
      expectedFeatureId: 'double_drive_thru',
      unexpectedFilteredId: 'drive_thru',
    },
    {
      name: 'surgical center operating rooms exact id',
      description: 'New 24,000 SF ambulatory surgery center with 6 operating rooms in Nashville, TN',
      parsedBuildingType: 'healthcare',
      parsedSubtype: 'surgical_center',
      expectedFeatureId: 'operating_room',
    },
    {
      name: 'dental office operatories exact id',
      description: 'New 4,500 SF dental office with 9 operatories in Nashville, TN',
      parsedBuildingType: 'healthcare',
      parsedSubtype: 'dental_office',
      expectedFeatureId: 'operatory',
    },
    {
      name: 'imaging center MRI suites exact id',
      description: 'New 12,000 SF imaging center with 2 MRI suites and 1 CT suite in Nashville, TN',
      parsedBuildingType: 'healthcare',
      parsedSubtype: 'imaging_center',
      expectedFeatureId: 'mri_suite',
    },
    {
      name: 'distribution center counted loading docks map to extra loading docks',
      description: 'New 220,000 SF distribution center with 10 loading docks and refrigerated area in Nashville, TN',
      parsedBuildingType: 'industrial',
      parsedSubtype: 'distribution_center',
      expectedFeatureId: 'extra_loading_docks',
      unexpectedFilteredId: 'loading_docks',
    },
    {
      name: 'full service live kitchen exact id',
      description: 'New 6,500 SF full service restaurant with live kitchen in Nashville, TN',
      parsedBuildingType: 'restaurant',
      parsedSubtype: 'full_service',
      expectedFeatureId: 'live_kitchen',
    },
    {
      name: 'fine dining dry aging room exact id',
      description: 'New 6,500 SF fine dining restaurant with dry aging room in Nashville, TN',
      parsedBuildingType: 'restaurant',
      parsedSubtype: 'fine_dining',
      expectedFeatureId: 'dry_aging_room',
    },
    {
      name: 'fine dining pastry kitchen exact id',
      description: 'New 6,500 SF fine dining restaurant with pastry kitchen in Nashville, TN',
      parsedBuildingType: 'restaurant',
      parsedSubtype: 'fine_dining',
      expectedFeatureId: 'pastry_kitchen',
    },
  ])(
    'keeps first-wave migrated exact ids through filtering for $name',
    ({
      description,
      parsedBuildingType,
      parsedSubtype,
      expectedFeatureId,
      unexpectedFilteredId,
    }) => {
      const result = resolveNewProjectAutoDetection({
        description,
        parsedBuildingType,
        parsedSubtype,
      });

      expect(result.rawDetectedFeatureIds).toContain(expectedFeatureId);
      expect(result.allowedFeatureIds).toContain(expectedFeatureId);
      expect(result.filteredFeatureIds).toContain(expectedFeatureId);
      if (unexpectedFilteredId) {
        expect(result.filteredFeatureIds).not.toContain(unexpectedFilteredId);
      }
    }
  );
});
