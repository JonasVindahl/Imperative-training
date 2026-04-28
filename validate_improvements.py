#!/usr/bin/env python3
"""
Validate and count the improvements made to hints and explanations.
"""

import json
from pathlib import Path

QUESTIONS_DIR = Path("/Users/jonasvindahl/Documents/projects/7_imperative_exam/questions")

def analyze_hint(hint):
    """Analyze hint quality."""
    if not hint:
        return {}

    metrics = {
        'has_educational_framing': any(word in hint for word in ['Remember', 'Consider', 'Think', 'Recall', 'Note']),
        'length': len(hint),
        'has_teaching_verb': any(word in hint.lower() for word in ['remember', 'consider', 'think', 'recall']),
    }
    return metrics


def analyze_explanation(explanation):
    """Analyze explanation quality."""
    if not explanation:
        return {}

    metrics = {
        'length': len(explanation),
        'has_why': any(word in explanation.lower() for word in ['because', 'since', 'therefore', 'thus', 'this means', 'as a result']),
        'has_teaching': any(word in explanation for word in ['store', 'allocate', 'dereference', 'call', 'return', 'cast', 'convert', 'truncate']),
        'has_best_practice': any(word in explanation for word in ['Always', 'Never', 'avoid', 'prevent', 'check']),
        'sentence_count': explanation.count('. ') + 1,
    }
    return metrics


def analyze_file(filepath):
    """Analyze a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    questions = data.get('questions', [])

    file_stats = {
        'total_questions': len(questions),
        'has_hint': 0,
        'has_hints_array': 0,
        'has_explanation': 0,
        'hints_with_framing': 0,
        'explanations_with_why': 0,
        'explanations_with_best_practice': 0,
        'avg_explanation_length': 0,
        'hints_array_progressive': 0,
    }

    explanation_lengths = []

    for question in questions:
        # Analyze single hint
        if 'hint' in question and question['hint']:
            file_stats['has_hint'] += 1
            metrics = analyze_hint(question['hint'])
            if metrics.get('has_educational_framing'):
                file_stats['hints_with_framing'] += 1

        # Analyze hints array
        if 'hints' in question and question['hints']:
            file_stats['has_hints_array'] += 1
            # Check if progressive (first hint should be longer or more general)
            hints = question['hints']
            if len(hints) >= 2:
                first_has_framing = any(word in hints[0] for word in ['Consider', 'Think', 'Remember'])
                if first_has_framing:
                    file_stats['hints_array_progressive'] += 1

        # Analyze explanation
        if 'explanation' in question and question['explanation']:
            file_stats['has_explanation'] += 1
            exp_metrics = analyze_explanation(question['explanation'])

            if exp_metrics.get('has_why'):
                file_stats['explanations_with_why'] += 1

            if exp_metrics.get('has_best_practice'):
                file_stats['explanations_with_best_practice'] += 1

            explanation_lengths.append(exp_metrics['length'])

    if explanation_lengths:
        file_stats['avg_explanation_length'] = sum(explanation_lengths) / len(explanation_lengths)

    return file_stats


def main():
    print("="*70)
    print("VALIDATION REPORT - Hint & Explanation Improvements")
    print("="*70)

    json_files = sorted([f for f in QUESTIONS_DIR.glob("*.json") if f.is_file()])

    all_stats = {
        'total_questions': 0,
        'has_hint': 0,
        'has_hints_array': 0,
        'has_explanation': 0,
        'hints_with_framing': 0,
        'explanations_with_why': 0,
        'explanations_with_best_practice': 0,
        'hints_array_progressive': 0,
    }

    print(f"\n{'File':<35} {'Questions':<12} {'Hints w/ Frame':<16} {'Exp w/ Why':<12}")
    print("-"*70)

    for filepath in json_files:
        stats = analyze_file(filepath)

        all_stats['total_questions'] += stats['total_questions']
        all_stats['has_hint'] += stats['has_hint']
        all_stats['has_hints_array'] += stats['has_hints_array']
        all_stats['has_explanation'] += stats['has_explanation']
        all_stats['hints_with_framing'] += stats['hints_with_framing']
        all_stats['explanations_with_why'] += stats['explanations_with_why']
        all_stats['explanations_with_best_practice'] += stats['explanations_with_best_practice']
        all_stats['hints_array_progressive'] += stats['hints_array_progressive']

        print(f"{filepath.name:<35} {stats['total_questions']:<12} "
              f"{stats['hints_with_framing']:<16} {stats['explanations_with_why']:<12}")

    print("="*70)
    print(f"{'TOTALS':<35} {all_stats['total_questions']:<12} "
          f"{all_stats['hints_with_framing']:<16} {all_stats['explanations_with_why']:<12}")

    # Calculate percentages
    print(f"\n{'='*70}")
    print("QUALITY METRICS")
    print(f"{'='*70}")

    if all_stats['has_hint'] > 0:
        framing_pct = (all_stats['hints_with_framing'] / all_stats['has_hint']) * 100
        print(f"Hints with educational framing: {all_stats['hints_with_framing']}/{all_stats['has_hint']} ({framing_pct:.1f}%)")

    if all_stats['has_hints_array'] > 0:
        progressive_pct = (all_stats['hints_array_progressive'] / all_stats['has_hints_array']) * 100
        print(f"Hints arrays with progressive structure: {all_stats['hints_array_progressive']}/{all_stats['has_hints_array']} ({progressive_pct:.1f}%)")

    if all_stats['has_explanation'] > 0:
        why_pct = (all_stats['explanations_with_why'] / all_stats['has_explanation']) * 100
        print(f"Explanations with 'why' reasoning: {all_stats['explanations_with_why']}/{all_stats['has_explanation']} ({why_pct:.1f}%)")

        bp_pct = (all_stats['explanations_with_best_practice'] / all_stats['has_explanation']) * 100
        print(f"Explanations with best practices: {all_stats['explanations_with_best_practice']}/{all_stats['has_explanation']} ({bp_pct:.1f}%)")

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Total questions analyzed: {all_stats['total_questions']}")
    print(f"Questions with single hint field: {all_stats['has_hint']}")
    print(f"Questions with hints array: {all_stats['has_hints_array']}")
    print(f"Questions with explanation: {all_stats['has_explanation']}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
