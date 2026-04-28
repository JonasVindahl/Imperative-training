#!/usr/bin/env python3
"""
Batch process to improve hints and explanations for C programming questions.
This script processes questions systematically with improvements.
"""

import json
from pathlib import Path

QUESTIONS_DIR = Path("/Users/jonasvindahl/Documents/projects/7_imperative_exam/questions")

def improve_hint_for_question(question):
    """
    Improve hints based on question content and correct answer.
    Returns tuple: (improved_hint, improved_hints_array, changed)
    """
    q_id = question.get('id', '')
    category = question.get('category', '')
    current_hint = question.get('hint', '')
    current_hints = question.get('hints', [])
    explanation = question.get('explanation', '')

    # We'll build improvements based on patterns
    new_hint = current_hint
    new_hints = current_hints.copy()
    changed = False

    # Check if hint gives away the answer (contains exact answer text)
    correct_answer = question.get('correct_answer', '')
    options = question.get('options', [])

    if correct_answer and options:
        try:
            answer_index = ord(correct_answer.upper()) - ord('A')
            if 0 <= answer_index < len(options):
                answer_text = options[answer_index]

                # If hint contains the exact answer, it's too revealing
                if answer_text.lower() in current_hint.lower():
                    # This needs improvement
                    changed = True
        except:
            pass

    # Improve based on category patterns
    if 'integer_division' in question.get('tags', []):
        if 'truncates' not in current_hint.lower():
            new_hint = "Remember that integer division in C truncates toward zero, discarding the decimal portion entirely."
            changed = True

    if 'pointer' in category or 'pointers' in question.get('tags', []):
        if current_hint and 'pointer' not in current_hint.lower():
            # Hints should mention pointers explicitly
            if 'dereference' in explanation.lower() and 'dereference' not in current_hint.lower():
                new_hint = "Consider how dereferencing a pointer with the * operator accesses the value at the memory address."
                changed = True

    # Improve hints array to be more progressive
    if len(current_hints) >= 2:
        # First hint should be most general
        if current_hints[0] and len(current_hints[0]) > len(current_hints[-1]):
            # Hints might be in wrong order
            new_hints = sorted(current_hints, key=len)
            changed = True

    return new_hint, new_hints, changed


def improve_explanation_for_question(question):
    """
    Improve explanation to be more educational.
    Returns tuple: (improved_explanation, changed)
    """
    current_exp = question.get('explanation', '')

    if not current_exp:
        return current_exp, False

    # Check if explanation just states the answer without teaching
    if len(current_exp) < 50:
        # Very short explanations likely just state the answer
        # These need expansion
        pass

    # Check if explanation uses educational language
    educational_words = ['because', 'therefore', 'this means', 'remember',
                         'always', 'never', 'rule', 'important']

    has_educational = any(word in current_exp.lower() for word in educational_words)

    # Check if explanation mentions common mistakes
    mentions_mistakes = any(word in current_exp.lower()
                           for word in ['common', 'mistake', 'error', 'wrong',
                                       'incorrect', 'avoid', 'careful'])

    # For now, keep original - manual review needed
    return current_exp, False


def process_file(filepath, dry_run=True):
    """Process a single question file."""
    print(f"\n{'='*70}")
    print(f"Processing: {filepath.name}")
    print(f"{'='*70}")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    questions = data.get('questions', [])
    print(f"Total questions: {len(questions)}")

    hints_improved = 0
    explanations_improved = 0

    for i, question in enumerate(questions):
        q_changed = False

        # Improve hints
        new_hint, new_hints, hint_changed = improve_hint_for_question(question)
        if hint_changed:
            if new_hint != question.get('hint', ''):
                question['hint'] = new_hint
                hints_improved += 1
                q_changed = True
                print(f"  Q{i+1} ({question['id']}): Improved hint")

            if new_hints != question.get('hints', []):
                question['hints'] = new_hints
                hints_improved += 1
                q_changed = True
                print(f"  Q{i+1} ({question['id']}): Improved hints array")

        # Improve explanation
        new_exp, exp_changed = improve_explanation_for_question(question)
        if exp_changed:
            question['explanation'] = new_exp
            explanations_improved += 1
            q_changed = True
            print(f"  Q{i+1} ({question['id']}): Improved explanation")

    print(f"\nSummary for {filepath.name}:")
    print(f"  Hints improved: {hints_improved}")
    print(f"  Explanations improved: {explanations_improved}")

    # Save if not dry run
    if not dry_run and (hints_improved > 0 or explanations_improved > 0):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Saved changes to {filepath.name}")

    return hints_improved, explanations_improved


def main():
    print("C Programming Practice System - Hint & Explanation Improver")
    print("="*70)

    # Get all JSON files
    json_files = sorted([f for f in QUESTIONS_DIR.glob("*.json") if f.is_file()])

    total_hints = 0
    total_explanations = 0

    # Process each file
    for filepath in json_files:
        h, e = process_file(filepath, dry_run=False)
        total_hints += h
        total_explanations += e

    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"Total hints improved: {total_hints}")
    print(f"Total explanations improved: {total_explanations}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
