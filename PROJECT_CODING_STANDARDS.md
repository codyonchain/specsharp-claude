# PROJECT CODING STANDARDS - MANDATORY FOR ALL CODE

## 🔴 CRITICAL RULES - NEVER VIOLATE

### 1. Frontend Display Only - No Logic
- **Frontend ONLY displays data** from backend
- **ZERO calculations** in frontend code
- **ZERO hardcoded values** (no magic numbers, no hardcoded strings)
- **ZERO business logic** in frontend

### 2. Backend is Single Source of Truth
- **ALL calculations** happen in Python engines
- **ALL business logic** lives in backend
- **ALL constants** defined in backend configs
- **ALL derived values** computed by backend

### 3. Data Flow is One-Way
```
Backend Engine → API Response → Frontend Display
↑                              ↓
└──────── User Input ←─────────┘
```

## 📁 FILE MANAGEMENT RULES

### Always Edit Existing Files
```bash
# ✅ CORRECT - Edit existing file
cat > frontend/src/v2/pages/ProjectView/ExecutiveView.tsx

# ❌ WRONG - Creating new files
cat > frontend/src/v2/pages/ProjectView/ExecutiveView_new.tsx
cat > frontend/src/v2/pages/ProjectView/ExecutiveView_fixed.tsx
```

### File Paths Must Be Exact
- Use the ACTUAL file paths in the project
- Don't create "backup" or "temp" versions
- Don't reorganize without explicit permission

## 💻 FRONTEND CODING PATTERNS

### ✅ CORRECT Frontend Patterns
```javascript
// 1. Display from backend
const roi = displayData.roi;
const units = calculations.project_info.unit_count;

// 2. Format for display only
<p>{formatters.currency(displayData.totalCost)}</p>
<p>{formatters.percentage(displayData.roi)}</p>

// 3. Use mapper for backend data
const displayData = BackendDataMapper.mapToDisplay(analysis);

// 4. Conditional display (not logic)
{displayData.investmentDecision === 'GO' && <SuccessAlert />}
```

### ❌ WRONG Frontend Patterns
```javascript
// 1. NEVER calculate in frontend
const roi = (revenue - costs) / costs;  // ❌ FORBIDDEN
const units = squareFootage / 1100;     // ❌ FORBIDDEN

// 2. NEVER hardcode values
const rentPerUnit = 3500;               // ❌ FORBIDDEN
const occupancyRate = 0.93;             // ❌ FORBIDDEN

// 3. NEVER hardcode conditional values
const rent = type === 'luxury' ? 3500 : 2200;  // ❌ FORBIDDEN

// 4. NEVER sum or aggregate in frontend
const total = trades.reduce((sum, t) => sum + t.cost, 0);  // ❌ FORBIDDEN
```

## 🔧 BACKEND CODING PATTERNS

### Backend Must Provide Complete Data
```python
# Backend MUST return ALL display values
def calculate(self):
    return {
        'calculations': {
            'totals': {
                'total_project_cost': 78384600,
                'cost_per_sf': 261,  # Backend calculates this
                'cost_per_unit': 288179,  # Backend calculates this
            },
            'ownership_analysis': {
                'roi': 0.082,  # Backend calculates
                'npv': 22500000,  # Backend calculates
                'irr': 0.07,  # Backend calculates
                'payback_period': 14.4,  # Backend calculates
            },
            'department_allocation': [  # Backend provides complete list
                {'name': 'Residential Units', 'percent': 0.70, 'amount': 54869220},
                {'name': 'Common Areas', 'percent': 0.20, 'amount': 15676920},
            ]
        }
    }
```

## 🎨 DISPLAY FORMATTING RULES

### Use Formatters Utility for ALL Display
```javascript
import { formatters } from '../../utils/displayFormatters';

// Use the appropriate formatter for each type
formatters.currency(value)        // $78.4M
formatters.currencyExact(value)   // $78,384,600
formatters.percentage(value)      // 8.2%
formatters.decimal(value, 2)      // 14.37
formatters.years(value)           // 14.4 yrs
formatters.multiplier(value)      // 1.43x
formatters.squareFeet(value)      // 300,000 SF
formatters.costPerSF(value)       // $261/SF
```

## 🔄 DATA MAPPING RULES

### Use BackendDataMapper for Complex Data
```javascript
// Map backend response to display data
const displayData = BackendDataMapper.mapToDisplay(project.analysis);

// Mapper handles:
// - Finding data in various backend locations
// - Providing fallbacks for missing data
// - Standardizing property names
// - NO CALCULATIONS - only mapping
```

## 📊 HANDLING MISSING DATA

### Frontend Handles Missing Data Gracefully
```javascript
// ✅ CORRECT - Graceful fallbacks
const revenue = displayData.annualRevenue || 0;
const label = displayData.unitLabel || 'Units';

// ✅ CORRECT - Show N/A for missing
<p>{formatters.currency(revenue) || 'N/A'}</p>

// ❌ WRONG - Calculate missing data
const revenue = units * rentPerUnit * 12;  // NEVER!
```

## 🚀 WHEN ADDING NEW FEATURES

### Process for New Display Elements

1. **FIRST**: Check if backend provides the data
```javascript
// Check what's in the response
console.log('Backend data:', calculations);
```

2. **IF NOT**: Request backend changes FIRST
```python
# Add to engine calculation
'new_metric': self.calculate_new_metric()
```

3. **THEN**: Update frontend to display
```javascript
// Only after backend provides it
const newMetric = calculations.new_metric;
```

## 🧪 TESTING STANDARDS

### Verify Data Flow
```javascript
// Test that frontend only displays
expect(component).not.toContain('*');  // No math
expect(component).not.toContain('/');  // No division
expect(component).not.toContain('1100');  // No magic numbers
```

## 📝 CODE REVIEW CHECKLIST

Before submitting any frontend code:

- [ ] No calculations (*, /, +, -)
- [ ] No hardcoded numbers
- [ ] No hardcoded strings for business values
- [ ] All data from displayData or calculations
- [ ] All numbers formatted with formatters
- [ ] Handles missing data gracefully
- [ ] No new files created (unless approved)

## 🎯 QUICK REFERENCE

| Task | Wrong ❌ | Correct ✅ |
|------|----------|------------|
| Show ROI | `const roi = profit/cost` | `displayData.roi` |
| Show units | `const units = sf/1100` | `calculations.unit_count` |
| Format money | `${value}M` | `formatters.currency(value)` |
| Show rent | `const rent = 3500` | `calculations.monthly_rent` |
| Sum costs | `trades.reduce(...)` | `calculations.total_cost` |
| Check type | `if (type === 'luxury')` | `if (displayData.isLuxury)` |

## 🚨 ENFORCEMENT

**ANY code that violates these standards should be immediately flagged and rewritten.**

Remember: The frontend is a DISPLAY LAYER ONLY. If you're thinking about HOW to calculate something, you're in the wrong place - that belongs in the backend.