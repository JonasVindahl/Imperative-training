#!/usr/bin/env python3
"""
Script to reorganize questions from format-based and topic-based categories
into pure topic-based categories for better learning experience.
"""

import json
import os
from collections import defaultdict

# New category definitions
NEW_CATEGORIES = {
    'pointers_and_memory': {
        'name': 'Pointers & Memory Management',
        'keywords': ['pointer', 'malloc', 'free', 'calloc', 'realloc', 'memory', 'leak', 'dangling', 'null', 'dereference', '&', '*'],
        'old_categories': ['pointers', 'memory_management'],
        'tags': ['pointers', 'malloc', 'free', 'memory', 'memory_management', 'calloc', 'realloc']
    },
    'arrays_and_strings': {
        'name': 'Arrays & Strings',
        'keywords': ['array', 'string', 'str', 'char', 'null terminator', '\\0', 'strlen', 'strcpy', 'strcmp', 'buffer'],
        'old_categories': ['strings'],
        'tags': ['arrays', 'strings', 'null_terminator', 'string', 'array']
    },
    'structs_and_data_structures': {
        'name': 'Structs & Data Structures',
        'keywords': ['struct', 'typedef', 'node', 'linked list', 'node_t', 'data structure'],
        'old_categories': ['structs'],
        'tags': ['structs', 'typedef', 'linked_lists', 'data_structures', 'node']
    },
    'control_flow': {
        'name': 'Control Flow & Loops',
        'keywords': ['if', 'else', 'switch', 'case', 'for', 'while', 'do-while', 'loop', 'break', 'continue', 'goto'],
        'old_categories': ['control_flow'],
        'tags': ['control_flow', 'loops', 'if', 'switch', 'for', 'while', 'break', 'continue']
    },
    'functions_and_recursion': {
        'name': 'Functions & Recursion',
        'keywords': ['function', 'recursive', 'recursion', 'call', 'return', 'parameter', 'argument', 'stack frame', 'base case'],
        'old_categories': ['recursion', 'recursive_trace'],
        'tags': ['recursion', 'recursive', 'function', 'trace', 'fibonacci', 'factorial']
    },
    'file_io': {
        'name': 'File I/O',
        'keywords': ['file', 'fopen', 'fclose', 'fread', 'fwrite', 'fprintf', 'fscanf', 'FILE'],
        'old_categories': ['file_io'],
        'tags': ['file_io', 'file', 'fopen', 'fclose']
    },
    'fundamentals': {
        'name': 'C Fundamentals & Types',
        'keywords': ['int', 'float', 'double', 'char', 'void', 'sizeof', 'type', 'operator', 'division', 'modulo'],
        'old_categories': ['terminology', 'integer_division'],
        'tags': ['terminology', 'integer_division', 'types', 'operators', 'fundamentals']
    },
    'programming_challenges': {
        'name': 'Programming Challenges',
        'keywords': ['gcd', 'fibonacci', 'factorial', 'algorithm'],
        'old_categories': ['programming_tasks'],
        'tags': ['programming_task', 'algorithm', 'challenge']
    }
}

def categorize_question(question):
    """Determine which new category a question belongs to"""
    title = question.get('title', '').lower()
    description = question.get('description', '').lower()
    code = question.get('code_template', '').lower()
    tags = [t.lower() for t in question.get('tags', [])]
    old_category = question.get('category', '')

    # Check linked lists first (specific case)
    if 'linked_list' in tags or 'node_t' in code or 'struct node' in code:
        return 'structs_and_data_structures'

    # Score each new category
    scores = {}
    for new_cat, config in NEW_CATEGORIES.items():
        score = 0

        # Check if from old category
        if old_category in config['old_categories']:
            score += 10

        # Check tags
        for tag in tags:
            if tag in config['tags']:
                score += 5

        # Check keywords in title/description/code
        text = f"{title} {description} {code}"
        for keyword in config['keywords']:
            if keyword.lower() in text:
                score += 1

        scores[new_cat] = score

    # Return category with highest score
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)

    # Default fallback
    if old_category in ['fill_blanks', 'drag_drop']:
        return 'fundamentals'  # Format-based without clear topic
    return 'programming_challenges'

def main():
    questions_dir = 'questions'
    old_categories = [
        'memory_management', 'integer_division', 'strings', 'structs',
        'pointers', 'recursion', 'control_flow', 'file_io',
        'fill_blanks', 'drag_drop', 'recursive_trace',
        'programming_tasks', 'terminology'
    ]

    # Load all questions
    all_questions = defaultdict(list)

    for old_cat in old_categories:
        filepath = os.path.join(questions_dir, f'{old_cat}.json')
        if not os.path.exists(filepath):
            print(f"Warning: {filepath} not found")
            continue

        with open(filepath, 'r') as f:
            data = json.load(f)
            questions = data.get('questions', [])
            print(f"Loaded {len(questions)} questions from {old_cat}")

            for q in questions:
                # Determine new category
                new_cat = categorize_question(q)

                # Update question's category field
                q['category'] = new_cat

                # Add to new category
                all_questions[new_cat].append(q)

    # Print summary
    print("\n=== CATEGORIZATION SUMMARY ===")
    total = 0
    for new_cat in sorted(NEW_CATEGORIES.keys()):
        count = len(all_questions[new_cat])
        total += count
        print(f"{NEW_CATEGORIES[new_cat]['name']:40s}: {count:3d} questions")
    print(f"{'TOTAL':40s}: {total:3d} questions")

    # Write new category files
    print("\n=== WRITING NEW CATEGORY FILES ===")
    for new_cat, questions in all_questions.items():
        # Sort by ID
        questions.sort(key=lambda q: q.get('id', ''))

        # Renumber IDs to be consistent (optional)
        prefix = new_cat[:4]  # e.g., "poin", "arra", etc.
        for idx, q in enumerate(questions, 1):
            old_id = q.get('id', '')
            # Keep original ID for now to avoid breaking references
            # new_id = f"{prefix}_{idx:03d}"
            # q['id'] = new_id

        output_file = os.path.join(questions_dir, f'{new_cat}.json')
        with open(output_file, 'w') as f:
            json.dump({'questions': questions}, f, indent=2)
        print(f"Wrote {len(questions):3d} questions to {new_cat}.json")

    print("\n✓ Reorganization complete!")
    print(f"\nNext steps:")
    print("1. Backup old category files")
    print("2. Update question_loader.py")
    print("3. Update adaptive.py")
    print("4. Update start_practice.html")
    print("5. Test the application")

if __name__ == '__main__':
    main()
