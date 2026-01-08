/**
 * Frontend Standards Compliance Test
 * Tests that frontend follows PROJECT_CODING_STANDARDS.md
 */

import fs from 'fs';
import path from 'path';

// Color codes for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  bold: '\x1b[1m'
};

// Files to test
const TEST_FILES = [
  'src/v2/pages/ProjectView/ExecutiveView.tsx',
  'src/v2/pages/ProjectView/ExecutiveViewComplete.tsx',
  'src/v2/pages/ProjectView/ConstructionView.tsx',
  'src/v2/pages/ProjectView/TradeBreakdown.tsx',
  'src/v2/pages/Dashboard/Dashboard.tsx',
  'src/v2/utils/backendDataMapper.ts'
];

// Forbidden patterns that violate standards
const FORBIDDEN_PATTERNS = [
  {
    name: 'Hardcoded rent values',
    pattern: /\b(3500|2200)\b(?!.*\/\/)/g,
    message: 'Found hardcoded rent value - should come from backend'
  },
  {
    name: 'Hardcoded unit size',
    pattern: /\b1100\b(?!.*\/\/)/g,
    message: 'Found hardcoded unit size (1100) - should come from backend'
  },
  {
    name: 'Hardcoded occupancy rate',
    pattern: /0\.93\b/g,
    message: 'Found hardcoded occupancy rate (0.93) - should come from backend'
  },
  {
    name: 'Frontend calculations',
    pattern: /const\s+\w+\s*=\s*[^=\n]*[\*\/\+\-]\s*[^=\n]*(?!.*\/\/)/g,
    message: 'Found calculation in frontend - all calculations should be in backend'
  },
  {
    name: 'Array reduce for summing',
    pattern: /\.reduce\s*\(\s*\(\s*sum/g,
    message: 'Found reduce operation for summing - totals should come from backend'
  },
  {
    name: 'Direct division for calculations',
    pattern: /\/\s*(?:squareFootage|square_footage|1000|12)(?!.*\/\/)/g,
    message: 'Found division operation - calculations should be in backend'
  },
  {
    name: 'NaN or undefined in display',
    pattern: /\bNaN\b|\bundefined\b/g,
    message: 'Found NaN or undefined - handle missing data gracefully'
  }
];

// Required patterns that should be present
const REQUIRED_PATTERNS = [
  {
    name: 'Using formatters',
    pattern: /formatters?\.\w+/g,
    message: 'Should use formatters for display values'
  },
  {
    name: 'Using displayData or calculations',
    pattern: /(?:displayData|calculations)\.\w+/g,
    message: 'Should pull data from displayData or calculations'
  },
  {
    name: 'Fallback for missing data',
    pattern: /\|\|\s*(?:0|''|'N\/A'|\[\])/g,
    message: 'Should have fallbacks for missing data'
  }
];

// Test results
const results = {
  passed: [],
  failed: [],
  warnings: []
};

/**
 * Test a single file for standards compliance
 */
function testFile(filePath) {
  console.log(`\n${colors.cyan}Testing: ${filePath}${colors.reset}`);
  
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    let hasViolations = false;
    
    // Check for forbidden patterns
    for (const rule of FORBIDDEN_PATTERNS) {
      const matches = content.match(rule.pattern);
      if (matches && matches.length > 0) {
        // Filter out false positives (comments, imports, etc.)
        const realMatches = matches.filter(match => {
          const lineWithMatch = content.split('\n').find(line => line.includes(match));
          return lineWithMatch && 
                 !lineWithMatch.trim().startsWith('//') && 
                 !lineWithMatch.trim().startsWith('*') &&
                 !lineWithMatch.includes('import ');
        });
        
        if (realMatches.length > 0) {
          hasViolations = true;
          results.failed.push({
            file: filePath,
            rule: rule.name,
            message: rule.message,
            count: realMatches.length,
            examples: realMatches.slice(0, 3)
          });
          console.log(`  ${colors.red}❌ ${rule.name}: ${realMatches.length} violation(s)${colors.reset}`);
          console.log(`     ${colors.yellow}${rule.message}${colors.reset}`);
        }
      }
    }
    
    // Check for required patterns
    for (const rule of REQUIRED_PATTERNS) {
      const matches = content.match(rule.pattern);
      if (!matches || matches.length < 3) {
        results.warnings.push({
          file: filePath,
          rule: rule.name,
          message: rule.message,
          count: matches ? matches.length : 0
        });
        console.log(`  ${colors.yellow}⚠ ${rule.name}: Only ${matches ? matches.length : 0} instances found${colors.reset}`);
        console.log(`     ${colors.yellow}${rule.message}${colors.reset}`);
      }
    }
    
    if (!hasViolations) {
      results.passed.push(filePath);
      console.log(`  ${colors.green}✅ No violations found${colors.reset}`);
    }
    
  } catch (error) {
    console.log(`  ${colors.red}❌ Error reading file: ${error.message}${colors.reset}`);
  }
}

/**
 * Print test summary
 */
function printSummary() {
  console.log(`\n${colors.bold}${colors.blue}${'='.repeat(60)}`);
  console.log('📊 FRONTEND STANDARDS COMPLIANCE REPORT');
  console.log(`${'='.repeat(60)}${colors.reset}\n`);
  
  console.log(`${colors.green}✅ Files Passed: ${results.passed.length}/${TEST_FILES.length}${colors.reset}`);
  console.log(`${colors.red}❌ Files with Violations: ${results.failed.length > 0 ? results.failed.map(f => f.file).filter((v, i, a) => a.indexOf(v) === i).length : 0}${colors.reset}`);
  console.log(`${colors.yellow}⚠️  Total Warnings: ${results.warnings.length}${colors.reset}`);
  
  // List violations by type
  if (results.failed.length > 0) {
    console.log(`\n${colors.red}${colors.bold}VIOLATIONS FOUND:${colors.reset}`);
    
    // Group by violation type
    const violationsByType = {};
    results.failed.forEach(failure => {
      if (!violationsByType[failure.rule]) {
        violationsByType[failure.rule] = [];
      }
      violationsByType[failure.rule].push(failure);
    });
    
    for (const [rule, violations] of Object.entries(violationsByType)) {
      console.log(`\n${colors.red}❌ ${rule}:${colors.reset}`);
      violations.forEach(v => {
        console.log(`   - ${path.basename(v.file)}: ${v.count} violation(s)`);
        if (v.examples && v.examples.length > 0) {
          console.log(`     Examples: ${v.examples.slice(0, 2).join(', ')}`);
        }
      });
    }
  }
  
  // Recommendations
  console.log(`\n${colors.cyan}${colors.bold}RECOMMENDATIONS:${colors.reset}`);
  
  if (results.failed.length > 0) {
    console.log('🔴 Critical: Remove all hardcoded values');
    console.log('🔴 Critical: Move all calculations to backend');
    console.log('🔴 Critical: Use backend data exclusively');
  }
  
  if (results.warnings.length > 0) {
    console.log('🟡 Warning: Increase use of formatters');
    console.log('🟡 Warning: Add more fallbacks for missing data');
  }
  
  if (results.failed.length === 0 && results.warnings.length === 0) {
    console.log('🎉 Excellent! All files comply with PROJECT_CODING_STANDARDS.md');
  }
  
  // Specific fixes needed
  if (results.failed.length > 0) {
    console.log(`\n${colors.bold}SPECIFIC FIXES NEEDED:${colors.reset}`);
    const uniqueMessages = [...new Set(results.failed.map(f => f.message))];
    uniqueMessages.forEach((msg, i) => {
      console.log(`${i + 1}. ${msg}`);
    });
  }
  
  console.log(`\n${colors.blue}${'='.repeat(60)}${colors.reset}`);
  console.log(`✨ Test completed at ${new Date().toLocaleTimeString()}`);
}

/**
 * Run all tests
 */
function runTests() {
  console.log(`${colors.bold}${colors.blue}${'='.repeat(60)}`);
  console.log('🔍 FRONTEND STANDARDS COMPLIANCE TEST');
  console.log(`Testing against PROJECT_CODING_STANDARDS.md`);
  console.log(`${'='.repeat(60)}${colors.reset}`);
  
  // Test each file
  for (const file of TEST_FILES) {
    const fullPath = path.join(process.cwd(), file);
    if (fs.existsSync(fullPath)) {
      testFile(fullPath);
    } else {
      console.log(`\n${colors.yellow}⚠ Skipping ${file} - file not found${colors.reset}`);
    }
  }
  
  // Print summary
  printSummary();
}

// Run the tests
runTests();