from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Text
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref

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


class Student(Base):
    __tablename__= "students"

    id =  Column (Integer, primary_key = True)
    first_name = Column (String (64), nullable = False)
    last_name = Column (String (64), nullable = False)
    teacher_id = Column (Integer, ForeignKey ('teachers.email'))

    teacher = relationship("Teacher", backref = "students")
    #teacher = relationship("Teacher")

class Goal(Base):
    __tablename__ = "goals"

    id = Column (Integer, primary_key = True)
    student_id = Column (Integer, ForeignKey ('students.id'))
    goal_name = Column (String, nullable = False)
    goal_type = Column (String(64), nullable = False)
    date_created = Column (DateTime, nullable = False)

    student = relationship("Student", backref= backref ("goals", order_by= id))

class Markers(Base):
    __tablename__ = "markers"

    id = Column (Integer, primary_key = True)
    date_created = Column (DateTime, nullable = True)
    text = Column (Text, nullable = True)
    student_id = Column (Integer, ForeignKey ('students.id'))

    student= relationship("Student",  backref= backref ("markers", order_by= id))

class RawData(Base):
    __tablename__= "raw_data"

    id = Column (Integer, primary_key = True)
    date = Column (DateTime, nullable = False)
    goal_id = Column (Integer, ForeignKey ('goals.id'))
    sub_goal_id = Column (Integer, ForeignKey ('sub_goals.id'))
    #sub_goal_name = Column (String(64), ForeignKey ('sub_goals.sub_goal_name'))
    sub_goal_notes = Column (Text, nullable = True)
    #sub_goal_type = Column (String(64), ForeignKey ('sub_goals.sub_goal_type'))
    sg_type_tally = Column (Integer, nullable = True)
    sg_type_tf = Column (Boolean, nullable = True)
    sg_type_range = Column (Integer, nullable = True)
    sg_type_narrative = Column (Text, nullable = True)

    goal = relationship("Goal", backref= backref ("raw_data", order_by= id))
    sub_goal = relationship("SubGoal", backref = backref ("raw_data", order_by= id))


class SubGoal(Base):
    __tablename__ = "sub_goals"

    id = Column (Integer, primary_key= True)
    goal_id = Column (Integer, ForeignKey ('goals.id'))
    sub_goal_name = Column (String(64), nullable = False)
    sub_goal_type = Column (String(64), nullable = False)

    goal = relationship("Goal", backref= backref ("sub_goals", order_by= id))
### End class declarations

def connect():
    global engine
    global Session

    return Session()


def main():
    pass
    

if __name__ == "__main__":
    main()