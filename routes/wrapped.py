from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from collections import Counter
from models.note import Note

wrapped_bp = Blueprint("wrapped", __name__)


@wrapped_bp.route("/wrapped")
@login_required
def index():
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0)

    notes = Note.query.filter(
        Note.user_id == current_user.id,
        Note.created_at >= month_start
    ).all()

    all_notes = Note.query.filter_by(user_id=current_user.id).all()

    day_counts = Counter()
    for n in notes:
        day_counts[n.created_at.strftime("%A")] += 1

    tag_counts = Counter()
    for n in all_notes:
        if n.tags:
            for t in n.tags.split(","):
                tag_counts[t.strip()] += 1

    mood_counts = Counter(n.mood for n in notes if n.mood)

    word_by_day = {}
    for n in all_notes:
        key = n.updated_at.strftime("%Y-%m-%d")
        word_by_day[key] = word_by_day.get(key, 0) + n.word_count

    days_30 = [(now - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(29, -1, -1)]
    word_data = [word_by_day.get(d, 0) for d in days_30]
    day_labels = [(now - timedelta(days=i)).strftime("%b %d") for i in range(29, -1, -1)]

    return render_template("wrapped.html",
        notes_this_month=len(notes),
        total_notes=len(all_notes),
        total_words=sum(n.word_count for n in all_notes),
        longest_note=max(all_notes, key=lambda n: n.word_count, default=None),
        most_productive_day=day_counts.most_common(1)[0][0] if day_counts else "—",
        top_tags=tag_counts.most_common(5),
        mood_counts=dict(mood_counts),
        word_data=word_data,
        day_labels=day_labels,
    )