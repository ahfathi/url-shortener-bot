from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hsh = db.Column(db.Integer, nullable=False, index=True)
    long_url = db.Column(db.Text, nullable=False)
    uix = db.UniqueConstraint('hsh', 'long_url')
