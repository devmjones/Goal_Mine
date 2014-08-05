from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
from datetime import datetime, date, timedelta
from collections import Counter
from types import *
import os

import os.path

db_exists = os.path.isfile('iepdata.db')
engine = create_engine("sqlite:///iepdata.db", echo=False)
session = scoped_session(sessionmaker(bind=engine,
                                      autocommit=False,
                                      autoflush=False))

Base = declarative_base()
Base.query = session.query_property()


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    email = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    nickname = Column(String(64), nullable=True)
    teacher_id = Column(Integer, ForeignKey('teachers.email'))

    teacher = relationship("Teacher", backref="students")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    goal_name = Column(String, nullable=False)

    student = relationship("Student", backref=backref("goals", order_by=id))


class Marker(Base):
    __tablename__ = "markers"

    id = Column(Integer, primary_key=True)
    marker_date = Column(DateTime, nullable=True)
    marker_text = Column(Text, nullable=True)
    student_id = Column(Integer, ForeignKey('students.id'))

    student = relationship("Student", backref=backref("markers", order_by=id))

    def marker_date_as_datetime(self):
        return datetime.fromtimestamp(self.marker_date)

    @classmethod
    def get_marker_record(cls, start_date, end_date, student_id):
        marker_record = cls.query.filter(cls.marker_date >= start_date).filter(cls.marker_date <= end_date).filter_by(
            student_id=student_id).all()
        return marker_record


class SubGoalRawData(Base):
    __tablename__ = "sub_goal_raw_data"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    sub_goal_id = Column(Integer, ForeignKey('sub_goals.id'))
    sub_goal_type = Column(String(64), nullable=False)
    sub_goal_notes = Column(Text, nullable=True)
    sub_goal_data_value = Column(String, nullable=False)

    sub_goal = relationship("SubGoal", backref=backref("sub_goal_raw_data", order_by=id))

    def value_as_timedelta(self):
        return timedelta(seconds = int(self.sub_goal_data_value))

    @classmethod
    def get_report_data(cls, goal_id, start_date, end_date):
        report_data = {}  # creating empty dict, keys will be sub goal ids, and the values the raw data objects associated with those sub goals.
        raw_data = cls.query.join(SubGoal) \
            .filter(SubGoal.goal_id == goal_id) \
            .filter(SubGoalRawData.date >= start_date) \
            .filter(SubGoalRawData.date <= end_date) \
            .order_by('sub_goal_id', 'date').all()
        # use join when you need to filter by a field in an associated table, order by organizes them by specified columns.
        for item in raw_data:  # result of db query (list of raw data objects)
            if item.sub_goal_id not in report_data:  # use. because items are db objects.
                report_data[item.sub_goal_id] = []  # if sub_goal id not in dict, add as key with empty list as value.
            report_data[item.sub_goal_id].append(item)
        return report_data


    @classmethod
    def summaries_for_report_data(cls, report_data):

        summaries = []  # will be a list of dictionaries from report data

        for sub_goal_id in report_data:  # I am going to go through each set by sub goal id.

            summary = None  # this will the the summary of one subgoal by subgoal id (all have same type)
            raw_data_item_list = report_data[sub_goal_id]  # not in " " because it's an object. List of just the subgoal ids?
            first_item = raw_data_item_list[0]  # I am looking at the first item with each subgoal in the list of sub_goal ids
            sub_goal_type = first_item.sub_goal_type  # and checking it's subgoal type since it's an object

            # depending on subgoal type, the diffrent type methods will be called to create the type summary dictionaries, with raw_data_items_list being the parameter.

            if sub_goal_type == "tally":
                summary = cls.tally_summary(raw_data_item_list)  # each is a list of sub goal raw data objects
            elif sub_goal_type == "t/f":
                summary = cls.tf_summary(raw_data_item_list)
            elif sub_goal_type == "narrative":
                summary = cls.narrative_summary(raw_data_item_list)
            elif sub_goal_type == "range":
                summary = cls.range_summary(raw_data_item_list)
            elif sub_goal_type == "stopwatch":
                summary = cls.stopwatch_summary(raw_data_item_list)

            summaries.append(summary)
        return summaries


    @staticmethod
    def stopwatch_summary(raw_stopwatch_items):

        stopwatch_summary_info = {}
        if not raw_stopwatch_items:
            return stopwatch_summary_info
        stopwatch_summary_info["type"] = "stopwatch"
        stopwatch_summary_info["sub_goal_name"] = raw_stopwatch_items[0].sub_goal.sub_goal_name
        stopwatch_summary_info["data_items"] = raw_stopwatch_items

        stopwatch_summary_info["notes"] = []
        for item in raw_stopwatch_items:
            stopwatch_summary_info["notes"].append(str(item.sub_goal_notes))

        stopwatch_summary_info["count"] = len(raw_stopwatch_items)

        stopwatch_summary_info["average"] = 0
        for item in raw_stopwatch_items:
            stopwatch_summary_info["average"] += int(item.sub_goal_data_value)
        stopwatch_summary_info["average"] /= stopwatch_summary_info["count"]
        stopwatch_summary_info["average"] = timedelta(seconds=stopwatch_summary_info["average"])

        breakdown = {}
        for item in raw_stopwatch_items:
            value = timedelta(seconds=int(item.sub_goal_data_value))
            if breakdown.get(value):
                breakdown[value] += 1
            else:
                breakdown[value] = 1
        stopwatch_summary_info["breakdown"] = breakdown
        return stopwatch_summary_info


    @staticmethod
    def tally_summary(
            raw_tally_items):  # raw data item list. list of complete raw data objects of the tally type for that subgoal

        tally_summary_info = {}
        if not raw_tally_items:
            return tally_summary_info
        tally_summary_info["type"] = "tally"
        tally_summary_info["sub_goal_name"] = raw_tally_items[0].sub_goal.sub_goal_name  # pulling the name of the subgoal out of the subgoal object that belongs to the first raw tally items object
        tally_summary_info["data_items"] = raw_tally_items

        tally_summary_info["notes"] = []  # list of strings containing subgoal notes
        for item in raw_tally_items:
            tally_summary_info["notes"].append(str(item.sub_goal_notes))

        tally_summary_info["count"] = len(raw_tally_items)
        tally_summary_info["average"] = 0
        for item in raw_tally_items:
            tally_summary_info["average"] += int(item.sub_goal_data_value)
        tally_summary_info["average"] /= tally_summary_info["count"]

        breakdown = {}
        for item in raw_tally_items:
            value = int(item.sub_goal_data_value)
            if breakdown.get(value):
                breakdown[value] += 1
            else:
                breakdown[value] = 1
        tally_summary_info["breakdown"] = breakdown

        percentage = {}
        for value in breakdown:
            percentage[value] = (breakdown[value] / float(tally_summary_info["count"])) * 100.0
        tally_summary_info["percentage"] = percentage

        return tally_summary_info

    @staticmethod
    def narrative_summary(raw_narrative_items):

        narrative_summary_info = {}
        if not raw_narrative_items:
            return narrative_summary_info

        narrative_summary_info["type"] = "narrative"
        narrative_summary_info["sub_goal_name"] = raw_narrative_items[0].sub_goal.sub_goal_name
        narrative_summary_info["count"] = len(raw_narrative_items)
        narrative_summary_info["data_items"] = raw_narrative_items
        return narrative_summary_info

    @staticmethod
    def tf_summary(raw_tf_items):

        tf_summary_info = {}
        if not raw_tf_items:
            return tf_summary_info

        tf_summary_info["type"] = "tf"
        tf_summary_info["sub_goal_name"] = raw_tf_items[0].sub_goal.sub_goal_name
        tf_summary_info["data_items"] = raw_tf_items

        tf_summary_info["notes"] = []  # list of strings containng subgoal notes
        for item in raw_tf_items:
            tf_summary_info["notes"].append(str(item.sub_goal_notes))

        tf_summary_info["count"] = len(raw_tf_items)

        total_yes = 0
        total_no = 0

        for item in raw_tf_items:
            raw_value = str(item.sub_goal_data_value)
            (yes, no) = raw_value.split(":")
            total_yes += int(yes)
            total_no += int(no)

        percentage = {}
        percentage["yes"] = (float(total_yes) / float(total_yes + total_no)) * 100.0
        percentage["no"] = 100.0 - percentage["yes"]
        tf_summary_info["yes"] = total_yes
        tf_summary_info["no"] = total_no
        tf_summary_info["percentage"] = percentage

        return tf_summary_info

    @staticmethod
    def range_summary(raw_range_items):

        range_summary_info = {}

        if not raw_range_items:
            return range_summary_info
        range_summary_info["type"] = "range"
        range_summary_info["sub_goal_name"] = raw_range_items[0].sub_goal.sub_goal_name
        range_summary_info["data_items"] = raw_range_items

        range_summary_info["notes"] = []  # list of strings containng subgoal notes
        for item in raw_range_items:
            range_summary_info["notes"].append(str(item.sub_goal_notes))

        range_summary_info["count"] = len(raw_range_items)
        range_summary_info["average"] = 0
        for item in raw_range_items:
            range_summary_info["average"] += int(item.sub_goal_data_value)
        range_summary_info["average"] /= range_summary_info["count"]

        breakdown = {}
        for item in raw_range_items:
            value = int(item.sub_goal_data_value)
            if breakdown.get(value):
                breakdown[value] += 1
            else:
                breakdown[value] = 1
        range_summary_info["breakdown"] = breakdown

        percentage = {}
        for value in breakdown:
            percentage[value] = (breakdown[value] / float(range_summary_info["count"])) * 100.0
        range_summary_info["percentage"] = percentage

        return range_summary_info


class SubGoal(Base):
    __tablename__ = "sub_goals"

    id = Column(Integer, primary_key=True)
    goal_id = Column(Integer, ForeignKey('goals.id'))
    sub_goal_name = Column(String(64), nullable=False)
    sub_goal_type = Column(String(64), nullable=False)

    goal = relationship("Goal", backref=backref("sub_goals", order_by=id))


def connect():
    global engine
    global Session

    return Session()


def main():
    pass


if not db_exists:
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    main()