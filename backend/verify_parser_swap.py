#!/usr/bin/env python3
"""Verify the parser swap is complete"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_swap():
    print("=" * 60)
    print("VERIFYING PARSER SWAP")
    print("=" * 60)
    
    # Check if phrase_parser exists
    try:
        from app.v2.services.phrase_parser import phrase_parser
        print("✅ Phrase parser module exists")
    except ImportError as e:
        print(f"❌ Cannot import phrase parser: {e}")
        return False
    
    # Check current V2 API scope.py
    try:
        api_file = "/Users/codymarchant/specsharp/backend/app/v2/api/scope.py"
        with open(api_file, "r") as f:
            content = f.read()
            
        if "from app.v2.services.phrase_parser import phrase_parser" in content:
            print("✅ V2 API imports phrase_parser")
        else:
            print("❌ V2 API doesn't import phrase_parser")
            return False
            
        if "phrase_parser.parse" in content:
            print("✅ V2 API uses phrase_parser.parse()")
        else:
            print("❌ V2 API doesn't call phrase_parser.parse()")
            return False
            
    except Exception as e:
        print(f"❌ Cannot check API: {e}")
        return False
    
    # Test actual parsing
    test_cases = [
        ("Build a 75,000 SF elementary school", "educational", "elementary_school"),
        ("Build a 300,000 SF luxury apartment complex", "residential", "luxury_apartments"),
        ("Build a 50,000 SF medical office building", "healthcare", "medical_office"),
        ("Build a 95,000 SF class A office", "commercial", "class_a"),
    ]
    
    print("\nTesting parser functionality:")
    print("-" * 40)
    all_passed = True
    
    for test_desc, expected_type, expected_subtype in test_cases:
        result = phrase_parser.parse(test_desc)
        actual_type = result['building_type']
        actual_subtype = result['subtype']
        
        if actual_type == expected_type and actual_subtype == expected_subtype:
            print(f"✅ '{test_desc[:30]}...'")
            print(f"   → {actual_type}/{actual_subtype}")
        else:
            print(f"❌ '{test_desc[:30]}...'")
            print(f"   Expected: {expected_type}/{expected_subtype}")
            print(f"   Got: {actual_type}/{actual_subtype}")
            all_passed = False
    
    # Check if old NLP service is still being used
    print("\nChecking for old NLP service usage:")
    print("-" * 40)
    
    try:
        # Check if nlp_service.py exists
        nlp_file = "/Users/codymarchant/specsharp/backend/app/v2/services/nlp_service.py"
        if os.path.exists(nlp_file):
            with open(nlp_file, "r") as f:
                nlp_content = f.read()
            
            # Check if it's the compatibility shim or the old complex parser
            if "Compatibility shim" in nlp_content or "phrase_parser" in nlp_content:
                print("✅ nlp_service.py is compatibility shim (redirects to phrase_parser)")
            elif len(nlp_content) > 1000:  # Old parser is much larger
                print("⚠️  Old complex NLP parser still exists")
                print("   Consider archiving it as nlp_service.py.old")
        else:
            print("✅ No nlp_service.py found (old parser removed)")
    except Exception as e:
        print(f"   Cannot check: {e}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ PARSER SWAP VERIFIED SUCCESSFULLY!")
        print("\nThe system is now using:")
        print("• Phrase-first parser (phrase_parser)")
        print("• Standardized taxonomy")
        print("• Simple, predictable matching")
    else:
        print("⚠️ Some issues found - review above")
    
    return all_passed

if __name__ == "__main__":
    success = verify_swap()
    sys.exit(0 if success else 1)