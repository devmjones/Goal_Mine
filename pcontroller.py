from flask import Flask, render_template, redirect, request, flash, session, g
from pmodel import session as db_session
import pmodel

from flask.ext.bootstrap3 import Bootstrap
from flask.ext.login import LoginManager, login_required, logout_user, login_user

app = Flask(__name__)
app.secret_key = '\xfb\x1c\x9dJ&H\xe8\x83x\x84Q\xde\xfe:\xd6\xfc\x055M\xdf\x9a\xf7\x19\x17'

bootstrap = Bootstrap()
bootstrap.init_app(app)

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="/login"


@login_manager.user_loader
def load_user(user_id):
    try:
        return pmodel.Teacher.query.filter_by(id=int(user_id)).first()
    except:
        return None

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

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def process_login():
    email = request.form["inputEmail1"]
    print email
    password = request.form["inputPassword1"]
    print password

    user = db_session.query(pmodel.Teacher).filter_by(email=email, password=password).first()


    if user:
        session["email"] = user.email
        session["password"] = user.password
        session["id"] = user.id
        flash("Login Successful!")
        login_user(user)
        return redirect(request.args.get("next") or "/class")

    else:
        flash("Login information incorrect, please try again.")
        return redirect("/login")

#TODO- add "remove student"

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")

@app.route("/class", methods=["GET"])
@login_required
def view_class():
    students = pmodel.Student.query.filter_by(teacher_id=session["id"]).all()
    teacher = pmodel.Teacher.query.filter_by(id=session["id"]).first()
    return render_template("class.html",  teacher= teacher, students=students)


#TODO- put students in table, alpha by last name
#TODO= add option to remove/edit student

@app.route("/class", methods=["POST"])
@login_required
def add_student():

#TODO- error if student name and nickname already exist.

    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    nickname = request.form["nickname"]
    teacher_id = session["id"]

    student = pmodel.Student(first_name=first_name, last_name=last_name, nickname= nickname, teacher_id=teacher_id)

    pmodel.session.add(student)
    pmodel.session.commit()

    flash("You have successfully added " + "%s %s %s to your class!" % (student.first_name, student.last_name, student.nickname))
    return redirect("/class")

@app.route("/student/<int:student_id>", methods= ["GET"])
@login_required
def view_student(student_id):
    student= pmodel.Student.query.filter_by(id=student_id).one()
    goals= pmodel.Goal.query.filter_by(student_id=student_id).all()
    return render_template("student.html", student= student, goals=goals)


@app.route("/student/<int:student_id>", methods= ["POST"])
@login_required
def add_marker(student_id):
    #TODO- add calendar to marker field
    #TODO- add option to edit/remove markers
    #TODO- add option to edit/remove goals

    marker_text= request.form["marker_text"]

    now= int(round(time.time()))
    marker= pmodel.Marker (marker_date= now, marker_text= marker_text, student_id= student_id)


    pmodel.session.add(marker)
    pmodel.session.commit()

    flash("Marker added.")
    return redirect("/markers/%d" % student_id)

@app.route("/markers/<int:student_id>", methods=["GET"])
@login_required
def view_marker(student_id):
    markers= pmodel.Marker.query.filter_by(id=student_id).all()
    student= pmodel.Student.query.filter_by(id=student_id).one()
    return render_template("markers.html", student=student, markers=markers)


@app.route("/goals/<int:student_id>", methods=["POST"])
@login_required
def add_goals(student_id):
    student = pmodel.Student.query.filter_by(id=student_id).one()
    return render_template("goals.html", student=student)



if __name__=="__main__":
    app.run(debug= True)