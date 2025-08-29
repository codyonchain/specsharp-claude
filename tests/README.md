# SpecSharp Test Suite

## Day 2 Part 2: Trade Breakdown & Executive Metrics Tests

### Test Files Created
1. **tests/e2e/critical-paths/trade-breakdown.spec.ts** - Validates trade cost percentages
2. **tests/e2e/critical-paths/executive-metrics.spec.ts** - Tests ROI and investment metrics
3. **tests/e2e/critical-paths/data-validation.spec.ts** - Input validation and edge cases

### Current Status
✅ All test files created
⚠️ Authentication flow needs adjustment - app uses OAuth/Google login
⚠️ Landing page flow detected - "Try it Now" button needs to be clicked first

### Known Issues
1. **OAuth Authentication**: App uses Google OAuth instead of traditional login
   - Tests updated to skip authentication
   - May need to mock OAuth or use test environment with bypass

2. **Landing Page**: App shows marketing page before project creation
   - Tests need to click "Try it Now - No Signup" button
   - Actual project creation form may be behind this flow

### Running Tests
```bash
# Run all tests
npx playwright test --config=tests/playwright.config.ts

# Run specific test file
npx playwright test tests/e2e/critical-paths/trade-breakdown.spec.ts --config=tests/playwright.config.ts

# Run with browser visible (helpful for debugging)
npx playwright test --headed --config=tests/playwright.config.ts

# Run single test
npx playwright test -g "healthcare" --config=tests/playwright.config.ts
```

### Test Coverage

#### Trade Breakdown Tests
- Healthcare: Mechanical ~32%, Electrical ~12%, Plumbing ~8%
- Restaurant: Higher mechanical/plumbing for kitchen
- Office: Lower plumbing ~6%, higher structural

#### Executive Metrics Tests
- Healthcare ROI validation (6-15% expected)
- Restaurant investment decision display
- Office efficiency metrics

#### Data Validation Tests
- Empty input validation
- Extreme values (100 sf and 5M sf buildings)
- Invalid locations
- Special characters in input
- Mixed-use building parsing

### Next Steps
1. Work with development team to create test-specific authentication bypass
2. Or implement OAuth mock for testing
3. Verify actual project creation flow once past landing page
4. Add API-level tests to bypass UI authentication issues