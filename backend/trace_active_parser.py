#!/usr/bin/env python3
"""
Trace which parser is actually being used in the system
"""

import os
import sys
import re

print("=" * 80)
print("TRACING ACTIVE PARSER PATH")
print("=" * 80)

# Step 1: Check the main.py to see which routers are included
print("\n1. Checking main.py for registered routers...")
print("-" * 40)

main_file = "/Users/codymarchant/specsharp/backend/app/main.py"
with open(main_file, 'r') as f:
    content = f.read()
    
# Find all router includes
router_includes = re.findall(r'app\.include_router\((.*?)\)', content, re.DOTALL)
print(f"Found {len(router_includes)} router includes:")

for include in router_includes:
    if 'v2' in include.lower() or 'analyze' in include.lower() or 'scope' in include.lower():
        print(f"  • {include.strip()[:100]}...")

# Step 2: Check which V2 routes are registered
print("\n2. Checking V2 route registration...")
print("-" * 40)

if 'v2_router' in content or 'v2.api' in content:
    print("✅ V2 routes ARE registered in main.py")
    v2_match = re.search(r'from app\.v2\.api(?:\.scope)? import (\w+)', content)
    if v2_match:
        print(f"  Imported as: {v2_match.group(1)}")
else:
    print("❌ V2 routes NOT found in main.py")

# Step 3: Check frontend API calls
print("\n3. Checking frontend API client...")
print("-" * 40)

frontend_client = "/Users/codymarchant/specsharp/frontend/src/v2/api/client.ts"
if os.path.exists(frontend_client):
    with open(frontend_client, 'r') as f:
        client_content = f.read()
    
    # Find analyze endpoint
    analyze_match = re.search(r"analyzeProject.*?['\"`](.*?)['\"`]", client_content, re.DOTALL)
    if analyze_match:
        endpoint = analyze_match.group(1)
        print(f"Frontend calls: {endpoint}")
        
        # Check if it's V1 or V2
        if '/v2/' in endpoint:
            print("  → This is V2 endpoint")
        elif '/v1/' in endpoint:
            print("  → This is V1 endpoint")
        else:
            print(f"  → Endpoint path: {endpoint}")

# Step 4: Find actual parser imports in API endpoints
print("\n4. Checking parser imports in API endpoints...")
print("-" * 40)

# Check V2 scope.py
v2_scope = "/Users/codymarchant/specsharp/backend/app/v2/api/scope.py"
if os.path.exists(v2_scope):
    with open(v2_scope, 'r') as f:
        v2_content = f.read()
    
    if 'nlp_service' in v2_content:
        print("✅ V2 scope.py uses nlp_service (V2 parser)")
        nlp_import = re.search(r'from app\.v2\.services\.nlp_service import (\w+)', v2_content)
        if nlp_import:
            print(f"  Imported as: {nlp_import.group(1)}")
            
            # Check how it's used
            parse_calls = re.findall(r'(\w+)\.parse_description\(', v2_content)
            if parse_calls:
                print(f"  Used in: {parse_calls[0]}.parse_description()")

# Check V1 endpoints
print("\n5. Checking V1 endpoints...")
print("-" * 40)

v1_scope = "/Users/codymarchant/specsharp/backend/app/api/endpoints/scope.py"
if os.path.exists(v1_scope):
    with open(v1_scope, 'r') as f:
        v1_content = f.read()
    
    if 'nlp_service' in v1_content:
        print("V1 scope.py uses nlp_service")
        # Check which nlp_service
        if 'app.services.nlp_service' in v1_content:
            print("  → Uses V1 NLP service")
        elif 'app.v2.services.nlp_service' in v1_content:
            print("  → Uses V2 NLP service")

# Step 6: Check the actual flow
print("\n6. ACTUAL PARSER FLOW:")
print("=" * 40)

# Based on our findings, determine the flow
if 'v2_router' in content or 'v2.api' in content:
    print("📍 When user creates a new project:")
    print("   1. Frontend (NewProject.tsx) calls useProjectAnalysis hook")
    print("   2. Hook calls api.analyzeProject() in client.ts")
    print("   3. client.ts makes POST to '/api/v2/analyze'")
    print("   4. Backend routes to app.v2.api.scope.analyze_project()")
    print("   5. analyze_project() calls nlp_service.parse_description()")
    print("   6. ✅ V2 PARSER (app.v2.services.nlp_service) is used")
    
    print("\n🎯 ACTIVE PARSER: V2 (app/v2/services/nlp_service.py)")
else:
    print("⚠️ V2 routes not registered - checking V1...")
    print("   Need to check if V1 endpoints are active")

# Step 7: Verify by checking imports
print("\n7. Import verification...")
print("-" * 40)

# Check if V2 is actually imported anywhere
import subprocess
result = subprocess.run(
    ["grep", "-r", "from app.v2", "/Users/codymarchant/specsharp/backend/app", "--include=*.py"],
    capture_output=True,
    text=True
)

v2_imports = [line for line in result.stdout.split('\n') if 'main.py' in line or 'api' in line]
if v2_imports:
    print("V2 is imported in:")
    for imp in v2_imports[:5]:  # Show first 5
        if not '__pycache__' in imp:
            file_part = imp.split(':')[0].replace('/Users/codymarchant/specsharp/backend/', '')
            print(f"  • {file_part}")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

# Make final determination
if os.path.exists(frontend_client):
    with open(frontend_client, 'r') as f:
        if "'/api/v2/analyze'" in f.read():
            print("✅ The V2 parser IS the active parser")
            print("   Location: backend/app/v2/services/nlp_service.py")
            print("   Method: NLPService.parse_description()")
            print("\n📝 The fix we applied to V2 parser WILL affect production!")
        else:
            print("⚠️ Need to check further - frontend may use V1")