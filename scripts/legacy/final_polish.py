#!/usr/bin/env python3
"""
Final polish for hints and explanations.
This script makes targeted improvements based on specific patterns.
"""

import json
from pathlib import Path
import re

QUESTIONS_DIR = Path("/Users/jonasvindahl/Documents/projects/7_imperative_exam/questions")

stats = {
    'total_questions': 0,
    'hints_polished': 0,
    'explanations_polished': 0,
    'files_processed': 0
}


def polish_hints_array(hints, question_data):
    """Polish hints array to be more progressive and educational."""
    if not hints or len(hints) < 2:
        return hints, False

    polished = hints.copy()
    changed = False

    # Ensure hints are progressive (general -> specific)
    # First hint should be conceptual
    if len(polished) >= 1:
        first = polished[0]
        # Should mention concept, not implementation
        if 'dereference' in first.lower() or '*' in first or '->' in first:
            # Too specific for first hint
            # Make it more conceptual
            if 'pointer' in first.lower():
                polished[0] = "Consider how pointers relate to memory addresses and values"
                changed = True

    # Middle hints should guide thinking
    if len(polished) >= 2:
        middle = polished[1]
        if not any(word in middle.lower() for word in ['think', 'consider', 'remember', 'note', 'recall']):
            polished[1] = "Think about " + middle[0].lower() + middle[1:]
            changed = True

    # Last hint should be most specific but not give answer
    if len(polished) >= 3:
        last = polished[-1]
        # Check if it gives away answer
        code_template = question_data.get('code_template', '')
        correct_answer = question_data.get('correct_answer', '')

        # If last hint contains exact answer code, it's too revealing
        if correct_answer and 'options' in question_data:
            options = question_data.get('options', [])
            try:
                answer_idx = ord(correct_answer.upper()) - ord('A')
                if 0 <= answer_idx < len(options):
                    answer_text = options[answer_idx]
                    if answer_text in last:
                        # Too revealing - make it more subtle
                        polished[-1] = "The solution involves " + last.lower()
                        changed = True
            except:
                pass

    return polished, changed


def enhance_explanation_with_context(explanation, question_data):
    """Add context-specific teaching to explanations."""
    if not explanation:
        return explanation, False

    enhanced = explanation
    changed = False

    category = question_data.get('category', '')
    tags = question_data.get('tags', [])
    difficulty = question_data.get('difficulty', '')

    # Add "Common mistake" section for appropriate questions
    error_tags = ['error', 'mistake', 'bug', 'undefined', 'segfault']
    if any(tag in tags for tag in error_tags):
        if 'common mistake' not in enhanced.lower() and 'avoid' not in enhanced.lower():
            # Could add common mistake warning
            if 'null' in enhanced.lower():
                if 'Always check' not in enhanced:
                    enhanced += " Always check pointers for NULL before dereferencing to prevent segmentation faults."
                    changed = True
            elif 'free' in enhanced.lower() or 'memory leak' in enhanced.lower():
                if 'Always' not in enhanced and 'Never' not in enhanced:
                    enhanced += " Always free dynamically allocated memory to prevent memory leaks."
                    changed = True

    # Add best practice for easy questions
    if difficulty == 'easy':
        best_practices = {
            'initialization': "Always initialize variables before using them to avoid undefined behavior.",
            'bounds': "Always check array bounds to prevent buffer overflows.",
            'return': "Functions should always return a value if they have a non-void return type.",
        }

        for key, practice in best_practices.items():
            if key in ' '.join(tags).lower() and practice not in enhanced:
                if len(enhanced) < 200:  # Don't make it too long
                    enhanced += " " + practice
                    changed = True
                    break

    # Ensure explanation references C standard behavior
    if 'standard' in tags or 'undefined' in tags:
        if 'C standard' not in enhanced and 'undefined behavior' not in enhanced:
            if 'undefined' in ' '.join(tags).lower():
                if len(enhanced) < 150:
                    enhanced += " This is undefined behavior according to the C standard."
                    changed = True

    # Add pointer arithmetic teaching
    if 'pointer_arithmetic' in tags:
        if 'size' not in enhanced.lower() and 'bytes' not in enhanced.lower():
            enhanced += " Pointer arithmetic moves by multiples of the type size, not individual bytes."
            changed = True

    # Add array decay teaching
    if 'arrays' in category or 'array' in tags:
        if 'decay' not in enhanced.lower() and 'sizeof' in enhanced.lower():
            if 'function' in enhanced.lower():
                enhanced += " Arrays decay to pointers when passed to functions, losing their size information."
                changed = True

    # Add string null terminator teaching
    if 'strings' in tags or 'string' in question_data.get('title', '').lower():
        if 'null' in enhanced.lower() and 'terminator' not in enhanced.lower():
            enhanced = enhanced.replace('null character', 'null terminator \\0')
            enhanced = enhanced.replace('\\0', "'\\0'")
            changed = True

    return enhanced, changed


def add_why_reasoning(explanation, question_data):
    """Ensure explanation explains WHY, not just WHAT."""
    if not explanation:
        return explanation, False

    improved = explanation
    changed = False

    # Check if explanation has "why" reasoning
    why_indicators = ['because', 'since', 'therefore', 'thus', 'this is why',
                      'as a result', 'consequently', 'this means']

    has_why = any(indicator in improved.lower() for indicator in why_indicators)

    if not has_why and len(improved) > 40 and len(improved) < 200:
        # Try to add "why" reasoning based on category
        category = question_data.get('category', '')

        # Add causal reasoning
        if 'pointers' in category:
            if '=' in improved and 'assign' in improved.lower():
                improved += " This is because the assignment operator copies the memory address, not the value."
                changed = True
        elif 'fundamentals' in category:
            if 'type' in improved.lower():
                if 'convert' in improved.lower() or 'cast' in improved.lower():
                    improved += " This is because C requires compatible types for operations."
                    changed = True

    return improved, changed


def process_question(question):
    """Process a single question."""
    changed = False

    # Polish hints array
    if 'hints' in question and question['hints']:
        polished, hints_changed = polish_hints_array(question['hints'], question)
        if hints_changed:
            question['hints'] = polished
            stats['hints_polished'] += 1
            changed = True

    # Enhance explanation with context
    if 'explanation' in question and question['explanation']:
        enhanced, exp_changed = enhance_explanation_with_context(
            question['explanation'], question)

        if exp_changed:
            question['explanation'] = enhanced
            changed = True

        # Add "why" reasoning
        enhanced, exp_changed2 = add_why_reasoning(enhanced, question)

        if exp_changed2:
            question['explanation'] = enhanced
            changed = True

        if exp_changed or exp_changed2:
            stats['explanations_polished'] += 1

    return changed


def process_file(filepath):
    """Process a single question file."""
    print(f"\n{'='*70}")
    print(f"Processing: {filepath.name}")
    print(f"{'='*70}")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    questions = data.get('questions', [])
    print(f"Total questions: {len(questions)}")

    file_changed = False
    for i, question in enumerate(questions, 1):
        stats['total_questions'] += 1

        if process_question(question):
            file_changed = True

        if i % 25 == 0:
            print(f"  Processed {i}/{len(questions)} questions...")

    # Save with proper formatting
    if file_changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved polishing improvements to {filepath.name}")
    else:
        print(f"  No additional polishing needed for {filepath.name}")

    stats['files_processed'] += 1


def main():
    print("C Programming Practice System - Final Polish")
    print("="*70)

    # Get all JSON files
    json_files = sorted([f for f in QUESTIONS_DIR.glob("*.json") if f.is_file()])

    # Process largest first
    file_sizes = [(f, f.stat().st_size) for f in json_files]
    file_sizes.sort(key=lambda x: x[1], reverse=True)

    for filepath, _ in file_sizes:
        process_file(filepath)

    # Print final statistics
    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"Files processed: {stats['files_processed']}")
    print(f"Total questions: {stats['total_questions']}")
    print(f"Hints polished: {stats['hints_polished']}")
    print(f"Explanations polished: {stats['explanations_polished']}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
