from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
from datetime import datetime
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
    __tablename__= "teachers"

    id = Column (Integer, primary_key= True)
    first_name = Column (String (64), nullable = False)
    last_name = Column (String (64), nullable = False)
    email = Column (String(64), nullable = False)
    password = Column (String(64), nullable = False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)



class Student(Base):
    __tablename__= "students"

    id =  Column(Integer, primary_key = True)
    first_name = Column(String (64), nullable = False)
    last_name = Column(String (64), nullable = False)
    nickname = Column(String(64), nullable = True)
    teacher_id = Column(Integer, ForeignKey ('teachers.email'))

    teacher = relationship("Teacher", backref = "students")

class Goal(Base):
    __tablename__ = "goals"

    id = Column (Integer, primary_key = True)
    student_id = Column (Integer, ForeignKey ('students.id'))
    goal_name = Column (String, nullable = False)
    date_created = Column (Integer, nullable = False)

    student = relationship("Student", backref= backref ("goals", order_by= id))

class Marker(Base):
    __tablename__ = "markers"

    id = Column (Integer, primary_key = True)
    marker_date = Column (Integer, nullable = True)
    marker_text = Column (Text, nullable = True)
    student_id = Column (Integer, ForeignKey ('students.id'))

    student= relationship("Student",  backref= backref ("markers", order_by= id))

    def marker_date_as_datetime(self):
        return datetime.fromtimestamp(self.marker_date)


class SubGoalRawData(Base):
    __tablename__= "sub_goal_raw_data"

    id = Column (Integer, primary_key = True)
    date = Column (Integer, nullable = False)
    sub_goal_id = Column (Integer, ForeignKey ('sub_goals.id'))
    sub_goal_type = Column (String(64), nullable = False)
    sub_goal_notes = Column (Text, nullable = True)
    sub_goal_data_value= Column (String, nullable = False)
    sub_goal_time = Column (Integer, nullable= True)

    sub_goal = relationship("SubGoal", backref = backref ("sub_goal_raw_data", order_by= id))


class SubGoal(Base):
    __tablename__ = "sub_goals"

    id = Column (Integer, primary_key= True)
    goal_id = Column (Integer, ForeignKey ('goals.id'))
    sub_goal_name = Column (String(64), nullable = False)
    sub_goal_type = Column (String(64), nullable = False)

    goal = relationship("Goal", backref= backref ("sub_goals", order_by= id))


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