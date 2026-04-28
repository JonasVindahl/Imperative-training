#!/usr/bin/env python3
"""
Comprehensive script to improve hints and explanations for C Programming Practice System.
Processes all 762 questions across 8 categories.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class QuestionImprover:
    def __init__(self):
        self.stats = {
            'total_questions': 0,
            'hints_created': 0,
            'explanations_improved': 0,
            'explanations_created': 0,
            'files_modified': 0
        }

    def create_hint_from_question(self, question_data: Dict) -> Optional[str]:
        """
        Generate a helpful hint based on the question content and explanation.
        Returns a hint that guides without giving away the answer.
        """
        explanation = question_data.get('explanation', '')
        question_text = question_data.get('question', '')
        category = question_data.get('category', '')
        code = question_data.get('code', '')

        if not explanation:
            return None

        # Extract key concepts from explanation to create progressive hints
        hint = None

        # Pattern-based hint generation based on common C concepts

        # Integer division
        if 'integer division' in explanation.lower() or 'truncate' in explanation.lower():
            hint = "Remember that when both operands are integers, C performs integer division which truncates the decimal part."

        # Type casting
        elif 'cast' in explanation.lower() and 'double' in explanation.lower():
            hint = "Consider what happens when you cast an operand to a floating-point type before performing the operation."

        # Pointer arithmetic
        elif 'pointer arithmetic' in explanation.lower():
            hint = "Think about how pointer arithmetic works with the size of the data type being pointed to."

        # Array decay
        elif 'array' in explanation.lower() and 'decay' in explanation.lower():
            hint = "Remember that arrays decay to pointers when passed to functions."

        # Memory allocation
        elif 'malloc' in explanation.lower() or 'calloc' in explanation.lower():
            hint = "Consider what value malloc() returns when memory allocation fails."

        # NULL pointer
        elif 'null' in explanation.lower() and 'pointer' in explanation.lower():
            hint = "Think about what happens when you dereference a NULL pointer."

        # String operations
        elif 'string' in explanation.lower() and ('null terminator' in explanation.lower() or '\\0' in explanation):
            hint = "Remember that C strings are null-terminated arrays of characters."

        # Sizeof operator
        elif 'sizeof' in explanation.lower():
            hint = "Think about what sizeof returns - the size in bytes, not the number of elements."

        # Undefined behavior
        elif 'undefined' in explanation.lower():
            hint = "This code exhibits undefined behavior. Consider what C standard says about this operation."

        # Operator precedence
        elif 'precedence' in explanation.lower():
            hint = "Consider the order of operations and operator precedence in C."

        # Post/Pre increment
        elif 'post' in explanation.lower() and 'increment' in explanation.lower():
            hint = "Remember the difference between post-increment (i++) and pre-increment (++i)."

        # Modulo operation
        elif 'modulo' in explanation.lower() or '% operator' in explanation:
            hint = "Think about what the modulo operator (%) returns - the remainder of division."

        # Logical vs Bitwise
        elif ('logical' in explanation.lower() and 'bitwise' in explanation.lower()) or ('&&' in explanation and '&' in explanation):
            hint = "Consider the difference between logical operators (&&, ||) and bitwise operators (&, |)."

        # Memory leak
        elif 'memory leak' in explanation.lower() or 'free' in explanation.lower():
            hint = "Remember to free dynamically allocated memory to avoid memory leaks."

        # Scope
        elif 'scope' in explanation.lower():
            hint = "Think about variable scope and lifetime in C."

        # Short-circuit evaluation
        elif 'short-circuit' in explanation.lower():
            hint = "Remember that logical operators use short-circuit evaluation."

        # File operations
        elif 'fopen' in explanation.lower() or 'fclose' in explanation.lower():
            hint = "Consider proper file handling - always check if fopen() succeeded and close files when done."

        # Recursion
        elif 'recursive' in explanation.lower() or 'base case' in explanation.lower():
            hint = "Think about the base case and how the function calls itself with modified arguments."

        # Struct member access
        elif 'struct' in explanation.lower() and ('->' in explanation or '.' in code):
            hint = "Remember: use '.' for struct variables and '->' for struct pointers."

        # Generic fallback based on first sentence of explanation
        if not hint and explanation:
            # Take first sentence as basis for hint
            first_sentence = explanation.split('.')[0]
            if len(first_sentence) > 20 and len(first_sentence) < 100:
                # Convert explanation to a thinking prompt
                if 'c' in first_sentence.lower() and ('result' in first_sentence.lower() or 'answer' in first_sentence.lower()):
                    hint = f"Consider the C language rule: {first_sentence.lower()}."
                else:
                    hint = f"Think about: {first_sentence.lower()}."

        return hint

    def improve_explanation(self, explanation: str, question_data: Dict) -> str:
        """
        Improve an existing explanation to be more educational.
        """
        if not explanation:
            return explanation

        # Ensure explanation starts with capital letter
        explanation = explanation.strip()
        if explanation and not explanation[0].isupper():
            explanation = explanation[0].upper() + explanation[1:]

        # Ensure explanation ends with proper punctuation
        if explanation and explanation[-1] not in '.!?':
            explanation += '.'

        # Check if explanation is too short and not educational enough
        if len(explanation) < 40:
            # Could be improved but needs manual review
            pass

        return explanation

    def process_question(self, question: Dict) -> bool:
        """Process a single question. Returns True if modified."""
        modified = False

        # Create hint if missing
        if not question.get('hint'):
            hint = self.create_hint_from_question(question)
            if hint:
                question['hint'] = hint
                self.stats['hints_created'] += 1
                modified = True

        # Improve explanation if exists
        if question.get('explanation'):
            original = question['explanation']
            improved = self.improve_explanation(original, question)
            if improved != original:
                question['explanation'] = improved
                self.stats['explanations_improved'] += 1
                modified = True
        elif not question.get('explanation'):
            # No explanation - needs to be created
            # This is complex and needs manual review, skip for now
            self.stats['explanations_created'] += 1
            modified = False

        return modified

    def process_file(self, filepath: Path) -> Tuple[int, int]:
        """
        Process a single JSON file.
        Returns (total_questions, modified_questions)
        """
        print(f"\nProcessing {filepath.name}...")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        questions = data.get('questions', [])
        modified_count = 0

        for question in questions:
            if self.process_question(question):
                modified_count += 1
            self.stats['total_questions'] += 1

        # Save file if any modifications were made
        if modified_count > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.stats['files_modified'] += 1
            print(f"  ✓ Modified {modified_count}/{len(questions)} questions")
        else:
            print(f"  - No modifications made")

        return len(questions), modified_count

    def process_all_files(self, questions_dir: str):
        """Process all question files in order of size (largest first)."""
        questions_path = Path(questions_dir)

        # Process files in order of priority (largest first)
        file_order = [
            'fundamentals.json',
            'pointers_and_memory.json',
            'functions_and_recursion.json',
            'structs_and_data_structures.json',
            'arrays_and_strings.json',
            'control_flow.json',
            'file_io.json',
            'programming_challenges.json'
        ]

        for filename in file_order:
            filepath = questions_path / filename
            if filepath.exists():
                self.process_file(filepath)

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print processing statistics."""
        print("\n" + "="*70)
        print("IMPROVEMENT SUMMARY")
        print("="*70)
        print(f"Total questions processed:    {self.stats['total_questions']}")
        print(f"Files modified:               {self.stats['files_modified']}")
        print(f"Hints created:                {self.stats['hints_created']}")
        print(f"Explanations improved:        {self.stats['explanations_improved']}")
        print(f"Explanations needing creation: {self.stats['explanations_created']}")
        print("="*70)

def main():
    questions_dir = '/Users/jonasvindahl/Documents/projects/7_imperative_exam/questions/'
    improver = QuestionImprover()
    improver.process_all_files(questions_dir)

    print("\n✓ Processing complete!")
    print("\nNote: Some questions may need manual review for:")
    print("  - Complex hints requiring deep C knowledge")
    print("  - Missing explanations (especially in programming_challenges)")
    print("  - Very short explanations that need expansion")

if __name__ == '__main__':
    main()
