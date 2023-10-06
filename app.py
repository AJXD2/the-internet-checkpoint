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

    return render_template("index.html", logged_in=logged_in, username=username)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            # Set a session variable to indicate the user is logged in
            session["user_id"] = user.id
            session["username"] = user.username
            session["logged_in"] = True
            flash("Login successful!", "success")
            return redirect(
                url_for("index")
            )  # Redirect to a dashboard page or some other page after login

        flash("Invalid username or password. Please try again.", "danger")

    return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        try:
            username = request.form.get("username")
            password = request.form.get("password")
            # try:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
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
    users = User.query.filter(User.username != "admin").all()

    return render_template("admin.html", users=users)


if __name__ == "__main__":
    db.init_app(app)

    app.run()
