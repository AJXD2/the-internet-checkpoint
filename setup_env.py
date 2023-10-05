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
from app import db, User, app

print("CREATING DB")
os.mkdir("instance")
# Create DB/Clear previous records
with app.app_context():
    db.drop_all()
    db.create_all()

# --------------ADMIN USER SETUP--------------
print("Setting up admin user. (username=admin, password=admin)")
with app.app_context():
    admin = User(username="admin", password="admin")
    db.session.add(admin)
    db.session.commit()
