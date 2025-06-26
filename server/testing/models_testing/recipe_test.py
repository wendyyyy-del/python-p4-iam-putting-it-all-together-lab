import pytest
from sqlalchemy.exc import IntegrityError

from app import app
from models import db, Recipe, User

class TestRecipe:
    '''Recipe in models.py'''

    def test_has_attributes(self):
        '''has attributes title, instructions, and minutes_to_complete.'''

        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # Create and commit a user first
            user = User(username="HamFan")
            user.password_hash = "secretpass"
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions=(
                    "Or kind rest bred with am shed then. In raptures building an bringing be. "
                    "Elderly is detract tedious assured private so to visited. Do travelling "
                    "companions contrasted it. Mistress strongly remember up to. Ham him compass "
                    "you proceed calling detract. Better of always missed we person mr. September "
                    "smallness northward situation few her certainty something."
                ),
                minutes_to_complete=60,
                user=user  # ✅ associate recipe with user
            )

            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter_by(title="Delicious Shed Ham").first()

            assert new_recipe.title == "Delicious Shed Ham"
            assert new_recipe.minutes_to_complete == 60
            assert new_recipe.user_id == user.id

    def test_requires_title(self):
        '''requires each record to have a title.'''

        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="NoTitleUser")
            user.password_hash = "pass123"
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                instructions="This has no title but 50+ character instructions, which is valid.",
                minutes_to_complete=30,
                user=user
            )

            with pytest.raises(IntegrityError):
                db.session.add(recipe)
                db.session.commit()

    def test_requires_50_plus_char_instructions(self):
        '''raises ValueError or IntegrityError for short instructions'''

        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="Shorty")
            user.password_hash = "pass123"
            db.session.add(user)
            db.session.commit()

            with pytest.raises((IntegrityError, ValueError)):
                recipe = Recipe(
                    title="Short Ham",
                    instructions="Too short!",
                    minutes_to_complete=20,
                    user=user
                )
                db.session.add(recipe)
                db.session.commit()
