from application import db


class ImageRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255))
    extracted_text = db.Column(db.Text)
    translated_text = db.Column(db.Text)
    audio_filename = db.Column(db.String(255))
