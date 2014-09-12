from flask import Flask, render_template, redirect, request, flash, session, g
from pmodel import session as db_session
import pmodel
import time, datetime
from datetime import date, timedelta

from flask.ext.bootstrap3 import Bootstrap
from flask.ext.login import LoginManager, login_required, logout_user, login_user, current_user

app = Flask(__name__)
app.secret_key = '\xfb\x1c\x9dJ&H\xe8\x83x\x84Q\xde\xfe:\xd6\xfc\x055M\xdf\x9a\xf7\x19\x17' # redo and hide from view before deploying

bootstrap = Bootstrap()
bootstrap.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"


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


@app.route("/signup", methods=["POST"])
def process_signup():
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    email = request.form["email"]
    password = request.form["password"]
    confirm_password = request.form["re-enter password"]

    existing = db_session.query(pmodel.Teacher).filter_by(email=email).first()

    if existing:
        flash("Email already in use", "error")
        return redirect("/login")

    user = pmodel.Teacher(first_name=first_name, last_name=last_name, email=email, password=password)
    pmodel.session.add(user)
    pmodel.session.commit()

    user_obj = db_session.query(pmodel.Teacher).filter_by(email=email).first()
    user_id = user_obj.id

    if password == confirm_password:
        print "Success"
        session["email"] = user.email
        session["password"] = user.password
        session["id"] = user_id
        login_user(user)

        return redirect("/class")
    else:
        flash("Your passwords don't match, please try again.", "error")
        return redirect("/signup")


@app.route("/login", methods=["GET"])
def login():
    logout_user()
    session.clear()
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
        flash("Login Successful!", "success")
        login_user(user)
        return redirect(request.args.get("next") or "/class")

    else:
        flash("Login information incorrect, please try again.", "error")
        return redirect("/login")


@app.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect("/login")


@app.route("/class", methods=["GET"])
@login_required
def view_class():
    teacher = current_user
    students = pmodel.Student.query.filter_by(teacher_id=teacher.id).all()
    return render_template("class.html", teacher=teacher, students=students)


#TODO= hook up buttons to remove student

@app.route("/class", methods=["POST"])
@login_required
def add_student():
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    nickname = request.form["nickname"]

    existing = db_session.query(pmodel.Student).filter_by(first_name=first_name, last_name=last_name,
                                                          nickname=nickname).first()

    if existing:
        flash("A student with that name already exists in your class", "error")
        return redirect("/class")

    teacher_id = session["id"]

    student = pmodel.Student(first_name=first_name, last_name=last_name, nickname=nickname, teacher_id=teacher_id)

    pmodel.session.add(student)
    pmodel.session.commit()

    flash("You have successfully added " + "%s %s %s to your class!" "success" % (
    student.first_name, student.last_name, student.nickname))
    return redirect("/class")


@app.route("/student/<int:student_id>/delete", methods=["GET"])
@login_required
def delete_student(student_id):
    student = pmodel.Student.query.filter_by(id=student_id).one()
    db_session.delete(student)
    db_session.commit()
    flash("You have successfully deleted this student")
    return redirect("/class")


@app.route("/student/<int:student_id>", methods=["GET"])
@login_required
def view_student(student_id):
    student = pmodel.Student.query.filter_by(id=student_id).one()
    goals = pmodel.Goal.query.filter_by(student_id=student_id).all()
    #TODO- hook up buttons to edit/remove goals

    return render_template("student.html", student=student, goals=goals)


@app.route("/student/<int:student_id>", methods=["POST"])
@login_required
def add_marker(student_id):
    #TODO- add option to edit/remove markers

    marker_text = request.form["marker_text"]
    raw_date = request.form["calendar"]
    marker_date = datetime.datetime.strptime(raw_date, "%Y-%m-%d")

    marker = pmodel.Marker(marker_date=marker_date, marker_text=marker_text, student_id=student_id)

    pmodel.session.add(marker)
    pmodel.session.commit()

    flash("Marker added.", "success")
    return redirect("/markers/%d" % student_id)


@app.route("/markers/<int:student_id>", methods=["GET"])
@login_required
def view_marker(student_id):
    markers = pmodel.Marker.query.filter_by(student_id=student_id).all()
    student = pmodel.Student.query.filter_by(id=student_id).one()
    return render_template("markers.html", student=student, markers=markers, time=time.time())


#TODO- fix flow of app routes starting here.

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

    goal = pmodel.Goal(student_id=student_id, goal_name=goal_name)
    pmodel.session.add(goal)
    pmodel.session.commit()

    max_counter = int(request.form["max_counter"])  # max_counter is created in jQuery.
    for i in range(
                    max_counter + 1):
        try:
            type = request.form[
                "type_%d" % i]
            text = request.form["text_%d" % i]
        except:
            continue
        sub_goal = pmodel.SubGoal(goal_id=goal.id, sub_goal_name=text, sub_goal_type=type)
        pmodel.session.add(sub_goal)
        pmodel.session.commit()

    return redirect("/student/%d" % student_id)

# @app.route("/student/<int:student_id>/<int;goal_id>/delete", methods=["GET"])
# @login_required
# def delete_goal(goal_id):
#     goal = pmodel.Goal.query.filter_by(id=goal_id).one()
#     db_session.delete(goal)
#     db_session.commit()
#     flash("You have successfully deleted this goal")
#     return redirect("/student/%d" % student.id)


@app.route("/goal/view/<int:student_id>/<int:goal_id>", methods=["GET"])
@login_required
def view_data_page(student_id, goal_id):
    student = pmodel.Student.query.filter_by(id=student_id).first()
    goal = pmodel.Goal.query.filter_by(student_id=student_id, id=goal_id).first()
    return render_template("goal/view.html", student=student, goal=goal)


@app.route("/student/<int:student_id>/goal/<int:goal_id>/record", methods=["POST"])
@login_required
def submit_data(student_id, goal_id):
    student = pmodel.Student.query.filter_by(id=student_id).first()
    sub_goals = pmodel.SubGoal.query.filter_by(goal_id=goal_id).all()
    sub_goal_data_value = None
    now = datetime.datetime.now()

    for sub_goal in sub_goals:
        if sub_goal.sub_goal_type == "tally":
            sub_goal_data_value = request.form["tally_%d" % sub_goal.id]
            sub_goal_notes = request.form["notes_%d" % sub_goal.id]

        elif sub_goal.sub_goal_type == "t/f":
            sub_goal_yes_data_value = request.form["yes_%d" % sub_goal.id]
            sub_goal_no_data_value = request.form["no_%d" % sub_goal.id]
            sub_goal_data_value = sub_goal_yes_data_value + ":" + sub_goal_no_data_value
            sub_goal_notes = request.form["notes_%d" % sub_goal.id]

        elif sub_goal.sub_goal_type == "narrative":
            sub_goal_data_value = request.form["narrative_text_%d" % sub_goal.id]
            sub_goal_notes = None

        elif sub_goal.sub_goal_type == "range":
            sub_goal_data_value = request.form["range_%d" % sub_goal.id]
            sub_goal_notes = request.form["notes_%d" % sub_goal.id]

        elif sub_goal.sub_goal_type == "stopwatch":
            sub_goal_data_value = request.form["stopwatch_%d" % sub_goal.id]
            sub_goal_notes = request.form["notes_%d" % sub_goal.id]

        sub_goal_raw_data = pmodel.SubGoalRawData(date=now, sub_goal_id=sub_goal.id,
                                                  sub_goal_type=sub_goal.sub_goal_type,
                                                  sub_goal_notes=sub_goal_notes,
                                                  sub_goal_data_value=sub_goal_data_value)

        pmodel.session.add(sub_goal_raw_data)
        pmodel.session.commit()

    flash("Data instance entered", "success")
    return redirect("/student/%d" % student.id)


@app.route("/goal/report/<int:student_id>/<int:goal_id>", methods=["GET", "POST"])
@login_required
def view_goal_report(student_id, goal_id):
    student = pmodel.Student.query.filter_by(id=student_id).first()
    goal = pmodel.Goal.query.filter_by(student_id=student_id, id=goal_id).first()
    markers = pmodel.Marker.query.filter_by(student_id=student_id).all()

    if "start_date" in request.form and "end_date" in request.form:  # keys are always in strings
        sd = request.form["start_date"]
        start_date = datetime.datetime.strptime(sd, "%Y-%m-%d")
        ed = request.form["end_date"]
        end_date = datetime.datetime.strptime(ed + 'T23:59:59.999999', "%Y-%m-%dT%H:%M:%S.%f")
        report_data = pmodel.SubGoalRawData.get_report_data(goal_id, start_date, end_date)
        summaries = pmodel.SubGoalRawData.summaries_for_report_data(report_data)
        marker_data = pmodel.Marker.get_marker_record(start_date, end_date, student_id)
        return render_template("report.html", student_id=student_id, goal_id=goal_id, start_date=start_date,
                               end_date=end_date, student=student, goal=goal, summaries=summaries, markers=markers,
                               marker_data=marker_data)
    else:
        return render_template("report.html", student_id=student_id, goal_id=goal_id, student=student, goal=goal)


if __name__ == "__main__":
    app.run(debug=True)