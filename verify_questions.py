#!/usr/bin/env python3
"""Verify all question files are valid and can be loaded."""

import json
import os
from pathlib import Path

def verify_questions():
    questions_dir = Path("questions")
    total_questions = 0
    issues = []

    # Expected question files
    question_files = [
        'memory_management.json',
        'pointers.json',
        'strings.json',
        'structs.json',
        'integer_division.json',
        'recursion.json',
        'control_flow.json',
        'file_io.json',
        'fill_blanks.json',
        'drag_drop.json',
        'recursive_trace.json'
    ]

    print("=" * 60)
    print("QUESTION BANK VERIFICATION")
    print("=" * 60)

    for filename in question_files:
        filepath = questions_dir / filename

        if not filepath.exists():
            issues.append(f"❌ Missing file: {filename}")
            continue

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            if 'questions' not in data:
                issues.append(f"❌ {filename}: Missing 'questions' key")
                continue

            count = len(data['questions'])
            total_questions += count

            # Verify each question has required fields
            for i, q in enumerate(data['questions']):
                required_fields = ['id', 'type']
                missing = [f for f in required_fields if f not in q]
                if missing:
                    issues.append(f"⚠️  {filename} question {i}: Missing {missing}")

            print(f"✅ {filename:.<40} {count:>3} questions")

        except json.JSONDecodeError as e:
            issues.append(f"❌ {filename}: JSON parse error - {e}")
        except Exception as e:
            issues.append(f"❌ {filename}: Error - {e}")

    print("=" * 60)
    print(f"TOTAL: {total_questions} questions")
    print("=" * 60)

    if issues:
        print("\n⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("\n✅ All question files verified successfully!")
        return True

if __name__ == "__main__":
    success = verify_questions()
    exit(0 if success else 1)
