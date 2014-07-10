from flask import Flask, render_template, redirect, request, flash, session
from pmodel import session as db_session
import pmodel
from flask.ext.bootstrap3 import Bootstrap
import uuid

app = Flask(__name__)
app.secret_key = "blahblah"

#TODO- need actual secret key

bootstrap = Bootstrap()
bootstrap.init_app(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup")
def show_signup():
    return render_template("signup.html")

@app.route("/signup", methods = ["POST"])
def process_signup():
   
    first_name = request.form["first_name"]
    last_name =request.form["last_name"]
    email = request.form["email"]
    password = request.form["password"]
    confirm_password = request.form["re-enter password"]

    user = pmodel.Teacher(first_name = first_name, last_name = last_name, email = email, password = password)
    pmodel.session.add(user)
    pmodel.session.commit()


    if password == confirm_password:
        flash("You have successfully signed up!")
        return redirect("/login")
    else:
        flash("Your passwords don't match, please try again.")
        return redirect("/signup")


#TODO- check to see if email already exists
#TODO- Add log out

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def process_login():
    email = request.form["inputEmail1"]
    password = request.form["inputPassword1"]

    user = db_session.query(pmodel.Teacher).filter_by(email=email, password=password).first()

    if user:
        session["email"] = user.email
        session["password"] = user.password
        session["id"] = user.id
        flash("Login Successful!")
        return redirect("/class")

    else:
        flash("Login information incorrect, please try again.")
        return redirect("/login")

@app.route("/class", methods= ["GET"])
def view_class():
    students = pmodel.Student.query.filter_by(teacher_id = session["id"]).all()
    return render_template("class.html",  students=students)

@app.route("/class", methods= ["POST"])
def add_student():

    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    teacher_id=session["id"]

    student = pmodel.Student(first_name = first_name, last_name = last_name, teacher_id = teacher_id)

    pmodel.session.add(student)
    pmodel.session.commit()

    flash("You have sucessfully added " + "%s %s to your class!" %(student.first_name, student.last_name))
    return redirect("/class")









if __name__=="__main__":
    app.run(debug= True)