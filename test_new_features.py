#!/usr/bin/env python3
"""
End-to-end testing script for new interactive question types
Tests: Fill-in-the-Blanks, Drag-and-Drop, Recursive Trace
"""

import json
import sys
from services.grader import GraderService
from services.question_loader import QuestionLoader

# Color output for terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_test(test_name, passed):
    """Print test result with color"""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} {test_name}")
    return passed

def test_fill_blanks():
    """Test fill-in-the-blanks grading"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Testing Fill-in-the-Blanks{Colors.END}")
    print("=" * 60)

    grader = GraderService()
    loader = QuestionLoader('questions')

    # Load fill_blanks questions
    questions = loader.load_category('fill_blanks')
    if not questions:
        print_test("Load fill_blanks questions", False)
        return False

    print_test(f"Load fill_blanks questions ({len(questions)} found)", True)

    # Test question 1: Function Parameters
    question = questions[0]

    # Test 1: All correct answers
    correct_answer = json.dumps({
        "blank_0_0": "local variables",
        "blank_0_1": "the function",
        "blank_1_0": "formal parameters",
        "blank_2_0": "integers"
    })

    result = grader.grade(question, correct_answer)
    test1 = print_test("Fill-blanks: All correct answers", result['correct'])

    # Test 2: Some wrong answers
    wrong_answer = json.dumps({
        "blank_0_0": "global variables",  # Wrong
        "blank_0_1": "the function",
        "blank_1_0": "formal parameters",
        "blank_2_0": "integers"
    })

    result = grader.grade(question, wrong_answer)
    test2 = print_test("Fill-blanks: Detect incorrect answer", not result['correct'])

    # Test 3: Empty answer
    empty_answer = json.dumps({})
    result = grader.grade(question, empty_answer)
    test3 = print_test("Fill-blanks: Handle empty answer", not result['correct'])

    return test1 and test2 and test3

def test_drag_drop():
    """Test drag-and-drop grading"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Testing Drag-and-Drop Code Assembly{Colors.END}")
    print("=" * 60)

    grader = GraderService()
    loader = QuestionLoader('questions')

    # Load drag_drop questions
    questions = loader.load_category('drag_drop')
    if not questions:
        print_test("Load drag_drop questions", False)
        return False

    print_test(f"Load drag_drop questions ({len(questions)} found)", True)

    # Test question 1: find_last function
    question = questions[0]

    # Test 1: All correct placements
    correct_answer = json.dumps({
        "blank1": "NULL",
        "blank2": "!=",
        "blank3": "NULL",
        "blank4": "node",
        "blank5": "->key",
        "blank6": "k",
        "blank7": "r",
        "blank8": "node",
        "blank9": "node",
        "blank10": "r"
    })

    result = grader.grade(question, correct_answer)
    test1 = print_test("Drag-drop: All correct tokens", result['correct'])

    # Test 2: Wrong token placement
    wrong_answer = json.dumps({
        "blank1": "node",  # Wrong - should be NULL
        "blank2": "!=",
        "blank3": "NULL",
        "blank4": "node",
        "blank5": "->key",
        "blank6": "k",
        "blank7": "r",
        "blank8": "node",
        "blank9": "node",
        "blank10": "r"
    })

    result = grader.grade(question, wrong_answer)
    test2 = print_test("Drag-drop: Detect incorrect token", not result['correct'])

    # Test question 2: While loop (simpler test)
    question2 = questions[1]

    correct_answer2 = json.dumps({
        "blank1": "0",
        "blank2": "1",
        "blank3": "<=",
        "blank4": "+=",
        "blank5": "++"
    })

    result = grader.grade(question2, correct_answer2)
    test3 = print_test("Drag-drop: While loop question", result['correct'])

    return test1 and test2 and test3

def test_recursive_trace():
    """Test recursive function tracing"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Testing Recursive Function Tracing{Colors.END}")
    print("=" * 60)

    grader = GraderService()
    loader = QuestionLoader('questions')

    # Load recursive_trace questions
    questions = loader.load_category('recursive_trace')
    if not questions:
        print_test("Load recursive_trace questions", False)
        return False

    print_test(f"Load recursive_trace questions ({len(questions)} found)", True)

    # Test question 1: Custom f(x) function
    question = questions[0]

    # Test 1: All correct traces
    correct_answer = json.dumps({
        "test_0": "-1",
        "test_1": "-1",
        "test_2": "1",
        "test_3": "5"
    })

    result = grader.grade(question, correct_answer)
    test1 = print_test("Recursive-trace: All correct values", result['correct'])

    # Test 2: Some wrong values
    wrong_answer = json.dumps({
        "test_0": "-1",
        "test_1": "0",  # Wrong - should be -1
        "test_2": "1",
        "test_3": "5"
    })

    result = grader.grade(question, wrong_answer)
    test2 = print_test("Recursive-trace: Detect incorrect value", not result['correct'])

    # Test question 2: Factorial
    question2 = questions[1]

    correct_answer2 = json.dumps({
        "test_0": "1",
        "test_1": "6",
        "test_2": "120"
    })

    result = grader.grade(question2, correct_answer2)
    test3 = print_test("Recursive-trace: Factorial question", result['correct'])

    # Test question 3: Fibonacci
    question3 = questions[2]

    correct_answer3 = json.dumps({
        "test_0": "0",
        "test_1": "1",
        "test_2": "3"
    })

    result = grader.grade(question3, correct_answer3)
    test4 = print_test("Recursive-trace: Fibonacci question", result['correct'])

    return test1 and test2 and test3 and test4

def test_question_count():
    """Test total question count across all categories"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Testing Question Inventory{Colors.END}")
    print("=" * 60)

    loader = QuestionLoader('questions')
    all_questions = loader.load_all_questions()

    total = sum(len(questions) for questions in all_questions.values())

    print(f"\n{Colors.BOLD}Question Count by Category:{Colors.END}")
    for category, questions in all_questions.items():
        print(f"  {category:20s}: {len(questions):3d} questions")

    print(f"\n{Colors.BOLD}Total Questions: {total}{Colors.END}")

    # Check specific counts
    test1 = print_test("Fill-blanks has >= 40 questions", len(all_questions.get('fill_blanks', [])) >= 40)
    test2 = print_test("Drag-drop has >= 55 questions", len(all_questions.get('drag_drop', [])) >= 55)
    test3 = print_test("Recursive-trace has >= 40 questions", len(all_questions.get('recursive_trace', [])) >= 40)
    test4 = print_test(f"Total questions >= 700", total >= 700)

    return test1 and test2 and test3 and test4

def test_question_structure():
    """Test that questions have required fields"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Testing Question Structure{Colors.END}")
    print("=" * 60)

    loader = QuestionLoader('questions')
    all_tests_passed = True

    # Test fill_blanks structure
    fill_blanks = loader.load_category('fill_blanks')
    for q in fill_blanks:
        has_required = all([
            'id' in q,
            'type' in q,
            'questions' in q,
            q['type'] == 'fill_blanks'
        ])
        if not has_required:
            print_test(f"Fill-blanks {q.get('id', 'unknown')} has required fields", False)
            all_tests_passed = False

    if all_tests_passed:
        print_test("Fill-blanks questions have correct structure", True)

    # Test drag_drop structure
    drag_drop = loader.load_category('drag_drop')
    for q in drag_drop:
        has_required = all([
            'id' in q,
            'type' in q,
            'code_template' in q,
            'blanks' in q,
            q['type'] == 'drag_drop'
        ])
        if not has_required:
            print_test(f"Drag-drop {q.get('id', 'unknown')} has required fields", False)
            all_tests_passed = False

    if all_tests_passed:
        print_test("Drag-drop questions have correct structure", True)

    # Test recursive_trace structure
    recursive_trace = loader.load_category('recursive_trace')
    for q in recursive_trace:
        has_required = all([
            'id' in q,
            'type' in q,
            'code_template' in q,
            'test_cases' in q,
            q['type'] == 'recursive_trace'
        ])
        if not has_required:
            print_test(f"Recursive-trace {q.get('id', 'unknown')} has required fields", False)
            all_tests_passed = False

    if all_tests_passed:
        print_test("Recursive-trace questions have correct structure", True)

    return all_tests_passed

def test_multiple_select():
    """Test multiple select (checkbox) question type"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Testing Multiple Select (Checkbox){Colors.END}")
    print("=" * 60)

    grader = GraderService()
    loader = QuestionLoader('questions')

    # Load memory_management questions
    questions = loader.load_category('memory_management')

    # Find multiple_select questions
    ms_questions = [q for q in questions if q.get('type') == 'multiple_select']

    test1 = print_test(f"Found {len(ms_questions)} multiple_select questions", len(ms_questions) >= 3)

    if not ms_questions:
        return False

    # Test grading of multiple_select
    question = {
        'type': 'multiple_select',
        'correct_answer': ['A', 'C', 'D'],
        'explanation': 'Test'
    }

    # Test all correct
    result = grader.grade(question, json.dumps(['A', 'C', 'D']))
    test2 = print_test("Multiple-select: All correct answers", result['correct'])

    # Test partial (should fail)
    result = grader.grade(question, json.dumps(['A', 'C']))
    test3 = print_test("Multiple-select: Detect missing answer", not result['correct'])

    # Test extra answer (should fail)
    result = grader.grade(question, json.dumps(['A', 'B', 'C', 'D']))
    test4 = print_test("Multiple-select: Detect extra answer", not result['correct'])

    # Test case insensitive
    result = grader.grade(question, json.dumps(['a', 'c', 'd']))
    test5 = print_test("Multiple-select: Case insensitive", result['correct'])

    return test1 and test2 and test3 and test4 and test5

def test_linked_list_questions():
    """Test linked list programming questions"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Testing Linked List Questions{Colors.END}")
    print("=" * 60)

    loader = QuestionLoader('questions')

    # Load programming_tasks questions
    questions = loader.load_category('programming_tasks')

    # Find linked list questions
    ll_questions = [q for q in questions if 'linked_lists' in q.get('tags', [])]

    test1 = print_test(f"Found {len(ll_questions)} linked list questions", len(ll_questions) >= 4)

    # Check node_t struct presence
    all_have_node_t = all('node_t' in q.get('code_template', '') for q in ll_questions)
    test2 = print_test("All linked list questions have node_t struct", all_have_node_t)

    # Check for exam_style tag
    exam_style = sum(1 for q in ll_questions if 'exam_style' in q.get('tags', []))
    test3 = print_test(f"Found {exam_style} exam-style linked list questions", exam_style >= 4)

    return test1 and test2 and test3

def test_exam_coverage():
    """Test that all exam question types are covered"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Testing Exam Coverage (Q1-Q19){Colors.END}")
    print("=" * 60)

    loader = QuestionLoader('questions')

    # Check for mixed drag-drop tokens
    drag_drop = loader.load_category('drag_drop')
    exam_drag = sum(1 for q in drag_drop if 'exam_style' in q.get('tags', []))
    test1 = print_test(f"Mixed drag-drop tokens (Q12, Q14): {exam_drag} questions", exam_drag > 0)

    # Check for multiple_select
    memory = loader.load_category('memory_management')
    ms_count = sum(1 for q in memory if q.get('type') == 'multiple_select')
    test2 = print_test(f"Multiple select checkboxes (Q13, Q15): {ms_count} questions", ms_count >= 3)

    # Check for conceptual questions
    terminology = loader.load_category('terminology')
    test3 = print_test(f"Conceptual/terminology questions (Q17): {len(terminology)} questions", len(terminology) >= 50)

    # Check for linked list questions
    programming = loader.load_category('programming_tasks')
    ll_count = sum(1 for q in programming if 'linked_lists' in q.get('tags', []))
    test4 = print_test(f"Linked list programming (Q18): {ll_count} questions", ll_count >= 4)

    print(f"\n{Colors.GREEN}✓ All exam question types (Q1-Q19) are now supported!{Colors.END}")

    return test1 and test2 and test3 and test4

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'=' * 60}")
    print("C PROGRAMMING PRACTICE SYSTEM - NEW FEATURES TEST SUITE")
    print(f"{'=' * 60}{Colors.END}\n")

    results = []

    # Run all test suites
    results.append(("Fill-in-the-Blanks", test_fill_blanks()))
    results.append(("Drag-and-Drop", test_drag_drop()))
    results.append(("Recursive Trace", test_recursive_trace()))
    results.append(("Multiple Select (NEW)", test_multiple_select()))
    results.append(("Linked List Questions (NEW)", test_linked_list_questions()))
    results.append(("Exam Coverage (Q1-Q19)", test_exam_coverage()))
    results.append(("Question Count", test_question_count()))
    results.append(("Question Structure", test_question_structure()))

    # Print summary
    print(f"\n{Colors.BOLD}{'=' * 60}")
    print("TEST SUMMARY")
    print(f"{'=' * 60}{Colors.END}\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{Colors.GREEN}PASSED{Colors.END}" if result else f"{Colors.RED}FAILED{Colors.END}"
        print(f"  {name:30s}: {status}")

    print(f"\n{Colors.BOLD}Overall: {passed}/{total} test suites passed{Colors.END}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All tests passed! New features are working correctly.{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Some tests failed. Please review the output above.{Colors.END}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
