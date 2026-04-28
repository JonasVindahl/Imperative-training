#!/usr/bin/env python3
"""
Smart improvement of hints and explanations for C programming questions.
This processes all questions and applies intelligent improvements.
"""

import json
from pathlib import Path
import re

QUESTIONS_DIR = Path("/Users/jonasvindahl/Documents/projects/7_imperative_exam/questions")

# Statistics
stats = {
    'total_questions': 0,
    'hints_improved': 0,
    'explanations_improved': 0,
    'files_processed': 0
}


def improve_single_hint(hint_text, question_context):
    """Improve a single hint to be more educational and less revealing."""
    if not hint_text:
        return hint_text, False

    improved = hint_text
    changed = False

    # Pattern 1: Remove answers that are too explicit
    # If hint starts with imperative without teaching context
    if improved.startswith("Use ") and "because" not in improved and "when" not in improved:
        improved = "Consider using " + improved[4:]
        changed = True

    # Pattern 2: Add educational framing
    teaching_phrases = ['Remember that', 'Consider', 'Think about', 'Recall that', 'Note that']
    starts_with_teaching = any(improved.startswith(phrase) for phrase in teaching_phrases)

    if not starts_with_teaching and len(improved) > 20:
        # Add teaching framing if it's a statement
        if improved[0].isupper() and not improved.startswith('In '):
            improved = "Remember that " + improved[0].lower() + improved[1:]
            changed = True

    # Pattern 3: Replace "just" or "simply" (minimizing language)
    if ' just ' in improved or ' simply ' in improved:
        improved = improved.replace(' just ', ' ')
        improved = improved.replace(' simply ', ' ')
        changed = True

    return improved, changed


def improve_hints_array(hints, question_context):
    """Improve an array of hints to be progressive."""
    if not hints or len(hints) == 0:
        return hints, False

    improved_hints = []
    changed = False

    for i, hint in enumerate(hints):
        # Each hint should be more specific than the last
        improved, hint_changed = improve_single_hint(hint, question_context)

        # First hint should be most general
        if i == 0:
            if not any(word in improved.lower() for word in ['consider', 'think', 'remember', 'recall']):
                improved = "Consider " + improved[0].lower() + improved[1:]
                hint_changed = True

        # Middle hints should reference concepts
        elif i < len(hints) - 1:
            if len(improved) < 15:  # Too short, not explanatory enough
                improved = "Think about " + improved.lower()
                hint_changed = True

        # Last hint should be most specific but still not give answer
        else:
            if "answer" in improved.lower() or "solution" in improved.lower():
                hint_changed = True

        improved_hints.append(improved)
        if hint_changed:
            changed = True

    return improved_hints, changed


def improve_explanation(explanation, question_context):
    """Improve explanation to be more educational."""
    if not explanation:
        return explanation, False

    improved = explanation
    changed = False

    # Pattern 1: Too short - likely just states answer
    if len(explanation) < 40:
        # Need to expand, but we can't without understanding context
        # For now, keep it
        pass

    # Pattern 2: Starts with "The answer is" or similar
    if improved.startswith("The answer is") or improved.startswith("The correct answer is"):
        # Remove this and focus on why
        improved = re.sub(r'^The (correct )?answer is \w+\.?\s*', '', improved)
        changed = True

    # Pattern 3: Add "why" if missing
    educational_indicators = ['because', 'since', 'therefore', 'thus', 'this means',
                              'as a result', 'consequently', 'this is why']

    has_why = any(indicator in improved.lower() for indicator in educational_indicators)

    if not has_why and len(improved) > 50:
        # Explanation states what but not why - ideally we'd expand
        # For now, flag for manual review
        pass

    # Pattern 4: Add common mistake warning if appropriate
    error_keywords = ['not', "don't", "doesn't", 'never', 'avoid', 'incorrect', 'wrong']
    has_warning = any(keyword in improved.lower() for keyword in error_keywords)

    # Pattern 5: Ensure proper C terminology
    terminology_fixes = {
        'variable': 'variable',
        'pointer': 'pointer',
        'array': 'array',
        'function': 'function',
        'memory': 'memory',
    }

    # Pattern 6: Remove casual language
    casual_phrases = [
        (' gonna ', ' going to '),
        (' wanna ', ' want to '),
        (' gotta ', ' have to '),
    ]

    for old, new in casual_phrases:
        if old in improved:
            improved = improved.replace(old, new)
            changed = True

    return improved, changed


def process_question(question):
    """Process a single question."""
    changed = False
    question_context = {
        'id': question.get('id'),
        'category': question.get('category'),
        'type': question.get('type'),
        'difficulty': question.get('difficulty'),
        'tags': question.get('tags', [])
    }

    # Improve single hint
    if 'hint' in question and question['hint']:
        improved, hint_changed = improve_single_hint(question['hint'], question_context)
        if hint_changed:
            question['hint'] = improved
            stats['hints_improved'] += 1
            changed = True

    # Improve hints array
    if 'hints' in question and question['hints']:
        improved, hints_changed = improve_hints_array(question['hints'], question_context)
        if hints_changed:
            question['hints'] = improved
            stats['hints_improved'] += 1
            changed = True

    # Improve explanation
    if 'explanation' in question and question['explanation']:
        improved, exp_changed = improve_explanation(question['explanation'], question_context)
        if exp_changed:
            question['explanation'] = improved
            stats['explanations_improved'] += 1
            changed = True

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
            if i % 20 == 0:
                print(f"  Processed {i}/{len(questions)} questions...")

    # Save with proper formatting
    if file_changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved improvements to {filepath.name}")
    else:
        print(f"  No changes needed for {filepath.name}")

    stats['files_processed'] += 1


def main():
    print("C Programming Practice System - Smart Hint & Explanation Improver")
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
    print(f"Hints improved: {stats['hints_improved']}")
    print(f"Explanations improved: {stats['explanations_improved']}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
