#!/usr/bin/env python3
"""Comprehensive project audit script."""

import json
import os
from pathlib import Path

def audit_project():
    print("=" * 70)
    print("PROJECT AUDIT")
    print("=" * 70)

    issues = []
    warnings = []

    # 1. Check Python files
    print("\n📝 Checking Python Files...")
    python_files = [
        'app.py', 'config.py',
        'models/__init__.py',
        'routes/auth.py', 'routes/practice.py', 'routes/progress.py',
        'services/adaptive.py', 'services/compiler.py',
        'services/grader.py', 'services/question_loader.py'
    ]

    for pyfile in python_files:
        if not os.path.exists(pyfile):
            issues.append(f"Missing Python file: {pyfile}")
        else:
            # Check file size
            size = os.path.getsize(pyfile)
            if size == 0:
                issues.append(f"Empty file: {pyfile}")
            elif size < 100:
                warnings.append(f"Very small file: {pyfile} ({size} bytes)")

    # 2. Check question files
    print("📊 Checking Question Files...")
    question_files = list(Path('questions').glob('*.json'))
    total_questions = 0

    for qfile in question_files:
        try:
            with open(qfile) as f:
                data = json.load(f)

            if 'questions' not in data:
                issues.append(f"{qfile.name}: Missing 'questions' key")
                continue

            qs = data['questions']
            if not isinstance(qs, list):
                issues.append(f"{qfile.name}: 'questions' is not a list")
                continue

            # Check each question
            for i, q in enumerate(qs):
                if not isinstance(q, dict):
                    issues.append(f"{qfile.name} question {i}: Not a dict")
                    continue

                # Check required fields
                required = ['id', 'type', 'category']
                for field in required:
                    if field not in q:
                        issues.append(f"{qfile.name} question {i} ({q.get('id', 'NO_ID')}): Missing '{field}'")

            total_questions += len(qs)
            print(f"  ✅ {qfile.name}: {len(qs)} questions")

        except json.JSONDecodeError as e:
            issues.append(f"{qfile.name}: JSON error - {e}")
        except Exception as e:
            issues.append(f"{qfile.name}: Error - {e}")

    print(f"\n  Total: {total_questions} questions")

    # 3. Check templates
    print("\n🎨 Checking Templates...")
    templates = [
        'templates/base.html',
        'templates/login.html',
        'templates/register.html',
        'templates/dashboard.html',
        'templates/practice.html',
        'templates/start_practice.html',
        'templates/session_complete.html',
        'templates/404.html',
        'templates/500.html'
    ]

    for tpl in templates:
        if not os.path.exists(tpl):
            issues.append(f"Missing template: {tpl}")
        else:
            print(f"  ✅ {os.path.basename(tpl)}")

    # 4. Check static files
    print("\n🎨 Checking Static Files...")
    static_dirs = ['static/css', 'static/js', 'static/images']
    for sdir in static_dirs:
        if os.path.exists(sdir):
            files = os.listdir(sdir)
            print(f"  ✅ {sdir}: {len(files)} files")
        else:
            warnings.append(f"Missing static directory: {sdir}")

    # 5. Check documentation
    print("\n📚 Checking Documentation...")
    docs = [
        'README.md',
        'README_TRUENAS.md',
        'TRUENAS_DEPLOY.md',
        'Dockerfile',
        'requirements.txt'
    ]

    for doc in docs:
        if os.path.exists(doc):
            print(f"  ✅ {doc}")
        else:
            warnings.append(f"Missing documentation: {doc}")

    # 6. Check deployment files
    print("\n🚀 Checking Deployment Files...")
    deploy_files = [
        'deployment/docker-compose.yml',
        'deployment/truenas-scale-app.yaml',
        'build-for-truenas.sh'
    ]

    for df in deploy_files:
        if os.path.exists(df):
            print(f"  ✅ {df}")
        else:
            issues.append(f"Missing deployment file: {df}")

    # 7. Check for common issues
    print("\n🔍 Checking for Common Issues...")

    # Check if __pycache__ exists (shouldn't be committed)
    if os.path.exists('__pycache__'):
        warnings.append("__pycache__ directory exists (should be in .gitignore)")

    # Check if .env exists (shouldn't be committed with secrets)
    if os.path.exists('.env'):
        warnings.append(".env file exists (verify no secrets are committed)")

    # Check if instance/ has database
    if os.path.exists('instance/practice.db'):
        warnings.append("Database file exists (should be excluded from git)")

    print("  ✅ Common issue check complete")

    # Summary
    print("\n" + "=" * 70)
    print("AUDIT SUMMARY")
    print("=" * 70)

    if issues:
        print(f"\n❌ ISSUES FOUND ({len(issues)}):")
        for issue in issues:
            print(f"  • {issue}")
    else:
        print("\n✅ No critical issues found!")

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  • {warning}")
    else:
        print("\n✅ No warnings!")

    print(f"\n📊 Total Questions: {total_questions}")
    print("=" * 70)

    return len(issues) == 0

if __name__ == '__main__':
    success = audit_project()
    exit(0 if success else 1)
