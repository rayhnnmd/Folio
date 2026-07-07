from app import db
from datetime import datetime


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    title = db.Column(db.String(200), default="Untitled")
    content = db.Column(db.Text, default="")
    tags = db.Column(db.String(300), default="")  # comma-separated
    mood = db.Column(db.String(30), default="")
    word_count = db.Column(db.Integer, default=0)
    is_pinned = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def days_since_update(self):
        return (datetime.utcnow() - self.updated_at).days

    def age_class(self):
        days = self.days_since_update()
        if days >= 21:
            return "note--age-3"
        if days >= 14:
            return "note--age-2"
        if days >= 7:
            return "note--age-1"
        return ""

    def __repr__(self):
        return f"<Note {self.title}>"