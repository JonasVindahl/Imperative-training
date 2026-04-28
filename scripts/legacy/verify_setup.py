#!/usr/bin/env python3
"""
Verification script for C Programming Practice System
Checks that all components are properly configured
"""

import os
import sys
import json
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor} (need 3.10+)")
        return False


def check_gcc():
    """Check if GCC is available"""
    print("\nChecking GCC compiler...")
    result = os.system("gcc --version > /dev/null 2>&1")
    if result == 0:
        print("  ✓ GCC compiler found")
        return True
    else:
        print("  ✗ GCC compiler not found")
        print("    Install with: xcode-select --install (macOS)")
        return False


def check_dependencies():
    """Check if Python dependencies are installed"""
    print("\nChecking Python dependencies...")
    required = ['flask', 'flask_sqlalchemy', 'flask_login', 'werkzeug', 'dotenv']
    missing = []

    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package}")
            missing.append(package)

    if missing:
        print("\n  Install missing packages:")
        print("  pip install -r requirements.txt")
        return False
    return True


def check_project_structure():
    """Check if all required directories and files exist"""
    print("\nChecking project structure...")

    required_dirs = [
        'models', 'routes', 'services', 'static', 'templates', 'questions', 'tests'
    ]
    required_files = [
        'app.py', 'config.py', 'requirements.txt', '.env', 'README.md'
    ]

    all_good = True

    for dir_name in required_dirs:
        if os.path.isdir(dir_name):
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ (missing)")
            all_good = False

    for file_name in required_files:
        if os.path.isfile(file_name):
            print(f"  ✓ {file_name}")
        else:
            print(f"  ✗ {file_name} (missing)")
            all_good = False

    return all_good


def check_questions():
    """Check question bank files"""
    print("\nChecking question bank...")

    categories = [
        'memory_management', 'integer_division', 'strings',
        'structs', 'pointers', 'recursion', 'control_flow'
    ]

    total_questions = 0
    all_good = True

    for category in categories:
        file_path = f'questions/{category}.json'
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    count = len(data.get('questions', []))
                    total_questions += count
                    print(f"  ✓ {category}: {count} questions")
            except json.JSONDecodeError:
                print(f"  ✗ {category}: Invalid JSON")
                all_good = False
        else:
            print(f"  ✗ {category}: File missing")
            all_good = False

    print(f"\n  Total: {total_questions} questions")
    return all_good


def check_env_file():
    """Check .env configuration"""
    print("\nChecking .env configuration...")

    if not os.path.isfile('.env'):
        print("  ✗ .env file missing")
        return False

    required_vars = ['FLASK_SECRET_KEY', 'DATABASE_URL', 'MAX_CODE_EXECUTION_TIME']
    all_good = True

    with open('.env', 'r') as f:
        content = f.read()
        for var in required_vars:
            if var in content:
                print(f"  ✓ {var} set")
            else:
                print(f"  ✗ {var} missing")
                all_good = False

    return all_good


def main():
    """Run all checks"""
    print("=" * 60)
    print("C Programming Practice System - Setup Verification")
    print("=" * 60)

    checks = [
        check_python_version(),
        check_gcc(),
        check_dependencies(),
        check_project_structure(),
        check_questions(),
        check_env_file()
    ]

    print("\n" + "=" * 60)
    if all(checks):
        print("✓ All checks passed! You're ready to run the application.")
        print("\nTo start the application:")
        print("  1. Activate virtual environment: source venv/bin/activate")
        print("  2. Run the app: python app.py")
        print("  3. Visit: http://localhost:5000")
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        sys.exit(1)
    print("=" * 60)


if __name__ == '__main__':
    main()
