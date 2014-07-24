from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
from datetime import datetime, date
from collections import Counter
import os

import os.path
db_exists = os.path.isfile('iepdata.db')
engine = create_engine("sqlite:///iepdata.db", echo = False)
session = scoped_session(sessionmaker(bind= engine,
                                      autocommit= False,
                                      autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key= True)
    first_name = Column(String (64), nullable = False)
    last_name = Column(String (64), nullable = False)
    email = Column(String(64), nullable = False)
    password = Column(String(64), nullable = False)

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

    id = Column(Integer, primary_key = True)
    first_name = Column(String (64), nullable=False)
    last_name = Column(String (64), nullable=False)
    nickname = Column(String(64), nullable=True)
    teacher_id = Column(Integer, ForeignKey('teachers.email'))

    teacher = relationship("Teacher", backref="students")

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    goal_name = Column(String, nullable=False)
    is_timed = Column(Boolean, nullable=False)

    student = relationship("Student", backref=backref("goals", order_by=id))

class Marker(Base):
    __tablename__ = "markers"

    id = Column(Integer, primary_key=True)
    marker_date = Column(DateTime, nullable =True)
    marker_text = Column(Text, nullable=True)
    student_id = Column(Integer, ForeignKey('students.id'))

    student = relationship("Student",  backref=backref("markers", order_by= id))

    def marker_date_as_datetime(self):
        return datetime.fromtimestamp(self.marker_date)

    @classmethod
    def get_marker_record(cls, start_date, end_date, student_id):
        marker_record= cls.query.filter(cls.marker_date >= start_date).filter(cls.marker_date <= end_date).filter_by(student_id=student_id).all()
        return cls.query (marker_record)


class SubGoalRawData(Base):
    __tablename__ = "sub_goal_raw_data"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    sub_goal_id = Column(Integer, ForeignKey('sub_goals.id'))
    sub_goal_type = Column(String(64), nullable=False)
    sub_goal_notes = Column(Text, nullable=True)
    sub_goal_data_value = Column(String, nullable=False)
    sub_goal_time = Column(Integer, nullable=True)

    sub_goal = relationship("SubGoal", backref = backref ("sub_goal_raw_data", order_by= id))

    @classmethod
    def get_report_data(cls, goal_id, start_date, end_date):
        sub_goal_data = {} # creating empty dict, keys will be sub goal ids, and the values the raw data objects associated with those sub goals.
        raw_data = cls.query.join(SubGoal)\
                      .filter(SubGoal.goal_id == goal_id)\
                      .filter(SubGoalRawData.date >= start_date)\
                      .filter(SubGoalRawData.date <= end_date)\
                      .order_by('sub_goal_id', 'date').all()
                   # use join when you need to filter by a field in an associated table, order by organizes them by specified columns.
        for item in raw_data: # result of db query (list of raw data objects)
            if item.sub_goal_id not in sub_goal_data: # use. because items are db objects.
                sub_goal_data[item.sub_goal_id]= [] # if sub_goal id not in dict, add as key with empty list as value.
            sub_goal_data[item.sub_goal_id].append(item)
        return sub_goal_data

    # @staticmethod
    # def print_report_data(report_data):
    #     for sub_goal_id in report_data:
    #         print "SUBGOAL %d (type %s)" % (sub_goal_id, report_data[sub_goal_id][0].sub_goal_type)
    #         for raw_data in report_data[sub_goal_id]:
    #             print " - DATA:"
    #             print "   id: %d" % (raw_data.id)
    #             print "   date: %s" % (raw_data.date)
    #             print "   sub_goal_id: %d" % (raw_data.sub_goal_id)
    #             print "   sub_goal_type: %s" % (raw_data.sub_goal_type)
    #             print "   sub_goal_notes: %s" % (raw_data.sub_goal_notes)
    #             print "   sub_goal_data_value: %s" % (raw_data.sub_goal_data_value)
    #             print "   sub_goal_time: %d" % (raw_data.sub_goal_time)

    @classmethod
    def summaries_for_report_data(cls, report_data):

        summaries = [] # will be a list of dictionaries from report data

        for sub_goal_id in report_data:

            summary = None #this will the the summary of one subgoal by subgoal id (all have same type)
            raw_data_item_list = report_data[sub_goal_id]
            first_item = raw_data_item_list[0]
            sub_goal_type = first_item.sub_goal_type

            if sub_goal_type == "tally":
                summary = cls.tally_summary(raw_data_item_list)
            elif sub_goal_type == "t/f":
                summary = cls.tf_summary(raw_data_item_list)
            elif sub_goal_type == "narrative":
                summary = cls.narrative_summary(raw_data_item_list)
            elif sub_goal_type == "range":
                summary = cls.range_summary(raw_data_item_list)

            summaries.append(summary)
        return summaries



    @staticmethod
    def tally_summary(raw_tally_items): #list of complete raw data objects of the tally type for that subgoal
        tally_info = {}
        if not raw_tally_items:
            return tally_info
        tally_info["type"] = "tally"
        tally_info["sub_goal_name"] = raw_tally_items[0].sub_goal.sub_goal_name #pulling the name of the subgoal out of the subgoal object that belongs to the first raw tally items object
        tally_info["count"] = len(raw_tally_items)
        tally_info["average"] = 0
        for item in raw_tally_items:
            tally_info["average"] += int(item.sub_goal_data_value)
            tally_info["average"] /= tally_info["count"]
        breakdown = {}
        for item in raw_tally_items:
            value = item.sub_goal_data_value
            if breakdown.get(value):
                breakdown[value] += 1
            else:
                breakdown[value] = 1
        tally_info["breakdown"] = breakdown
        return tally_info

    @staticmethod
    def narrative_summary(raw_narrative_items):
        narrative_info = {}
        if not raw_narrative_items:
            return narrative_info
        narrative_info["type"] = "narrative"
        narrative_info["sub_goal_name"] = raw_narrative_items[0].sub_goal.sub_goal_name
        narrative_info["count"] = len(raw_narrative_items)
        narrative_info["data_items"] = raw_narrative_items
        return narrative_info

    @staticmethod
    def tf_summary(raw_tf_items):
        tf_info = {}
        if not raw_tf_items:
            return tf_info
        tf_info["type"] = "tf"
        tf_info["sub_goal_name"] = raw_tf_items[0].sub_goal.sub_goal_name
        tf_info["count"] = len(raw_tf_items)
        breakdown = {}
        for item in raw_tf_items:
            value = item.sub_goal_data_value
            if breakdown.get(value):
                breakdown[value] += 1
            else:
                breakdown[value] = 1
        tf_info["breakdown"] = breakdown
        return tf_info

    @staticmethod
    def range_summary(raw_range_items):
        range_info = {}
        if not raw_range_items:
            return range_info
        range_info["type"] = "range"
        range_info["sub_goal_name"] = raw_range_items[0].sub_goal.sub_goal_name
        range_info["count"] = len(raw_range_items)
        breakdown = {}
        for item in raw_range_items:
            value = item.sub_goal_data_value
            if breakdown.get(value):
                breakdown[value] += 1
            else:
                breakdown[value] = 1
        range_info["breakdown"] = breakdown
        return range_info


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