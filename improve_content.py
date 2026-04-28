#!/usr/bin/env python3
"""
Improve hints and explanations for C Programming Practice System.
This script reads all question files and enhances educational content.
"""

import json
import re
from pathlib import Path
from anthropic import Anthropic
import os

# Configuration
QUESTIONS_DIR = Path("/Users/jonasvindahl/Documents/projects/7_imperative_exam/questions")
API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Initialize Anthropic client
client = Anthropic(api_key=API_KEY) if API_KEY else None

# Statistics
stats = {
    'total_questions': 0,
    'hints_improved': 0,
    'explanations_improved': 0,
    'files_processed': 0,
    'questions_per_file': {}
}

IMPROVEMENT_PROMPT = """You are an expert C programming educator. Your task is to improve the educational content for a C programming question.

QUESTION DATA:
{question_json}

GUIDELINES FOR HINTS:
- Guide the student toward the answer WITHOUT giving it away
- Reference the relevant C concept or technique
- Be progressive (start general, get more specific)
- Encourage thinking: "Consider...", "Think about...", "Remember that..."
- Should NOT contain the answer itself

GUIDELINES FOR EXPLANATIONS:
- TEACH the concept, not just state the answer
- Explain WHY the correct answer is correct
- Point out common mistakes if applicable
- Reference C language rules or best practices
- Be clear and concise (2-4 sentences ideal)
- Use proper C terminology

TASK:
1. If there is a 'hint' field, improve it following the hint guidelines
2. If there is a 'hints' array, improve each hint to be progressive
3. Improve the 'explanation' field following the explanation guidelines
4. Maintain any Danish text if present

Return ONLY a JSON object with these fields (include only fields that exist in the original):
{{
  "hint": "improved single hint if it exists",
  "hints": ["improved hint 1", "improved hint 2", ...] if array exists,
  "explanation": "improved explanation"
}}
"""

def improve_question_content(question):
    """
    Use Claude to improve hints and explanation for a question.
    Returns dict with improved content or None if no improvement needed.
    """
    if not client:
        return None

    # Prepare question data for the prompt
    question_data = {
        'id': question.get('id'),
        'title': question.get('title'),
        'description': question.get('description'),
        'code_template': question.get('code_template', ''),
        'options': question.get('options', []),
        'correct_answer': question.get('correct_answer'),
        'current_hint': question.get('hint'),
        'current_hints': question.get('hints'),
        'current_explanation': question.get('explanation')
    }

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": IMPROVEMENT_PROMPT.format(
                    question_json=json.dumps(question_data, indent=2)
                )
            }]
        )

        # Extract JSON from response
        response_text = message.content[0].text
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            improvements = json.loads(json_match.group())
            return improvements

    except Exception as e:
        print(f"  Error improving question {question.get('id')}: {e}")

    return None

def process_question(question):
    """Process a single question and improve its content."""
    improvements = improve_question_content(question)

    if not improvements:
        return False

    changed = False

    # Update hint
    if 'hint' in improvements and 'hint' in question:
        if improvements['hint'] != question['hint']:
            question['hint'] = improvements['hint']
            stats['hints_improved'] += 1
            changed = True

    # Update hints array
    if 'hints' in improvements and 'hints' in question:
        if improvements['hints'] != question['hints']:
            question['hints'] = improvements['hints']
            stats['hints_improved'] += 1
            changed = True

    # Update explanation
    if 'explanation' in improvements and 'explanation' in question:
        if improvements['explanation'] != question['explanation']:
            question['explanation'] = improvements['explanation']
            stats['explanations_improved'] += 1
            changed = True

    return changed

def process_file(filepath):
    """Process a single question file."""
    print(f"\nProcessing {filepath.name}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    questions = data.get('questions', [])
    file_question_count = len(questions)
    print(f"  Found {file_question_count} questions")

    stats['questions_per_file'][filepath.name] = file_question_count

    file_changed = False
    for i, question in enumerate(questions, 1):
        stats['total_questions'] += 1

        if i % 10 == 0:
            print(f"  Processing question {i}/{file_question_count}...")

        if process_question(question):
            file_changed = True

    # Save the file with proper formatting
    if file_changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Saved improvements to {filepath.name}")
    else:
        print(f"  No changes needed for {filepath.name}")

    stats['files_processed'] += 1

def main():
    """Main function to process all question files."""
    if not client:
        print("ERROR: ANTHROPIC_API_KEY not found in environment variables")
        return

    print("C Programming Practice System - Content Improvement Tool")
    print("=" * 70)

    # Get all JSON files (excluding old_categories)
    json_files = [f for f in QUESTIONS_DIR.glob("*.json") if f.is_file()]

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
    print("\nQuestions per file:")
    for filename, count in sorted(stats['questions_per_file'].items()):
        print(f"  {filename}: {count}")
    print("=" * 70)

if __name__ == "__main__":
    main()
