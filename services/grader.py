import re
from typing import Dict, List, Any
from services.compiler import CompilerService


class GraderService:
    """Service for grading different types of C programming exercises"""

    def __init__(self):
        self.compiler = CompilerService()

    def grade_output_prediction(self, question: Dict, user_answer: str) -> Dict:
        """Grade output prediction exercises"""
        correct_output = question['correct_answer'].strip()
        user_output = user_answer.strip()

        # Normalize whitespace for comparison
        correct_normalized = ' '.join(correct_output.split())
        user_normalized = ' '.join(user_output.split())

        is_correct = correct_normalized == user_normalized

        return {
            'correct': is_correct,
            'expected': correct_output,
            'received': user_output,
            'explanation': question.get('explanation', '')
        }

    def grade_bug_finding(self, question: Dict, user_answer: str) -> Dict:
        """Grade bug finding exercises (user identifies line numbers)"""
        correct_lines = set(question['correct_answer'])  # Set of line numbers
        user_lines = self._parse_line_numbers(user_answer)

        is_correct = correct_lines == user_lines

        return {
            'correct': is_correct,
            'expected_lines': sorted(correct_lines),
            'found_lines': sorted(user_lines),
            'explanation': question.get('explanation', '')
        }

    def grade_code_completion(self, question: Dict, user_code: str, test_cases: List[Dict]) -> Dict:
        """Grade code completion exercises by running test cases"""
        results = []
        all_passed = True

        for test_case in test_cases:
            # Replace placeholder with user's code
            full_code = question['code_template'].replace('/* YOUR CODE HERE */', user_code)

            # Compile and run
            result = self.compiler.compile_and_run(full_code, test_case.get('input', ''))

            if not result['success']:
                all_passed = False
                results.append({
                    'input': test_case.get('input', ''),
                    'expected': test_case['expected_output'],
                    'received': result.get('error', 'Compilation/Runtime error'),
                    'passed': False
                })
            else:
                output = result['stdout'].strip()
                expected = test_case['expected_output'].strip()
                passed = output == expected

                if not passed:
                    all_passed = False

                results.append({
                    'input': test_case.get('input', ''),
                    'expected': expected,
                    'received': output,
                    'passed': passed
                })

        return {
            'correct': all_passed,
            'test_results': results,
            'explanation': question.get('explanation', '')
        }

    def grade_code_writing(self, question: Dict, user_code: str) -> Dict:
        """Grade full code writing exercises"""
        test_cases = question.get('test_cases', [])
        return self.grade_code_completion(question, user_code, test_cases)

    def grade_multiple_choice(self, question: Dict, user_answer: str) -> Dict:
        """Grade multiple choice questions"""
        correct = question['correct_answer']
        is_correct = user_answer.strip().upper() == correct.strip().upper()

        return {
            'correct': is_correct,
            'expected': correct,
            'received': user_answer,
            'explanation': question.get('explanation', '')
        }

    def grade_memory_tracing(self, question: Dict, user_answer: str) -> Dict:
        """Grade memory allocation/deallocation tracing"""
        correct_trace = question['correct_answer']
        user_trace = user_answer.strip()

        # Parse malloc/free counts or patterns
        is_correct = self._compare_memory_traces(correct_trace, user_trace)

        return {
            'correct': is_correct,
            'expected': correct_trace,
            'received': user_trace,
            'explanation': question.get('explanation', '')
        }

    def grade_struct_size(self, question: Dict, user_answer: str) -> Dict:
        """Grade struct size calculation"""
        try:
            user_size = int(user_answer.strip())
            correct_size = int(question['correct_answer'])
            is_correct = user_size == correct_size

            return {
                'correct': is_correct,
                'expected': correct_size,
                'received': user_size,
                'explanation': question.get('explanation', ''),
                'memory_layout': question.get('memory_layout', '')
            }
        except ValueError:
            return {
                'correct': False,
                'expected': question['correct_answer'],
                'received': user_answer,
                'explanation': 'Please enter a valid number',
                'memory_layout': question.get('memory_layout', '')
            }

    def grade_fill_blanks(self, question: Dict, user_answer: str) -> Dict:
        """Grade fill-in-the-blanks questions"""
        import json
        try:
            # user_answer is JSON: {"blank1": "answer1", "blank2": "answer2"}
            user_answers = json.loads(user_answer)
        except:
            user_answers = {}

        questions_data = question.get('questions', [])
        all_correct = True
        results = []

        for q_item in questions_data:
            blanks = q_item.get('blanks', [])
            for idx, blank in enumerate(blanks):
                blank_id = f"blank_{q_item.get('id', 0)}_{idx}"
                user_val = user_answers.get(blank_id, '')
                correct_val = blank.get('correct', '')

                is_correct = user_val.strip().lower() == correct_val.strip().lower()
                if not is_correct:
                    all_correct = False

                results.append({
                    'blank_id': blank_id,
                    'user_answer': user_val,
                    'correct_answer': correct_val,
                    'correct': is_correct
                })

        return {
            'correct': all_correct,
            'blank_results': results,
            'explanation': question.get('explanation', '')
        }

    def grade_drag_drop(self, question: Dict, user_answer: str) -> Dict:
        """Grade drag-and-drop code assembly"""
        import json
        try:
            # user_answer is JSON: {"blank1": "token", "blank2": "token"}
            user_placements = json.loads(user_answer)
        except:
            user_placements = {}

        blanks = question.get('blanks', {})
        all_correct = True
        results = []

        for blank_id, blank_data in blanks.items():
            user_token = user_placements.get(blank_id, '')
            correct_token = blank_data.get('correct', '')

            is_correct = user_token == correct_token
            if not is_correct:
                all_correct = False

            results.append({
                'blank_id': blank_id,
                'user_answer': user_token,
                'correct_answer': correct_token,
                'expected': correct_token,  # For UI compatibility
                'received': user_token,     # For UI compatibility
                'passed': is_correct,       # For UI compatibility
                'correct': is_correct
            })

        # Build summary for UI
        user_summary = ', '.join([f"{r['blank_id']}: {r['received']}" for r in results])
        correct_summary = ', '.join([f"{r['blank_id']}: {r['expected']}" for r in results])

        return {
            'correct': all_correct,
            'blank_results': results,
            'test_results': results,  # For UI compatibility
            'expected': correct_summary,
            'received': user_summary,
            'explanation': question.get('explanation', ''),
            'correct_code': self._build_code_from_blanks(question, blanks)
        }

    def grade_recursive_trace(self, question: Dict, user_answer: str) -> Dict:
        """Grade recursive function tracing"""
        import json
        try:
            # user_answer is JSON: {"test_0": "result", "test_1": "result"}
            user_results = json.loads(user_answer)
        except:
            user_results = {}

        test_cases = question.get('test_cases', [])
        all_correct = True
        results = []

        for idx, test_case in enumerate(test_cases):
            test_id = f"test_{idx}"
            user_val = user_results.get(test_id, '').strip()
            correct_val = str(test_case.get('correct_answer', '')).strip()

            is_correct = user_val == correct_val
            if not is_correct:
                all_correct = False

            results.append({
                'input': test_case.get('input', ''),
                'user_answer': user_val,
                'correct_answer': correct_val,
                'expected': correct_val,  # For UI compatibility
                'received': user_val,     # For UI compatibility
                'passed': is_correct,     # For UI compatibility
                'correct': is_correct,
                'trace': test_case.get('trace', [])
            })

        return {
            'correct': all_correct,
            'test_results': results,
            'explanation': question.get('explanation', '')
        }

    def _build_code_from_blanks(self, question: Dict, blanks: Dict) -> str:
        """Build the complete code with correct answers"""
        code_template = question.get('code_template', '')
        for blank_id, blank_data in blanks.items():
            code_template = code_template.replace(f'{{{blank_id}}}', blank_data.get('correct', ''))
        return code_template

    def grade(self, question: Dict, user_answer: str) -> Dict:
        """Main grading method that dispatches to specific graders"""
        question_type = question.get('type', 'code_output')

        grading_methods = {
            'code_output': self.grade_output_prediction,
            'bug_finding': self.grade_bug_finding,
            'code_completion': self.grade_code_completion,
            'code_writing': self.grade_code_writing,
            'multiple_choice': self.grade_multiple_choice,
            'memory_tracing': self.grade_memory_tracing,
            'struct_size': self.grade_struct_size,
            'fill_blanks': self.grade_fill_blanks,
            'drag_drop': self.grade_drag_drop,
            'recursive_trace': self.grade_recursive_trace
        }

        grading_method = grading_methods.get(question_type, self.grade_output_prediction)

        # For code completion/writing, pass test cases
        if question_type in ['code_completion', 'code_writing']:
            return grading_method(question, user_answer)
        else:
            return grading_method(question, user_answer)

    def _parse_line_numbers(self, text: str) -> set:
        """Extract line numbers from user's answer"""
        numbers = re.findall(r'\d+', text)
        return set(int(n) for n in numbers)

    def _compare_memory_traces(self, correct: str, user: str) -> bool:
        """Compare memory allocation traces"""
        # Simple comparison for now
        # Could be enhanced to parse malloc/free patterns
        return correct.strip().lower() == user.strip().lower()
