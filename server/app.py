from flask import Flask, request, session
from flask_restful import Resource, Api
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from models import db, User, Recipe

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super-secret-key'

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)


class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"error": "Username and password required."}, 422

        image_url = data.get("image_url", "https://cdn.vox-cdn.com/thumbor/I3GEucLDPT6sRdISXmY_Yh8IzDw=/0x0:1920x1080/1820x1024/filters:focal(960x540:961x541)/cdn.vox-cdn.com/uploads/chorus_asset/file/24185682/Ash_Ketchum_World_Champion_Screenshot_4.jpg")
        bio = data.get("bio", "")

        user = User(username=username, image_url=image_url, bio=bio)
        user.password_hash = password  
        try:
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            return {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio
            }, 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Username already exists."}, 422



class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {}, 401

        user = db.session.get(User, user_id)
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio
            }, 200
        return {}, 401


class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
            session["user_id"] = user.id
            return {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio
            }, 200
        return {"error": "Invalid username or password."}, 401


class Logout(Resource):
    def delete(self):
        if not session.get("user_id"):
            return {"error": "Unauthorized"}, 401
        session.pop("user_id", None)
        return {}, 204


class RecipeIndex(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized."}, 401

        user = db.session.get(User, user_id)
        recipes = [
            {
                "id": r.id,
                "title": r.title,
                "instructions": r.instructions,
                "minutes_to_complete": r.minutes_to_complete,
                "user_id": r.user_id
            } for r in user.recipes
        ]
        return recipes, 200

    def post(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized."}, 401

        data = request.get_json()
        title = data.get("title")
        instructions = data.get("instructions")
        minutes = data.get("minutes_to_complete")

        if not title or not instructions or len(instructions.strip()) < 50:
            return {"error": "Invalid recipe data."}, 422

        recipe = Recipe(
            title=title.strip(),
            instructions=instructions.strip(),
            minutes_to_complete=minutes,
            user_id=user_id
        )

        db.session.add(recipe)
        db.session.commit()

        return {
            "id": recipe.id,
            "title": recipe.title,
            "instructions": recipe.instructions,
            "minutes_to_complete": recipe.minutes_to_complete,
            "user_id": recipe.user_id
        }, 201

api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(RecipeIndex, '/recipes')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5555, debug=True)