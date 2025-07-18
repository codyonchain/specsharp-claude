#!/usr/bin/env python3
"""Test script to verify SpecSharp setup"""

import sys
import subprocess
import os

def check_python():
    print("✓ Python version:", sys.version.split()[0])
    return True

def check_backend_deps():
    try:
        import fastapi
        import pydantic
        import sqlalchemy
        print("✓ Backend dependencies installed")
        return True
    except ImportError as e:
        print("✗ Missing backend dependency:", e)
        return False

def check_frontend():
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        print("✓ Node.js version:", result.stdout.strip())
        return True
    except:
        print("✗ Node.js not found")
        return False

def main():
    print("SpecSharp Setup Verification")
    print("=" * 40)
    
    checks = [
        check_python(),
        check_frontend()
    ]
    
    if all(checks):
        print("\n✅ All checks passed! You can now run:")
        print("   Backend: ./start-backend.sh")
        print("   Frontend: ./start-frontend.sh")
    else:
        print("\n❌ Some checks failed. Please install missing dependencies.")

if __name__ == "__main__":
    main()