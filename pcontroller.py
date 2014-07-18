from flask import Flask, render_template, redirect, request, flash, session, g
from pmodel import session as db_session
import pmodel
import time, datetime
from datetime import date

from flask.ext.bootstrap3 import Bootstrap
from flask.ext.login import LoginManager, login_required, logout_user, login_user, current_user

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


    existing= db_session.query(pmodel.Teacher).filter_by(email=email).first()

    if existing:
        flash("Email already in use", "error")
        return redirect("/login")

    user = pmodel.Teacher(first_name = first_name, last_name = last_name, email = email, password = password)
    pmodel.session.add(user)
    pmodel.session.commit()

    user_obj= db_session.query(pmodel.Teacher).filter_by(email=email).first()
    user_id = user_obj.id

    if password == confirm_password:
        print "Success"
        session["email"] = user.email
        session["password"] = user.password
        session["id"]= user_id
        login_user(user)

        return redirect("/class")
    else:
        flash("Your passwords don't match, please try again.")
        return redirect("/signup")


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
        login_user(user)
        return redirect(request.args.get("next") or "/class/%d" % user.id)

    else:
        flash("Login information incorrect, please try again.")
        return redirect("/login")

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")

@app.route("/class", methods=["GET"])
@login_required
def view_class():
    teacher= current_user
    students = pmodel.Student.query.filter_by(teacher_id=teacher.id).all()
    return render_template("class.html",  teacher= teacher, students=students)


#TODO- put students alpha by last name
#TODO= add option to remove/edit student

@app.route("/class", methods=["POST"])
@login_required
def add_student():

    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    nickname = request.form["nickname"]

    existing= db_session.query(pmodel.Student).filter_by(first_name=first_name, last_name=last_name, nickname=nickname).first()

    if existing:
        flash("A student with that name already exists in your class", "error")
        return redirect("/class")

    teacher_id = session["id"]

    student = pmodel.Student(first_name=first_name, last_name=last_name, nickname= nickname, teacher_id=teacher_id)

    pmodel.session.add(student)
    pmodel.session.commit()

    flash("You have successfully added " + "%s %s %s to your class!" % (student.first_name, student.last_name, student.nickname))
    return redirect("/class")

# @app.route("/student/<int:student_id>/delete", methods=["GET"])
# @login_required
# def delete_student(student_id):
#   student = pmodel.Student.query.filter_by(id=student_id).one()
#     db_session.delete(student)
#     db_session.commit()
#     flash("You have successfully deleted this student")
#     return_redirect("/class")


@app.route("/student/<int:student_id>", methods= ["GET"])
@login_required
def view_student(student_id):
    student = pmodel.Student.query.filter_by(id=student_id).one()
    goals = pmodel.Goal.query.filter_by(student_id=student_id).all()

    return render_template("student.html", student=student, goals=goals)

@app.route("/student/<int:student_id>", methods= ["POST"])
@login_required
def add_marker(student_id):
    #TODO- hook up datepicker to markers
    #TODO- add option to edit/remove markers
    #TODO- add option to edit/remove goals

    marker_text= request.form["marker_text"]
    raw_date=request.form["calendar"]
    marker_date= datetime.datetime.strptime(raw_date, "%Y-%m-%d")


    # now= int(round(time.time()))

    marker= pmodel.Marker (marker_date= marker_date, marker_text= marker_text, student_id= student_id)


    pmodel.session.add(marker)
    pmodel.session.commit()

    flash("Marker added.")
    return redirect("/markers/%d" % student_id)

@app.route("/markers/<int:student_id>", methods=["GET"])
@login_required
def view_marker(student_id):
    markers= pmodel.Marker.query.filter_by(student_id=student_id).all()
    student= pmodel.Student.query.filter_by(id=student_id).one()
    return render_template("markers.html", student=student, markers=markers, time=time.time())


@app.route("/student/<int:student_id>/goal/new", methods=["GET"])
@login_required
def new_goal(student_id):
    student = pmodel.Student.query.filter_by(id=student_id).one()
    return render_template('goal/new.html', student=student)

@app.route("/student/<int:student_id>/goal/create", methods=["POST"])
@login_required
def create_goal(student_id):
    student = pmodel.Student.query.filter_by(id=student_id).one()
    goal_name = request.form["goal_name"]
    now = int(round(time.time()))
    goal = pmodel.Goal(student_id=student_id, goal_name=goal_name, date_created=now)
    pmodel.session.add(goal)
    pmodel.session.commit()

    max_counter=int(request.form["max_counter"]) # max_counter is created in jQuery.
    for i in range(max_counter+1): #to ensure we get the last number, as range includes number up to but not including.
        try:
            type= request.form["type_%d" % i] # in jQuery we iterate through our list and name each type "type_x", with x being a number. The number lines up with the index.
            text= request.form["text_%d" % i] #ditto
        except: # in case someone randomly types a student number into the browser.
            continue
        sub_goal= pmodel.SubGoal(goal_id=goal.id, sub_goal_name=text, sub_goal_type=type)
        pmodel.session.add(sub_goal)
        pmodel.session.commit()

    return redirect("/student/%d" % student_id) #back to student page

@app.route("/goal/view/<int:student_id>/<int:goal_id>", methods=["GET"])
@login_required
def view_data_page(student_id, goal_id):
    print "yes, we are entering the function."
    student = pmodel.Student.query.filter_by(id=student_id).first()
    goal = pmodel.Goal.query.filter_by(student_id=student_id, id=goal_id).first()
    return render_template("goal/view.html", student=student, goal=goal)




if __name__=="__main__":
    app.run(debug= True)