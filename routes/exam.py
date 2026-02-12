from flask import Blueprint, redirect, request, session, flash, url_for, current_app
from flask_login import login_required

exam_bp = Blueprint('exam', __name__, url_prefix='/exam')


@exam_bp.route('/switch', methods=['POST'])
@login_required
def switch_exam():
    """Switch the active exam/course"""
    exam_id = request.form.get('exam_id')
    exam_service = current_app.config['EXAM_SERVICE']

    if not exam_id:
        flash('No exam selected.', 'error')
        return redirect(request.referrer or url_for('progress.dashboard'))

    if exam_service.set_active_exam(exam_id):
        exam = exam_service.get_exam(exam_id)
        # Clear any active practice session when switching exams
        session.pop('practice_questions', None)
        session.pop('current_question_index', None)
        session.pop('session_start_time', None)
        session.pop('question_start_time', None)
        session.pop('answered_questions', None)
        flash(f'Switched to {exam["name"]}', 'success')
    else:
        flash('Invalid exam selected.', 'error')

    return redirect(request.referrer or url_for('progress.dashboard'))
