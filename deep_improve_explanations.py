#!/usr/bin/env python3
"""
Deep improvement of explanations - make them more educational.
This focuses on enhancing explanations to teach concepts, not just state answers.
"""

import json
from pathlib import Path
import re

QUESTIONS_DIR = Path("/Users/jonasvindahl/Documents/projects/7_imperative_exam/questions")

stats = {
    'total_questions': 0,
    'explanations_improved': 0,
    'files_processed': 0
}


def get_concept_teaching(tags, category):
    """Get teaching phrase based on tags and category."""
    teachings = {
        'integer_division': "In C, when both operands of the division operator are integers, the result is truncated toward zero, discarding any fractional part.",
        'float_division': "When at least one operand is a floating-point type, C performs floating-point division, preserving the fractional part of the result.",
        'casting': "Type casting in C converts a value from one type to another. Casting happens before the operation when you cast an operand.",
        'pointers': "Pointers store memory addresses. The * operator dereferences a pointer to access the value at that address.",
        'pointer_arithmetic': "Pointer arithmetic in C moves the pointer by multiples of the pointed-to type's size, not by bytes.",
        'arrays': "In C, arrays decay to pointers when passed to functions, losing size information.",
        'strings': "C strings are null-terminated character arrays. The null terminator '\\0' marks the end of the string.",
        'malloc': "malloc() allocates memory dynamically on the heap and returns NULL if allocation fails. Always check for NULL before dereferencing.",
        'memory_leak': "Memory leaks occur when dynamically allocated memory is not freed. Always free() what you malloc().",
        'segfault': "Segmentation faults occur when accessing invalid memory, such as dereferencing NULL or using freed memory.",
        'undefined_behavior': "Undefined behavior means the C standard doesn't specify what should happen. Avoid it by following language rules carefully.",
        'recursion': "Recursive functions call themselves. They need a base case to stop recursion and prevent stack overflow.",
        'scope': "Variable scope determines where a variable can be accessed. Local variables are only accessible within their block.",
        'struct': "Structs group related data together. Access members with the dot operator (.) or arrow operator (->) for pointers.",
        'sizeof': "sizeof returns the size in bytes at compile time. For arrays, it only works on the original array, not a pointer parameter.",
    }

    # Check tags first
    for tag in tags:
        if tag in teachings:
            return teachings[tag]

    # Check category
    if category in teachings:
        return teachings[category]

    return None


def needs_expansion(explanation):
    """Determine if explanation needs to be expanded."""
    if not explanation:
        return True

    # Too short - likely just states answer
    if len(explanation) < 60:
        return True

    # Doesn't explain why
    educational_indicators = ['because', 'since', 'therefore', 'thus', 'this means',
                              'as a result', 'consequently', 'this is why', 'when', 'always', 'never']

    has_why = any(indicator in explanation.lower() for indicator in educational_indicators)

    if not has_why:
        return True

    return False


def improve_explanation(explanation, question_context):
    """Improve explanation to be more educational."""
    if not explanation:
        return explanation, False

    improved = explanation
    changed = False

    # Remove "The answer is X." prefix
    answer_pattern = r'^(The (correct )?answer is [A-D]\.|Answer: [A-D]\.?)\s*'
    if re.match(answer_pattern, improved):
        improved = re.sub(answer_pattern, '', improved)
        changed = True

    # Ensure explanation teaches the concept
    tags = question_context.get('tags', [])
    category = question_context.get('category', '')

    concept_teaching = get_concept_teaching(tags, category)

    # If explanation is too short or doesn't explain why, enhance it
    if needs_expansion(improved):
        if concept_teaching:
            # Add concept teaching if not already present
            if concept_teaching.lower()[:30] not in improved.lower():
                # Prepend or append the teaching
                if len(improved) < 40:
                    improved = f"{concept_teaching} {improved}"
                else:
                    # Insert teaching naturally
                    if improved.endswith('.'):
                        improved = f"{improved} {concept_teaching}"
                    else:
                        improved = f"{improved}. {concept_teaching}"
                changed = True

    # Add common mistake warning if appropriate
    if 'common' in ' '.join(tags).lower() or 'error' in ' '.join(tags).lower():
        mistake_indicators = ['mistake', 'error', 'incorrect', 'wrong', 'careful', 'avoid']
        has_warning = any(word in improved.lower() for word in mistake_indicators)

        if not has_warning and len(improved) < 200:
            # Could add a mistake warning, but need context
            pass

    # Ensure proper sentence structure
    if improved and not improved.endswith(('.', '!', '?')):
        improved += '.'
        changed = True

    # Make sure first letter is capitalized
    if improved and improved[0].islower():
        improved = improved[0].upper() + improved[1:]
        changed = True

    # Remove redundant phrases
    redundant_patterns = [
        (r'\s+therefore\s+therefore\s+', ' therefore '),
        (r'\s+because\s+because\s+', ' because '),
        (r'\.\s*\.\s*', '. '),
    ]

    for pattern, replacement in redundant_patterns:
        if re.search(pattern, improved):
            improved = re.sub(pattern, replacement, improved)
            changed = True

    # Ensure we reference C language explicitly
    if len(improved) > 50 and ' C ' not in improved and 'In C,' not in improved:
        # Check if it should mention C explicitly
        if any(tag in tags for tag in ['standard', 'language', 'specification']):
            pass  # Already clear from context

    return improved, changed


def enhance_explanation_quality(explanation, question_context):
    """Second pass: enhance explanation quality with better structure."""
    if not explanation:
        return explanation, False

    improved = explanation
    changed = False

    # Structure: Concept -> Why -> Consequence
    sentences = re.split(r'(?<=[.!?])\s+', improved)

    if len(sentences) >= 2:
        # Check if we explain concept, then why, then consequence
        has_concept = len(sentences[0]) > 30
        has_why = any(word in ' '.join(sentences[1:]).lower()
                     for word in ['because', 'since', 'therefore', 'this means'])

        # Good structure - keep it
        pass

    # Add "Always" or "Never" rule if appropriate
    if question_context.get('difficulty') == 'easy':
        rule_keywords = ['check', 'free', 'initialize', 'null', 'bounds']
        if any(keyword in improved.lower() for keyword in rule_keywords):
            if 'always' not in improved.lower() and 'never' not in improved.lower():
                # Could add best practice note
                pass

    # Ensure technical terms are used correctly
    technical_terms = {
        'null pointer': 'NULL pointer',
        'null terminator': 'null terminator',
        'seg fault': 'segmentation fault',
        'segfault': 'segmentation fault',
    }

    for wrong, correct in technical_terms.items():
        if wrong in improved.lower() and correct.lower() not in improved.lower():
            improved = re.sub(re.escape(wrong), correct, improved, flags=re.IGNORECASE)
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
        'tags': question.get('tags', []),
        'correct_answer': question.get('correct_answer'),
        'options': question.get('options', [])
    }

    if 'explanation' in question and question['explanation']:
        # First pass: improve content
        improved, changed1 = improve_explanation(question['explanation'], question_context)

        # Second pass: enhance quality
        improved, changed2 = enhance_explanation_quality(improved, question_context)

        if changed1 or changed2:
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
        print(f"  No additional changes needed for {filepath.name}")

    stats['files_processed'] += 1


def main():
    print("C Programming Practice System - Deep Explanation Improver")
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
    print(f"Explanations improved: {stats['explanations_improved']}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
