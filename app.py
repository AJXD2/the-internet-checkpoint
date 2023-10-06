from flask import (
    Flask,
    request,
    redirect,
    jsonify,
    render_template,
    session,
    url_for,
    flash,
)
from flask_sqlalchemy import SQLAlchemy
import os

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
import bcrypt

SALT = bcrypt.gensalt(rounds=12)


trustedusers = ["admin", "ajxd2", "truthparadox"]

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder="static")
app.config["SECRET_KEY"] = "f8ef945328094e22b6ae3045819ff4a5"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "instance", "dev.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    messages = db.relationship(
        "Message", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    # Establishing the one-to-many relationship with Message
    messages = db.relationship("Message", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def __str__(self):
        return f"<User {self.username}>"


class Message(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    body = db.Column(db.String(150), nullable=False)

    # Creating a foreign key to the User model
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


def create_user(username, password):
    hashed_password = bcrypt.hashpw(password.encode(), SALT)
    user = User(username=username, password=hashed_password)
    db.session.add(user)
    db.session.commit()


def login_user(username, password):
    user = User.query.filter_by(username=username).first()

    if user and bcrypt.checkpw(password.encode(), user.password):
        return user
    else:
        return None


@app.route("/")
def index():
    logged_in = False
    username = None
    if "user_id" in session:
        logged_in = True
        # User is signed in, do something
        user_id = session["user_id"]
        user = User.query.get(user_id)
        if user:
            username = user.username

    messages = Message.query.all()

    return render_template(
        "index.html",
        logged_in=logged_in,
        username=username,
        messages=messages,
        trustedusers=trustedusers,
    )


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = login_user(username, password)
        if user is not None:
            # Set a session variable to indicate the user is logged in
            session["user_id"] = user.id
            session["username"] = user.username
            session["logged_in"] = True
            flash("Login successful!", "success")
            return redirect(
                url_for("index")
            )  # Redirect to a dashboard page or some other page after login

        flash("Invalid username or password. Please try again.", "danger")
        return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        try:
            username = request.form.get("username")
            password = request.form.get("password")
            # try:
            create_user(username, password)
            redirect(url_for("index"))
        except IntegrityError:
            flash("User Exists", "error")
            return redirect(url_for("register"))
    return render_template("signup.html")


@app.route("/logout")
def logout():
    flash("Logged out!", "info")
    session.pop("user_id", None)
    session.pop("logged_in", None)
    session.pop("username", None)
    return redirect(url_for("index"))


@app.route("/users/<int:user_id>/delete", methods=["POST", "GET"])
def delete_user(user_id):
    if session.get("username") not in trustedusers:
        return "<h1>Unauthorized</h1> <a href='/'>Home</a>", 401

    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        # Delete associated messages
        Message.query.filter_by(user_id=user_id).delete()

        db.session.delete(user)
        db.session.commit()

        flash("User and associated messages deleted successfully", "success")
        return redirect(url_for("admin"))

    return render_template("delete_user.html", user=user)


@app.route("/admin")
def admin():
    if session.get("username") not in trustedusers:
        return "<h1>Unauthorized</h1> <a href='/'>Home</a>", 401
    users = User.query.filter(
        User.username != "admin", User.username != session.get("username")
    ).all()

    return render_template("admin.html", users=users)


@app.route("/post_message", methods=["POST"])
def post_message():
    if "user_id" in session:
        user_id = session["user_id"]
        message_body = request.form.get("message")

        user = User.query.filter_by(id=user_id).first()
        if user is None:
            flash(
                "You are using an expired account. We logged you out for security pourposes."
            )
            return redirect(url_for("logout"))
        if len(user.messages) > 0 and user.username not in trustedusers:
            flash("Error: You have reached the max amount of messages.")
            return redirect(url_for("index"))

        new_message = Message(body=message_body, user_id=user_id)
        db.session.add(new_message)
        db.session.commit()

    return redirect(url_for("index"))


if __name__ == "__main__":
    db.init_app(app)

    app.run()
