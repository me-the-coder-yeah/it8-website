from flask import Flask, send_file, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from flask_wtf import CSRFProtect
import flask_login
from functools import wraps
import math

Base = declarative_base()
class User(Base, flask_login.UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
#let's go
app = Flask(__name__)
engine = create_engine(f"postgresql://neondb_owner:npg_Pb7kfi0zaSmK@ep-shy-night-aq32kjx1-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require", echo=True)
SessionLocal = sessionmaker(bind=engine)
csrf = CSRFProtect(app)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'totally_secret'

with app.app_context():
    Base.metadata.create_all(engine)

@login_manager.user_loader
def load_user(user_id):
    session = SessionLocal()
    user = session.query(User).get(int(user_id))
    session.close()
    return user

def anonymous_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if flask_login.current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return route_function(*args, **kwargs)
    return wrapper


@app.route("/")
def homepage():
    return render_template('homepage.html')

@app.route("/login/sign-up", methods = ["GET","POST"])
@anonymous_required
def sign_up():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with SessionLocal() as session:
            try:
                new_user = User(
                    username=username,
                    password=generate_password_hash(password, method='scrypt', salt_length=10)
                )
                session.add(new_user)
                session.commit()
                flask_login.login_user(new_user)
                flash("user created!")
                return redirect(url_for("download_files"))
            except Exception:
                flash("user with the same username already exists, try logging in?")
                return redirect(url_for("sign_in"))
    return render_template("register.html")

@app.route("/login", methods = ["GET","POST"])
@anonymous_required
def sign_in():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with SessionLocal() as session:
            user = session.query(User).filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                flash("login success!")
                flask_login.login_user(user)
                return redirect(url_for("download_files"))
            elif user:
                flash("incorrect password")
                return redirect(url_for("sign_in"))
            else:
                flash("user does not exist")
                return redirect(url_for("sign_in"))
    return render_template('signin.html')

@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for("homepage"))

@app.route('/calculators')
@flask_login.login_required
def download_files():
    return render_template("select_calculator_page.html")

@app.route('/calculators/trigonometry')
@flask_login.login_required
def trig1():
    return render_template("trigonometry.html")

@app.route('/calculators/trigonometry/calculate-sin-and-cos', methods=["GET", "POST"])
@flask_login.login_required
def trig2():
    if request.method == "POST":
        try:
            result = math.cos(int(request.form.get("value")))
            return redirect(url_for("show_results", result=f"Cos/Sin({round(int(request.form.get("value")))})={result}"))
        except ValueError:
            flash("You did not input a number.")
    function = request.args.get("function")
    return render_template("calc-trig.html", function=function)


@app.route('/calculators/trigonometry/tan', methods=["GET", "POST"])
@flask_login.login_required
def tan():
    if request.method == "POST":
        x = int(request.form.get("sin"))
        y = int(request.form.get("cos"))
        result = x/y
        return redirect(url_for("show_results", result=f"Tan({x}/{y}) = {result}"))
    return render_template("calc-tan.html")

#redirects
@app.route('/calculators/trigonometry/sin')
@flask_login.login_required
def sine():
    return redirect(url_for("trig2", function="sin"))
@app.route('/calculators/trigonometry/cos')
@flask_login.login_required
def cosine():
    return redirect(url_for("trig2", function="cos"))


@app.route('/calculators/linear-interpolation', methods=["GET", "POST"])
@flask_login.login_required
def linear_interpolation():
    if request.method == "POST":
        try:
            x1 = int(request.form.get("x1"))
            x2 = int(request.form.get("x2"))
            y1 = int(request.form.get("y1"))
            y2 = int(request.form.get("y2"))
            x = int(request.form.get("x"))
            result = y1 + (x-x1) * ((y2-y1)/(x2-x1))
            return redirect(url_for("show_results", result=f"Y = {result}"))
        except Exception:
            flash("Your equation either includes division by zero or does not contain any data.")
            return redirect(url_for("linear_interpolation"))
    return render_template("linear_interpolation.html")


@app.route('/calculators/euclidean-calculator', methods=["GET", "POST"])
@flask_login.login_required
def euclidian_calculator():
    if request.method == "POST":
        fraction1 = int(request.form.get("fraction1"))
        fraction2 = int(request.form.get("fraction2"))
        a, b = fraction1, fraction2
        if fraction1 == fraction2:
            result = fraction1
        else:
            while fraction2 != 0:
                fraction1, fraction2 = fraction2, fraction1 % fraction2
            result = fraction1
        return redirect(url_for("show_results", result=f"The GCD (Greatest Common Divisor) is {result}. The fraction in its most simple form is {int(a/result)}/{int(b/result)}"))
    return render_template("euclidean.html")

@app.route('/calculators/results')
@flask_login.login_required
def show_results():
    result = request.args.get("result")
    return render_template("results.html", result=result)

@app.errorhandler(404)
def four_zero_four(error):
    flash("404, page not found. We've brought you back here.")
    return redirect(url_for('homepage'))

if __name__ == "__main__":
    app.run(debug=True)

#Renee WAS HERE!!!!!!!!!!!!MUHAHAHA 👈(ﾟヮﾟ👈)👈(ﾟヮﾟ👈)👈(ﾟヮﾟ👈)👈(ﾟヮﾟ👈)👈(ﾟヮﾟ👈)(❤️ ω ❤️)(❤️ ω ❤️)◉_◉◉_◉◉_◉◉_◉◉_◉◉_◉◉_◉◉_◉◉_◉◉_◉◉_◉◉_◉◉_◉◉_◉◉_◉◉_◉(*￣rǒ￣)(*￣rǒ￣)(*￣rǒ￣)(*￣rǒ￣)つ﹏⊂_(:з)∠)_(´ｰ∀ｰ`)(☆-ｖ-)(☆-ｖ-)(￣、￣)🎶😎😎😎😎😎😊😊😊😊😊🎈🎈🎈🎈🎈🎈🎈✨✨✨✨✨✨✨🧧🧧🧧🧧🧧🎀🎀🎀🎀🎀🎀🎀🎀🎀🎀🎀🎀🎀🎀🎀🎀🎀🎀🎀🎀👛👛👛👛👛👛👛👛👛👛❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️❣️
