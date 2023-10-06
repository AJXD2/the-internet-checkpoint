# --------------SETTINGS--------------

ADMIN_USERS = [
    {"username": "admin", "password": "admin"},
    {"username": "ajxd2", "password": "test"},
]


# --------------LIB--------------
import os

print("CHECKING LIBRARIES")
try:
    import flask, flask_sqlalchemy
except ImportError:
    print(
        "CANNOT FIND LIBRARIES. INSTALLING NOW USING `current enviroment (too lazy to add this)` PACKAGE MANAGER"
    )
    os.system("pip install Flask Flask-SQLAlchemy python-dotenv")
print("LIB CHECK DONE!")

# --------------DB--------------
from app import db, User, app, create_user

print("CREATING DB")
if not os.path.exists("instance"):
    os.mkdir("instance")
# Create DB/Clear previous records
with app.app_context():
    db.drop_all()
    db.create_all()

# --------------ADMIN USER SETUP--------------
print("Setting up admin accounts.")
with app.app_context():
    for index, user in enumerate(ADMIN_USERS):
        print(f"Creating user: `{user['username']}` ({index+1}/{len(ADMIN_USERS)})")
        create_user(user["username"], user["password"])
