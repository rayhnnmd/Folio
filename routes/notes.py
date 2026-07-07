from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from models.note import Note

notes_bp = Blueprint("notes", __name__)


@notes_bp.route("/notes")
@login_required
def dashboard():
    tag_filter = request.args.get("tag", "")
    query = Note.query.filter_by(user_id=current_user.id)

    if tag_filter:
        # simple tag filter — checks if tag string contains the filter
        query = query.filter(Note.tags.contains(tag_filter))

    notes = query.order_by(Note.is_pinned.desc(), Note.updated_at.desc()).all()

    # collect all unique tags across user's notes
    all_tags = set()
    for n in notes:
        if n.tags:
            for t in n.tags.split(","):
                all_tags.add(t.strip())

    return render_template("notes.html",
        notes=notes,
        all_tags=sorted(all_tags),
        active_tag=tag_filter
    )


@notes_bp.route("/notes/new", methods=["POST"])
@login_required
def new_note():
    note = Note(user_id=current_user.id)
    db.session.add(note)
    db.session.commit()
    return redirect(url_for("notes.editor", note_id=note.id))


@notes_bp.route("/notes/<int:note_id>")
@login_required
def editor(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    return render_template("editor.html", note=note)


@notes_bp.route("/notes/<int:note_id>/save", methods=["POST"])
@login_required
def save_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    data = request.get_json()

    note.title = data.get("title", "Untitled")
    note.content = data.get("content", "")
    note.tags = data.get("tags", "")
    note.mood = data.get("mood", "")
    note.word_count = len(note.content.split()) if note.content else 0
    note.updated_at = datetime.utcnow()

    db.session.commit()
    return jsonify({"status": "saved", "updated_at": note.updated_at.isoformat()})


@notes_bp.route("/notes/<int:note_id>/pin", methods=["POST"])
@login_required
def pin_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    note.is_pinned = not note.is_pinned
    db.session.commit()
    return jsonify({"pinned": note.is_pinned})


@notes_bp.route("/notes/<int:note_id>/delete", methods=["POST"])
@login_required
def delete_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for("notes.dashboard"))


@notes_bp.route("/focus/<int:note_id>")
@login_required
def focus(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    return render_template("focus.html", note=note)