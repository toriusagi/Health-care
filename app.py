import streamlit as st
from enum import unique #列挙unique
from flask import Flask #web module
from flask import render_template, request, redirect #file use request, redirect
from flask_sqlalchemy import SQLAlchemy #python sql use
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, date #datetime get
import pytz

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///health_care.db"
app.config["SECRET_KEY"] = os.urandom(24)
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_at = db.Column(db.Date, nullable=False, default=date.today()) #作成日時
    bedtime = db.Column(db.String(6), nullable=False) #就寝時間
    wake_up = db.Column(db.String(6), nullable=False) #起床時間
    time_of_sleeping = db.Column(db.String(6), nullable=False) #睡眠時間
    weight = db.Column(db.String(4), nullable=False) #体重
    morning = db.Column(db.Integer, nullable=False) #朝の体調１～５
    noon = db.Column(db.Integer, nullable=False) #昼の体調１～５
    evening = db.Column(db.Integer, nullable=False) #夕の体調１～５
    comment = db.Column(db.String(300), nullable=False) #コメント

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(12))
    
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "GET":
        posts = Post.query.all()
        return render_template("index.html", posts=posts)

@app.route("/create", methods=["GET","POST"])
@login_required
def create():
    if request.method == "POST":
        create_at = request.form.get("create_at")
        bedtime = request.form.get("bedtime")
        wake_up = request.form.get("wake_up")
        time_of_sleeping = request.form.get("time_of_sleeping")
        weight = request.form.get("weight")
        morning = request.form.get("morning")
        noon = request.form.get("noon")
        evening = request.form.get("evening")
        comment = request.form.get("comment")

        post = Post(create_at=create_at,bedtime=bedtime,wake_up=wake_up,time_of_sleeping=time_of_sleeping,weight=weight,morning=morning,noon=noon,evening=evening,comment=comment)

        db.session.add(post)
        db.session.commit()
        return redirect("/")
    else:
        return render_template("create.html")

@app.route("/edit", methods=["GET","POST"])
@login_required
def edit():
    if request.method == "GET":
        posts = Post.query.all()
        return render_template("edit.html", posts=posts)

@app.route("/<int:id>/update", methods=["GET", "POST"])
@login_required
def update(id):
        post = Post.query.get(id)
        if request.method == "GET":
            return render_template("update.html", post=post)
        else:
            post.create_at = request.form.get("create_at")
            post.bedtime = request.form.get("bedtime")
            post.wake_up = request.form.get("wake_up")
            post.time_of_sleeping = request.form.get("time_of_sleeping")
            post.weight = request.form.get("weight")
            post.morning = request.form.get("morning")
            post.noon = request.form.get("noon")
            post.evening = request.form.get("evening")
            post.comment = request.form.get("comment")

            post.create_at = datetime.strptime(post.create_at, '%Y-%m-%d')

            db.session.commit()
            return redirect("/edit")
    
@app.route("/<int:id>/delete", methods=["GET"])
@login_required
def delete(id):
        post = Post.query.get(id)
        
        db.session.delete(post)
        db.session.commit()
        return redirect("/")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User(username=username,password=generate_password_hash(password, method="sha256"))

        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    else:
        return render_template("signup.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

if __name__ == '__main__':
    app.run()