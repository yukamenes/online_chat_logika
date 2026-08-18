from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os

import settings
import db_scripts

app = Flask(__name__)
app.config["SECRET_KEY"] = settings.SECRET_KEY

db_scripts.create_tables()


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db_scripts.get_user_by_id(user_id)


@app.route("/")
@app.route("/index")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = get_current_user()
    posts = db_scripts.get_posts()
    return render_template("index.html", user=user, posts=posts)


@app.route("/about")
def about():
    user = get_current_user()
    return render_template("about.html", user=user)


@app.route("/add_post", methods=["GET", "POST"])
def add_post():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        text = request.form.get("text", "").strip()
        category = request.form.get("category", "")
        image = request.files.get("image")

        if image is None or image.filename == "" or title == "" or text == "" or category == "":
            return "Заповніть усі поля"

        filename = secure_filename(image.filename)
        upload_dir = os.path.join(app.root_path, "static", "images", "posts")
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        image.save(filepath)

        db_scripts.add_post(session["user_id"], category, title, text, filename)
        return redirect(url_for("index"))

    user = get_current_user()
    categories = db_scripts.get_categories()
    return render_template("add_post.html", user=user, categories=categories)


@app.route("/delete_post/<int:post_id>")
def delete_post(post_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    post = db_scripts.get_post_by_id(post_id)
    if post is None:
        return redirect(url_for("index"))

    if post["user_id"] != session["user_id"]:
        return redirect(url_for("index"))

    db_scripts.delete_post(post_id)
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        login_value = request.form.get("login", "")
        user = db_scripts.get_user_by_login(login_value)
        if user is None:
            return render_template("login.html", error="Користувача не знайдено!")

        password = request.form.get("password", "")
        if user[4] != password:
            return render_template("login.html", error="Неправильний пароль!")

        session["user_id"] = user[0]
        session["user_name"] = user[1]
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        login_value = request.form.get("login", "").strip()
        password = request.form.get("password", "").strip()

        if not name or not login_value or not password:
            return render_template("login.html", register_error="Заповніть усі поля")

        if db_scripts.get_user_by_login(login_value) is not None:
            return render_template("login.html", register_error="Користувач з таким логіном вже існує")

        db_scripts.add_user(name, login_value, password)
        user = db_scripts.get_user_by_login(login_value)
        session["user_id"] = user[0]
        session["user_name"] = user[1]
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
