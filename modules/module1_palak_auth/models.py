# modules/module1_palak_auth/models.py
# Author: Palak Rawat
# OS Concept: Process Synchronization / Authentication State & Session Control

from flask_login import UserMixin
from extensions import db, bcrypt


class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_role = db.Column(db.String(30), nullable=False)
    login_status = db.Column(db.String(20), default="Logged Out")
    session_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def get_id(self):
        return str(self.user_id)

    @property
    def id(self):
        return self.user_id

    @property
    def password_hash(self):
        return self.password

    def set_password(self, raw_password):
        self.password = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password):
        return bcrypt.check_password_hash(self.password, raw_password)

    def __repr__(self):
        return f"<User {self.username} - {self.user_role}>"
