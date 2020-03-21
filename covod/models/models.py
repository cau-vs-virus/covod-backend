import enum
import time
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from sqlalchemy_utils import UUIDType
from sqlalchemy_utils.types.password import PasswordType
from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin,
    OAuth2TokenMixin,
)

db = SQLAlchemy()


class MediaType(enum.Enum):
    VIDEO_ONLY = 1
    AUDIO_ONLY = 2
    AUDIO_VIDEO = 3


class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUIDType(binary=False), unique=True, nullable=False)
    type = db.Column(Enum(MediaType), nullable=False)
    lecture_id = db.Column(db.Integer, db.ForeignKey("lecture.id"), nullable=False)
    lecture = db.relationship("Lecture", back_populates="media", uselist=False)


class Lecture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    name = db.Column(db.String(80))
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    media = db.relationship("Media", uselist=False, back_populates="lecture")

    def __str__(self):
        return self.number


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    lectures = db.relationship("Lecture", backref="course")

    def __str__(self):
        return self.name


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    full_name = db.Column(db.String(80))
    password = db.Column(PasswordType(schemes=["pbkdf2_sha512"]))

    def __str__(self):
        return self.username

    def check_password(self, password):
        return self.password == password


class OAuth2Client(db.Model, OAuth2ClientMixin):
    __tablename__ = "oauth2_client"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))
    user = db.relationship("User")


class OAuth2Token(db.Model, OAuth2TokenMixin):
    __tablename__ = "oauth2_token"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))
    user = db.relationship("User")

    def is_refresh_token_active(self):
        if self.revoked:
            return False
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at >= time.time()