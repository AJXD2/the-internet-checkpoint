from sqlalchemy import false
from sqlalchemy.exc import IntegrityError
from app import db, User, Message, app
import fire


class UserObj(object):
    def add(self, username: str, password: str, force: bool = False):
        try:
            with app.app_context():
                newuser = User(username=username, password=password)
                db.session.add(newuser)
                db.session.commit()
            print(f"Added user: `{username}` with password `{password}`")
        except IntegrityError as e:
            if force:
                with app.app_context():
                    olduser = User.query.filter_by(username=username).first()

                    if olduser is None:
                        print("An unknown error occoured")
                        return
                    db.session.delete(olduser)
                    db.session.commit()
                    db.session.add(newuser)
                    db.session.commit()
                print(f"The --force option was used. Overwrote `{username}`")
                return
            print(
                "Cannot create user. If you would like to force make a user use the --force"
            )

    def purge(self):
        ans = input("Are you sure? (y/n)>")

        if ans == "y":
            ans = True
        else:
            ans = False

        if ans:
            with app.app_context():
                users = User.query.all()
                for i in users:
                    db.session.delete(i)
                    db.session.commit()

        print("i suggest you rerun `setup_env.py`.")


class MessageObj(object):
    def clear(self):
        with app.app_context():
            messages = Message.query.all()
            for i in messages:
                db.session.delete(i)
                db.session.commit()


if __name__ == "__main__":
    fire.Fire({"user": UserObj, "message": MessageObj})
