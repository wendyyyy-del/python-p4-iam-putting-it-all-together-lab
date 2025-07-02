from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)
    
    image_url = db.Column(
    db.String,
    default="https://cdn.pixabay.com/photo/2015/03/04/22/35/head-659651_1280.png"
)


    bio = db.Column(db.String, default="")

    recipes = db.relationship("Recipe", backref="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hash is not readable.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = generate_password_hash(password)

    def authenticate(self, password):
        return check_password_hash(self._password_hash, password)

    @validates("username")
    def validate_username(self, key, value):
        if not value or len(value.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        return value.strip()


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"<Recipe {self.title}>"

    @validates("title")
    def validate_title(self, key, value):
        if not value or len(value.strip()) == 0:
            raise ValueError("Title is required.")
        return value.strip()

    @validates("instructions")
    def validate_instructions(self, key, value):
        if not value or len(value.strip()) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return value.strip()