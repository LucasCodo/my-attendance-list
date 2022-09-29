from peewee import *
from datetime import datetime
from enum import Enum
import os


class LicenseType(Enum):
    Free = "free"
    Monthly = "monthly"
    Yearly = "yearly"


db_name = os.getenv("db_name")
user = os.getenv("db_user")
password = os.getenv("db_password")
host = os.getenv("db_host")
port = int(os.getenv("db_port"))

pg_db = PostgresqlDatabase(db_name, user=user, password=password,
                           host=host, port=port)


class BaseModel(Model):
    class Meta:
        database = pg_db


class Student(BaseModel):
    name = TextField()
    email = TextField()
    password = TextField()
    registration_number = TextField(null=True)  # matricula


class StudentList(BaseModel):
    student = ForeignKeyField(Student, backref='Students')
    description = TextField(null=True)
    time_stamp = DateTimeField(default=datetime.now)


class License(BaseModel):
    type = TextField(default=LicenseType.Free)
    start_date = DateTimeField(default=datetime.now)
    end_date = DateTimeField(null=True)
    is_active = BooleanField(default=True)


class Teacher(BaseModel):
    name = TextField()
    email = TextField()
    password = TextField()


class TeacherList(BaseModel):
    teacher = ForeignKeyField(Teacher, backref='listTeachers')
    description = TextField(null=True)


class Course(BaseModel):
    name = TextField()
    students = ForeignKeyField(StudentList, backref='courses', null=True)
    teacher = ForeignKeyField(Teacher, backref='courses', null=True)


class CourseList(BaseModel):
    course = ForeignKeyField(Course, backref='listCourses')
    description = TextField(null=True)


class Organization(BaseModel):
    name = TextField()
    email = TextField()
    password = TextField()
    teachers = ForeignKeyField(TeacherList, backref='organizations', null=True)
    courses = ForeignKeyField(CourseList, backref='organizations', null=True)


class AttendanceList(BaseModel):
    date = DateTimeField()
    studentList = ForeignKeyField(StudentList, backref='AttendanceLists')
    description = TextField(null=True)


pg_db.create_tables([Student,
                     StudentList,
                     License,
                     Teacher,
                     TeacherList,
                     Course,
                     CourseList,
                     Organization,
                     AttendanceList])

"""
data = [
    {'name': 'lucas', 'email': 'lucas@email.com', 'password': 'senha',
     'registration_number': '123'},
    {'name': 'pedro', 'email': 'pedro@email.com', 'password': 'senha',
     'registration_number': '234'},
    {'name': 'joão', 'email': 'joao@email.com', 'password': 'senha',
     'registration_number': '345'},
    {'name': 'maria', 'email': 'maria@email.com', 'password': 'senha',
     'registration_number': '456'},
    {'name': 'paula', 'email': 'paula@email.com', 'password': 'senha',
     'registration_number': '567'},
    {'name': 'ana', 'email': 'ana@email.com', 'password': 'senha',
     'registration_number': '678'}
]
with pg_db.atomic():
    query = Student.insert_many(data)
    query.execute()

data = [
    {'name': 'raimundo', 'email': 'raimundo@email.com', 'password': 'senha'},
    {'name': 'juliana', 'email': 'juliana@email.com', 'password': 'senha'},
    {'name': 'romulo', 'email': 'romulo@email.com', 'password': 'senha'}
]
with pg_db.atomic():
    query = Teacher.insert_many(data)
    query.execute()

data = [
    {'name': 'Curso X', 'teacher': 1},
    {'name': 'Disciplina Y', 'teacher': 2},
    {'name': 'Materia Z', 'teacher': 3}
]
with pg_db.atomic():
    query = Course.insert_many(data)
    query.execute()

data = [
    {'course_id': 1, 'student_id': 1},
    {'course_id': 1, 'student_id': 2},
    {'course_id': 1, 'student_id': 3},
    {'course_id': 2, 'student_id': 4},
    {'course_id': 2, 'student_id': 5},
    {'course_id': 3, 'student_id': 6},
]
with pg_db.atomic():
    query = StudentCourse.insert_many(data)
    query.execute()

query = (Student
         .select()
         .join(StudentCourse)
         .join(Course)
         .where(Course.name == 'Curso X'))
for student in query:
    print(student.name)
"""
