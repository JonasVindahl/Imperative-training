#!/usr/bin/env python3
"""
Fix duplicate question IDs across categories.
Strategy: Keep first occurrence, rename duplicates with category prefix.
"""

import json
import os
from collections import defaultdict

def main():
    questions_dir = 'questions'
    categories = [
        'pointers_and_memory',
        'arrays_and_strings',
        'structs_and_data_structures',
        'control_flow',
        'functions_and_recursion',
        'file_io',
        'fundamentals',
        'programming_challenges'
    ]

    # Category prefix mapping for clear naming
    cat_prefix = {
        'pointers_and_memory': 'pnm',
        'arrays_and_strings': 'ars',
        'structs_and_data_structures': 'sds',
        'control_flow': 'cfl',
        'functions_and_recursion': 'fnr',
        'file_io': 'fio',
        'fundamentals': 'fun',
        'programming_challenges': 'pch'
    }

    # Track which IDs we've seen
    id_registry = {}  # id -> (category, index_in_category)
    duplicates_found = 0
    duplicates_fixed = 0

    # First pass: identify all IDs and find duplicates
    all_data = {}
    for cat in categories:
        filepath = os.path.join(questions_dir, f'{cat}.json')
        with open(filepath, 'r') as f:
            data = json.load(f)
            all_data[cat] = data

            for idx, q in enumerate(data['questions']):
                qid = q.get('id')
                if qid in id_registry:
                    duplicates_found += 1
                    print(f"DUPLICATE: {qid} found in {cat} (already in {id_registry[qid][0]})")
                else:
                    id_registry[qid] = (cat, idx)

    print(f"\nFound {duplicates_found} duplicate IDs")
    print("=" * 60)

    # Second pass: fix duplicates
    id_counters = defaultdict(int)  # Track highest number for each prefix

    for cat in categories:
        data = all_data[cat]
        modified = False

        for idx, q in enumerate(data['questions']):
            qid = q.get('id')
            original_owner = id_registry[qid]

            # If this is NOT the original owner of this ID, it's a duplicate
            if original_owner != (cat, idx):
                # Generate new unique ID
                old_id = qid

                # Extract the base prefix and number
                parts = qid.split('_')
                if len(parts) >= 2:
                    prefix = parts[0]
                    try:
                        num = int(parts[1])
                    except:
                        num = 0
                else:
                    prefix = cat_prefix[cat]
                    num = 0

                # Generate new ID with category prefix
                new_prefix = f"{cat_prefix[cat]}_{prefix}"

                # Find unique number
                counter_key = new_prefix
                if counter_key not in id_counters:
                    id_counters[counter_key] = num

                new_num = id_counters[counter_key] + 1
                new_id = f"{new_prefix}_{new_num:03d}"

                # Make sure it's truly unique
                while new_id in id_registry:
                    new_num += 1
                    new_id = f"{new_prefix}_{new_num:03d}"

                id_counters[counter_key] = new_num

                # Update the question
                q['id'] = new_id
                id_registry[new_id] = (cat, idx)
                modified = True
                duplicates_fixed += 1

                print(f"FIXED: {old_id} -> {new_id} (in {cat})")

        # Save if modified
        if modified:
            filepath = os.path.join(questions_dir, f'{cat}.json')
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✓ Updated {cat}.json")

    print("=" * 60)
    print(f"\n✓ Fixed {duplicates_fixed} duplicate IDs")
    print(f"✓ All {len(id_registry)} question IDs are now unique")

if __name__ == '__main__':
    main()
