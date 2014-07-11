from flask import Flask, render_template, redirect, request, flash, session,g
from pmodel import session as db_session
import pmodel
from flask.ext.bootstrap3 import Bootstrap

app = Flask(__name__)
app.secret_key = "blahblah"

#TODO- need actual secret key

bootstrap = Bootstrap()
bootstrap.init_app(app)

#TODO- use this type of stuff or Flask Login package
# @app.teardown_request
# def shutdown_session(exception = None):
#     db_session.remove()

# @app.before_request
# def load_user_id():
#     g.user_id = session.get('user_id')

# @app.route("/")
# def index():
#     if g.user_id:
#         return redirect(url_for("display_search"))
#     return render_template("index.html")

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
#TODO- Clear session when user logs out

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

#TODO- add "remove student"

@app.route("/class", methods= ["GET"])
def view_class():
    students = pmodel.Student.query.filter_by(teacher_id = session["id"]).all()
    return render_template("class.html",  students=students)

#TODO- add optional nickname field

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

@app.route("/student/<int:student_id>", methods= ["GET"])
def view_student(student_id):
    student= pmodel.Student.query.filter_by(id=student_id).one()
    print student
    goals= pmodel.Goal.query.filter_by(student_id=student_id).all()
    return render_template("student.html", student= student, goals=goals)



if __name__=="__main__":
    app.run(debug= True)