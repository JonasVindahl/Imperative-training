from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_required, current_user
from services.question_loader import QuestionLoader
from services.grader import GraderService
from services.adaptive import AdaptiveLearningService
from services.compiler import CompilerService
from models import db, Attempt
from config import Config
from datetime import datetime

practice_bp = Blueprint('practice', __name__, url_prefix='/practice')

# Initialize services
question_loader = QuestionLoader(Config.QUESTIONS_DIR)
grader_service = GraderService()
compiler_service = CompilerService()


@practice_bp.route('/start', methods=['GET', 'POST'])
@login_required
def start_practice():
    """Start a new practice session"""
    if request.method == 'POST':
        # Clear any existing session data before starting a new one
        session.pop('practice_questions', None)
        session.pop('current_question_index', None)
        session.pop('session_start_time', None)
        session.pop('question_start_time', None)
        session.pop('answered_questions', None)

        mode = request.form.get('mode', 'smart')
        category = request.form.get('category', None)
        try:
            requested_count = int(request.form.get('question_count', 10))
        except (TypeError, ValueError):
            requested_count = 10
        requested_count = max(1, min(requested_count, 50))

        # Load questions
        all_questions = question_loader.load_all_questions()

        if mode == 'smart':
            # Adaptive learning mode
            adaptive_service = AdaptiveLearningService(current_user.id)
            questions = adaptive_service.generate_practice_session(
                all_questions,
                session_size=requested_count
            )
        elif mode == 'category':
            if not category:
                flash('Please select a category before starting.', 'error')
                question_ids = session.get('practice_questions', [])
                current_index = session.get('current_question_index', 0)
                has_active_session = bool(question_ids) and current_index < len(question_ids)
                remaining_questions = max(len(question_ids) - current_index, 0)
                return render_template(
                    'start_practice.html',
                    has_active_session=has_active_session,
                    remaining_questions=remaining_questions
                )
            # Specific category practice
            questions = question_loader.get_random_questions(category, requested_count)
        else:
            # Random mixed practice
            import random
            all_q = []
            for cat_questions in all_questions.values():
                all_q.extend(cat_questions)
            unique_questions = list({q.get('id'): q for q in all_q}.values())
            questions = random.sample(unique_questions, min(requested_count, len(unique_questions)))

        # Store session data
        session['practice_questions'] = [q['id'] for q in questions]
        session['current_question_index'] = 0
        session['session_start_time'] = datetime.utcnow().isoformat()
        session['question_start_time'] = datetime.utcnow().isoformat()

        return redirect(url_for('practice.question'))

    # Show practice mode selection
    question_ids = session.get('practice_questions', [])
    current_index = session.get('current_question_index', 0)
    has_active_session = bool(question_ids) and current_index < len(question_ids)
    remaining_questions = max(len(question_ids) - current_index, 0)

    return render_template(
        'start_practice.html',
        has_active_session=has_active_session,
        remaining_questions=remaining_questions
    )


@practice_bp.route('/question')
@login_required
def question():
    """Display current question"""
    if 'practice_questions' not in session:
        return redirect(url_for('practice.start_practice'))

    question_ids = session.get('practice_questions', [])
    current_index = session.get('current_question_index', 0)

    if current_index >= len(question_ids):
        return redirect(url_for('practice.session_complete'))

    question_id = question_ids[current_index]
    question_data = question_loader.get_question_by_id(question_id)

    if not question_data:
        return redirect(url_for('practice.session_complete'))

    # Track question start time
    session['question_start_time'] = datetime.utcnow().isoformat()

    answered_questions = set(session.get('answered_questions', []))
    has_answered = question_id in answered_questions

    return render_template('practice.html',
                         question=question_data,
                         question_number=current_index + 1,
                         total_questions=len(question_ids),
                         has_answered=has_answered)


@practice_bp.route('/submit', methods=['POST'])
@login_required
def submit_answer():
    """Submit and grade an answer"""
    data = request.json
    question_id = data.get('question_id')
    user_answer = data.get('answer', '')
    hints_used = data.get('hints_used', 0)

    # Load question
    question = question_loader.get_question_by_id(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404

    # Grade the answer
    result = grader_service.grade(question, user_answer)

    # Calculate time spent
    start_time_str = session.get('question_start_time')
    time_spent = 0
    if start_time_str:
        start_time = datetime.fromisoformat(start_time_str)
        time_spent = int((datetime.utcnow() - start_time).total_seconds())

    # Save attempt to database
    attempt = Attempt(
        user_id=current_user.id,
        question_id=question_id,
        category=question['category'],
        correct=result['correct'],
        time_spent=time_spent,
        submitted_answer=user_answer,
        hints_used=hints_used
    )
    db.session.add(attempt)

    # Update progress
    adaptive_service = AdaptiveLearningService(current_user.id)
    adaptive_service.update_progress(question['category'], result['correct'])

    answered_questions = session.get('answered_questions', [])
    if question_id not in answered_questions:
        answered_questions.append(question_id)
        session['answered_questions'] = answered_questions

    db.session.commit()

    return jsonify({
        'correct': result['correct'],
        'explanation': result.get('explanation', ''),
        'expected': result.get('expected'),
        'received': result.get('received'),
        'test_results': result.get('test_results'),
        'memory_layout': result.get('memory_layout')
    })


@practice_bp.route('/next')
@login_required
def next_question():
    """Move to next question"""
    if 'practice_questions' not in session:
        return redirect(url_for('practice.start_practice'))

    session['current_question_index'] = session.get('current_question_index', 0) + 1
    return redirect(url_for('practice.question'))


@practice_bp.route('/complete')
@login_required
def session_complete():
    """Practice session completion summary"""
    question_ids = session.get('practice_questions', [])

    if not question_ids:
        return redirect(url_for('practice.start_practice'))

    # Get all attempts from this session
    attempts = Attempt.query.filter(
        Attempt.user_id == current_user.id,
        Attempt.question_id.in_(question_ids)
    ).order_by(Attempt.timestamp.desc()).limit(len(question_ids)).all()

    correct_count = sum(1 for a in attempts if a.correct)
    total_time = sum(a.time_spent for a in attempts)

    incorrect_details = []
    for attempt in attempts:
        if not attempt.correct:
            question = question_loader.get_question_by_id(attempt.question_id)
            if question:
                incorrect_details.append({
                    'attempt': attempt,
                    'question': question
                })

    # Clear session
    session.pop('practice_questions', None)
    session.pop('current_question_index', None)
    session.pop('session_start_time', None)
    session.pop('answered_questions', None)

    return render_template('session_complete.html',
                         attempts=attempts,
                         correct_count=correct_count,
                         total_questions=len(question_ids),
                         total_time=total_time,
                         incorrect_details=incorrect_details)


@practice_bp.route('/compile', methods=['POST'])
@login_required
def compile_code():
    """Compile and run C code (for testing/validation)"""
    data = request.json
    code = data.get('code', '')
    input_data = data.get('input', '')

    result = compiler_service.compile_and_run(code, input_data)

    return jsonify(result)
