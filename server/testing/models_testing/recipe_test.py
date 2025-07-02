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

            user = User(username="HasAttrsUser")
            user.password_hash = "somepass123"
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions="""Or kind rest bred with am shed then. In raptures building an bringing be. Elderly is detract 
                tedious assured private so to visited. Do travelling companions contrasted it. Mistress strongly remember 
                up to. Ham him compass you proceed calling detract. Better of always missed we person mr. September 
                smallness northward situation few her certainty something.""",
                minutes_to_complete=60,
                user_id=user.id
            )

            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter(Recipe.title == "Delicious Shed Ham").first()

            assert new_recipe.title == "Delicious Shed Ham"
            assert "Or kind rest bred" in new_recipe.instructions
            assert new_recipe.minutes_to_complete == 60

    def test_requires_title(self):
        '''requires each record to have a title.'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # Create a user to satisfy the foreign key
            user = User(username="NoTitleUser")
            user.password_hash = "somepass123"
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                instructions="A" * 60,  # ✅ Valid instructions (>= 50 chars)
                minutes_to_complete=20,
                user_id=user.id         # ✅ Valid user_id
            )

            with pytest.raises(IntegrityError):
                db.session.add(recipe)
                db.session.commit()

    def test_requires_50_plus_char_instructions(self):
        '''must raise IntegrityError or ValueError if instructions < 50 characters'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # Create user first to satisfy foreign key
            user = User(username="FailingUser")
            user.password_hash = "abc123"
            db.session.add(user)
            db.session.commit()

            with pytest.raises(ValueError):
                # The error is raised during object creation because of @validates
                recipe = Recipe(
                    title="Generic Ham",
                    instructions="Too short",  # ❌ less than 50 characters
                    minutes_to_complete=20,
                    user_id=user.id
                )
                db.session.add(recipe)
                db.session.commit()