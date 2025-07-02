from random import randint, choice as rc
from faker import Faker

from app import app
from models import db, Recipe, User

fake = Faker()

with app.app_context():

    print("Deleting all records...")
    Recipe.query.delete()
    User.query.delete()
    db.session.commit()

    print("Creating users...")
    users = []
    usernames = set()

    for _ in range(20):
        username = fake.first_name()
        while username in usernames:
            username = fake.first_name()
        usernames.add(username)

        user = User(
            username=username,
            bio=fake.paragraph(nb_sentences=3),
            image_url="https://cdn.vox-cdn.com/thumbor/I3GEucLDPT6sRdISXmY_Yh8IzDw=/0x0:1920x1080/1820x1024/filters:focal(960x540:961x541)/cdn.vox-cdn.com/uploads/chorus_asset/file/21904538/blank_profile_pic.jpeg"
        )
        user.password_hash = f"{username}_password"  
        users.append(user)

    db.session.add_all(users)
    db.session.commit()

    print("Creating recipes...")
    recipes = []

    for _ in range(100):
        instructions = fake.paragraph(nb_sentences=8)

        while len(instructions.strip()) < 50:
            instructions = fake.paragraph(nb_sentences=10)

        recipe = Recipe(
            title=fake.sentence().rstrip("."),
            instructions=instructions,
            minutes_to_complete=randint(15, 90),
            user_id=rc(users).id 
        )
        recipes.append(recipe)

    db.session.add_all(recipes)
    db.session.commit()

    print("Done seeding!")