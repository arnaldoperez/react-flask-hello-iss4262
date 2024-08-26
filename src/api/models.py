from flask_sqlalchemy import SQLAlchemy
from firebase_admin import storage
from datetime import timedelta

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=True)
    last_name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    profile_pic = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return '<User %r>' % self.first_name

    def getProfilePicture(self):
        output = ""
        if self.profile_pic is not None:
            bucket = storage.bucket()
            resource = bucket.blob(self.profile_pic)
            picture_url = resource.generate_signed_url(
                version="v4", expiration=timedelta(minutes=15), method="GET")
            output = picture_url
        return output

    def serialize(self):
        output = {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "profilePicture": ""
            # do not serialize the password, its a security breach
        }
        if self.profile_pic is not None:
            bucket = storage.bucket()
            resource = bucket.blob(self.profile_pic)
            picture_url = resource.generate_signed_url(
                version="v4", expiration=timedelta(minutes=15), method="GET")
            output["profilePicture"] = picture_url
        return output


class TokenBlockedList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(100), nullable=False)
