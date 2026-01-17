from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from services.adaptive import AdaptiveLearningService
from models import Attempt, Progress
from datetime import datetime, timedelta

progress_bp = Blueprint('progress', __name__, url_prefix='/progress')


@progress_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard showing user progress"""
    adaptive_service = AdaptiveLearningService(current_user.id)
    progress_summary = adaptive_service.get_progress_summary()

    # Get recent attempts
    recent_attempts = Attempt.query.filter_by(user_id=current_user.id)\
        .order_by(Attempt.timestamp.desc())\
        .limit(10)\
        .all()

    # Calculate streak
    streak = calculate_streak(current_user.id)

    return render_template('dashboard.html',
                         progress=progress_summary,
                         recent_attempts=recent_attempts,
                         streak=streak,
                         user=current_user)


@progress_bp.route('/stats')
@login_required
def stats():
    """Detailed statistics page"""
    adaptive_service = AdaptiveLearningService(current_user.id)
    progress_summary = adaptive_service.get_progress_summary()

    # Get all attempts
    all_attempts = Attempt.query.filter_by(user_id=current_user.id)\
        .order_by(Attempt.timestamp.desc())\
        .all()

    # Calculate additional statistics
    total_time = sum(a.time_spent for a in all_attempts)
    avg_time_per_question = total_time / len(all_attempts) if all_attempts else 0

    # Category breakdown
    category_stats = {}
    for attempt in all_attempts:
        if attempt.category not in category_stats:
            category_stats[attempt.category] = {
                'correct': 0,
                'total': 0,
                'time': 0
            }
        category_stats[attempt.category]['total'] += 1
        if attempt.correct:
            category_stats[attempt.category]['correct'] += 1
        category_stats[attempt.category]['time'] += attempt.time_spent

    # Build trend data for the last 14 days
    today = datetime.utcnow().date()
    last_days = [today - timedelta(days=i) for i in range(13, -1, -1)]
    attempts_by_day = {}
    for attempt in all_attempts:
        attempt_day = attempt.timestamp.date()
        attempts_by_day.setdefault(attempt_day, []).append(attempt)

    trend_labels = [day.strftime('%b %d') for day in last_days]
    trend_accuracy = []
    trend_attempts = []
    for day in last_days:
        day_attempts = attempts_by_day.get(day, [])
        total = len(day_attempts)
        correct = sum(1 for a in day_attempts if a.correct)
        trend_attempts.append(total)
        if total == 0:
            trend_accuracy.append(None)
        else:
            trend_accuracy.append(int((correct / total) * 100))

    category_labels = []
    category_accuracy = []
    category_summary = []
    for category in sorted(category_stats.keys()):
        stats = category_stats[category]
        category_labels.append(category.replace('_', ' ').title())
        if stats['total'] > 0:
            accuracy = int((stats['correct'] / stats['total']) * 100)
        else:
            accuracy = 0
        category_accuracy.append(accuracy)
        category_summary.append(f"{category_labels[-1]}: {accuracy}%")

    return render_template('stats.html',
                         progress=progress_summary,
                         category_stats=category_stats,
                         total_time=total_time,
                         avg_time=avg_time_per_question,
                         attempts_count=len(all_attempts),
                         trend_labels=trend_labels,
                         trend_accuracy=trend_accuracy,
                         trend_attempts=trend_attempts,
                         category_labels=category_labels,
                         category_accuracy=category_accuracy,
                         category_summary=category_summary)


@progress_bp.route('/api/progress')
@login_required
def api_progress():
    """API endpoint for progress data (for charts)"""
    adaptive_service = AdaptiveLearningService(current_user.id)
    progress_summary = adaptive_service.get_progress_summary()
    return jsonify(progress_summary)


def calculate_streak(user_id: int) -> int:
    """
    Calculate the current practice streak in days

    Args:
        user_id: User ID

    Returns:
        Number of consecutive days practiced
    """
    attempts = Attempt.query.filter_by(user_id=user_id)\
        .order_by(Attempt.timestamp.desc())\
        .all()

    if not attempts:
        return 0

    today = datetime.utcnow().date()
    current_date = today
    streak = 0

    # Group attempts by date
    attempt_dates = set()
    for attempt in attempts:
        attempt_dates.add(attempt.timestamp.date())

    # Check consecutive days
    while current_date in attempt_dates:
        streak += 1
        current_date -= timedelta(days=1)

    # If no practice today, don't count streak
    if today not in attempt_dates:
        return 0

    return streak
