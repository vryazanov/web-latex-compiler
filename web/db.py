import uuid

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class AsyncResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.Text, nullable=False, unique=True)
    origin_key = db.Column(db.Text, nullable=False, unique=True)
    target_key = db.Column(db.Text, nullable=True, unique=True)

    def generate_origin_key(self, filename: str):
        self.token = str(uuid.uuid4())
        self.origin_key = f'{self.token}/{filename}'

    def generate_target_key(self):
        path, _ = self.origin_key.rsplit('.')  # take path without extension
        self.target_key = f'{path}.pdf'
