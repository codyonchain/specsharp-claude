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
});
