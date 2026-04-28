#!/usr/bin/env python3
"""
Script to improve hints and explanations for C Programming Practice System questions.
"""

import json
import os
from pathlib import Path

# Question files directory
QUESTIONS_DIR = Path("/Users/jonasvindahl/Documents/projects/7_imperative_exam/questions")

# Statistics
stats = {
    'total_questions': 0,
    'hints_improved': 0,
    'explanations_improved': 0,
    'files_processed': 0
}

def improve_hint(question_data, hint_text):
    """
    Analyze and potentially improve a hint.
    Returns (improved_hint, was_improved)
    """
    # Check if hint gives away the answer
    if not hint_text:
        return hint_text, False

    # Basic improvement: ensure hints guide without revealing
    # This is a placeholder - actual improvement logic would be more sophisticated

    return hint_text, False  # For now, keep original

def improve_explanation(question_data, explanation_text):
    """
    Analyze and potentially improve an explanation.
    Returns (improved_explanation, was_improved)
    """
    if not explanation_text:
        return explanation_text, False

    # Placeholder - actual improvement would analyze and rewrite

    return explanation_text, False  # For now, keep original

def process_question(question):
    """Process a single question and improve its hint and explanation."""
    improved = False

    # Improve single hint field
    if 'hint' in question and question['hint']:
        new_hint, was_improved = improve_hint(question, question['hint'])
        if was_improved:
            question['hint'] = new_hint
            stats['hints_improved'] += 1
            improved = True

    # Improve hints array
    if 'hints' in question and question['hints']:
        for i, hint in enumerate(question['hints']):
            new_hint, was_improved = improve_hint(question, hint)
            if was_improved:
                question['hints'][i] = new_hint
                stats['hints_improved'] += 1
                improved = True

    # Improve explanation
    if 'explanation' in question and question['explanation']:
        new_explanation, was_improved = improve_explanation(question, question['explanation'])
        if was_improved:
            question['explanation'] = new_explanation
            stats['explanations_improved'] += 1
            improved = True

    return improved

def process_file(filepath):
    """Process a single question file."""
    print(f"\nProcessing {filepath.name}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    questions = data.get('questions', [])
    print(f"  Found {len(questions)} questions")

    file_improved = False
    for question in questions:
        stats['total_questions'] += 1
        if process_question(question):
            file_improved = True

    # Save the file with proper formatting
    if file_improved:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Saved improvements to {filepath.name}")

    stats['files_processed'] += 1

def main():
    """Main function to process all question files."""
    print("C Programming Practice System - Hint and Explanation Improver")
    print("=" * 70)

    # Get all JSON files
    json_files = sorted(QUESTIONS_DIR.glob("*.json"))

    # Process largest files first
    file_sizes = [(f, f.stat().st_size) for f in json_files]
    file_sizes.sort(key=lambda x: x[1], reverse=True)

    for filepath, size in file_sizes:
        process_file(filepath)

    # Print statistics
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Files processed: {stats['files_processed']}")
    print(f"Total questions: {stats['total_questions']}")
    print(f"Hints improved: {stats['hints_improved']}")
    print(f"Explanations improved: {stats['explanations_improved']}")
    print("=" * 70)

if __name__ == "__main__":
    main()
