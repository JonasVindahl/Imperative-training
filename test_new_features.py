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
    test1 = print_test("Fill-blanks has 2 questions", len(all_questions.get('fill_blanks', [])) == 2)
    test2 = print_test("Drag-drop has 2 questions", len(all_questions.get('drag_drop', [])) == 2)
    test3 = print_test("Recursive-trace has 3 questions", len(all_questions.get('recursive_trace', [])) == 3)
    test4 = print_test(f"Total questions >= 41", total >= 41)

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
