#!/usr/bin/env python3
"""
Script to improve hints and explanations for C Programming Practice System questions.
"""

import json
import re
from pathlib import Path

class HintExplanationImprover:
    def __init__(self):
        self.stats = {
            'total_questions': 0,
            'hints_improved': 0,
            'explanations_improved': 0,
            'files_processed': 0
        }

    def improve_hint(self, question, original_hint):
        """
        Improve a hint to guide students without giving away the answer.
        Returns improved hint or None if no improvement needed.
        """
        if not original_hint or original_hint.strip() == "":
            return None

        # Common patterns that need improvement
        improvements = []

        # Check if hint is too short (likely not helpful)
        if len(original_hint) < 20:
            return None  # Will need manual review

        # Check if hint gives away the answer directly
        giveaway_patterns = [
            r'(the answer is|correct answer|answer:|^[A-D]\.)',
            r'(use|write|return|output)\s+["\'].*["\']',
        ]

        for pattern in giveaway_patterns:
            if re.search(pattern, original_hint, re.IGNORECASE):
                return None  # Needs manual review

        # Enhance generic hints with better phrasing
        hint = original_hint.strip()

        # Add thinking prompts if missing
        thinking_words = ['consider', 'think', 'remember', 'recall', 'note']
        has_thinking_prompt = any(word in hint.lower() for word in thinking_words)

        if not has_thinking_prompt and not hint[0].isupper():
            # Capitalize first letter
            hint = hint[0].upper() + hint[1:]

        return hint

    def improve_explanation(self, question, original_explanation):
        """
        Improve an explanation to be more educational.
        Returns improved explanation or None if no improvement needed.
        """
        if not original_explanation or original_explanation.strip() == "":
            return None

        explanation = original_explanation.strip()

        # Check if explanation is too short (likely not educational enough)
        if len(explanation) < 30:
            return None  # Needs manual review

        # Ensure it doesn't just state the answer without teaching
        if re.match(r'^(The answer is|Correct answer|Answer:)', explanation, re.IGNORECASE):
            return None  # Needs manual review

        # Capitalize first letter if needed
        if explanation and not explanation[0].isupper():
            explanation = explanation[0].upper() + explanation[1:]

        return explanation

    def process_question(self, question):
        """Process a single question and improve its hint and explanation."""
        improved = False

        # Process hint
        if 'hint' in question:
            if isinstance(question['hint'], list):
                # Multiple hints
                new_hints = []
                for i, hint in enumerate(question['hint']):
                    improved_hint = self.improve_hint(question, hint)
                    if improved_hint and improved_hint != hint:
                        new_hints.append(improved_hint)
                        improved = True
                        self.stats['hints_improved'] += 1
                    else:
                        new_hints.append(hint)
                question['hint'] = new_hints
            else:
                # Single hint
                improved_hint = self.improve_hint(question, question['hint'])
                if improved_hint and improved_hint != question['hint']:
                    question['hint'] = improved_hint
                    improved = True
                    self.stats['hints_improved'] += 1

        # Process explanation
        if 'explanation' in question:
            improved_explanation = self.improve_explanation(question, question['explanation'])
            if improved_explanation and improved_explanation != question['explanation']:
                question['explanation'] = improved_explanation
                improved = True
                self.stats['explanations_improved'] += 1

        return improved

    def process_file(self, filepath):
        """Process a single JSON file containing questions."""
        print(f"Processing {filepath.name}...")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        questions = data.get('questions', [])
        file_improved = False

        for i, question in enumerate(questions):
            if self.process_question(question):
                file_improved = True
            self.stats['total_questions'] += 1

        # Save the file if any improvements were made
        if file_improved:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.stats['files_processed'] += 1
            print(f"  ✓ Saved improvements to {filepath.name}")
        else:
            print(f"  - No automatic improvements needed for {filepath.name}")

        return file_improved

    def process_all_files(self, questions_dir):
        """Process all question files in the directory."""
        questions_path = Path(questions_dir)
        json_files = sorted(questions_path.glob('*.json'))

        for filepath in json_files:
            self.process_file(filepath)

        # Print statistics
        print("\n" + "="*60)
        print("IMPROVEMENT STATISTICS")
        print("="*60)
        print(f"Total questions processed: {self.stats['total_questions']}")
        print(f"Files modified: {self.stats['files_processed']}")
        print(f"Hints improved: {self.stats['hints_improved']}")
        print(f"Explanations improved: {self.stats['explanations_improved']}")
        print("="*60)

if __name__ == '__main__':
    questions_dir = '/Users/jonasvindahl/Documents/projects/7_imperative_exam/questions/'
    improver = HintExplanationImprover()
    improver.process_all_files(questions_dir)
