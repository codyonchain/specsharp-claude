import '@testing-library/jest-dom';
import { expect } from 'vitest';

// Global test setup
beforeAll(() => {
  // Set test environment variables
  process.env.NODE_ENV = 'test';
  process.env.API_URL = 'http://localhost:8001';
  
  // Mock console methods to reduce noise in test output
  global.console = {
    ...console,
    error: vi.fn(),
    warn: vi.fn(),
  };
});

afterAll(() => {
  // Cleanup
  vi.clearAllMocks();
});

// Custom matchers
expect.extend({
  toBeWithinRange(received: number, min: number, max: number) {
    const pass = received >= min && received <= max;
    
    return {
      pass,
      message: () =>
        pass
          ? `Expected ${received} not to be within range ${min}-${max}`
          : `Expected ${received} to be within range ${min}-${max}`,
    };
  },
  
  toBeWithinPercentage(received: number, expected: number, tolerance: number) {
    const diff = Math.abs(received - expected);
    const pass = diff <= tolerance;
    
    return {
      pass,
      message: () =>
        pass
          ? `Expected ${received} not to be within ${tolerance} of ${expected}`
          : `Expected ${received} to be within ${tolerance} of ${expected} (diff: ${diff})`,
    };
  }
});

// Declare custom matchers for TypeScript
declare global {
  namespace Vi {
    interface Assertion {
      toBeWithinRange(min: number, max: number): void;
      toBeWithinPercentage(expected: number, tolerance: number): void;
    }
  }
}

// Mock fetch for unit tests
global.fetch = vi.fn();

// Reset mocks between tests
beforeEach(() => {
  vi.clearAllMocks();
});