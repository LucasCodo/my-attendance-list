from peewee import *
from datetime import datetime
from enum import Enum
import os
from typing import List


class LicenseType(Enum):
    Free = "free"
    Monthly = "monthly"
    Yearly = "yearly"


class TransactionType(Enum):
    Bitcoin = "bitcoin"
    Lightning = "lightning"
    CreditCard = "credit"


db_name = os.getenv("db_name")
user = os.getenv("db_user")
password = os.getenv("db_password")
host = os.getenv("db_host")
port = int(os.getenv("db_port"))

pg_db = PostgresqlDatabase(db_name, user=user, password=password,
                           host=host, port=port)


class BaseModel(Model):
    time_stamp = DateTimeField(default=datetime.now, null=True)

    class Meta:
        database = pg_db


class UserModel(BaseModel):
    username = TextField(unique=True)
    full_name = TextField()
    email = TextField(unique=True)
    hashed_password = TextField()
    disabled = BooleanField(default=False, null=True)


class License(BaseModel):  # Licença de uso do Serviço
    type = TextField(default=LicenseType.Free)
    start_date = DateTimeField(default=datetime.now)
    end_date = DateTimeField(null=True)
    is_active = BooleanField(default=True)
    payment_method = TextField(default=TransactionType.Lightning)
    payment_id = TextField()


class Student(UserModel):  # Estudante
    registration_code = TextField(null=True)  # matricula


class Teacher(UserModel):  # Professor
    pass


class Organization(UserModel):  # Organização, Escola | Universidade
    pass


class Course(BaseModel):  # Curso | Disciplina
    name = TextField()
    teacher = ForeignKeyField(Teacher, backref='courses', null=True)
    description = TextField(null=True)


class AttendanceList(BaseModel):  # Lista de Prensença
    date = DateTimeField()
    comment = TextField(null=True)


class LinkCoursesStudents(BaseModel):  # Ligação de Cursos com Estudantes
    course = ForeignKeyField(Course, backref='linkCoursesStudents')
    student = ForeignKeyField(Student, backref='linkCoursesStudents')


class LinkStudentsOrganizations(BaseModel):  # Ligação de Estudantes com Organizações
    student = ForeignKeyField(Student, backref='linkStudentsOrganizations')
    organization = ForeignKeyField(Organization, backref='linkStudentsOrganizations')


class LinkCoursesOrganizations(BaseModel):  # Ligação de Cursos com Organizações
    course = ForeignKeyField(Course, backref='linkCoursesOrganizations')
    organization = ForeignKeyField(Organization, backref='linkCoursesOrganizations')


class LinkTeachersOrganizations(BaseModel):  # Ligação de Professores com Organizações
    teacher = ForeignKeyField(Teacher, backref='linkTeachersOrganizations')
    organization = ForeignKeyField(Organization, backref='linkTeachersOrganizations')


class LinkStudentsAttendanceLists(BaseModel):  # Ligação de Estudantes com Listas de Presença
    student = ForeignKeyField(Student, backref='linkStudentsAttendanceLists')
    attendanceList = ForeignKeyField(AttendanceList, backref='linkStudentsAttendanceLists')
    comment = TextField(null=True)


class LinkLicensesTeachers(BaseModel):  # Ligação das Licenças dos Professores
    teacher = ForeignKeyField(Teacher, backref='linkLicensesTeachers')
    license = ForeignKeyField(License, backref='linkLicensesTeachers')


class LinkLicensesOrganizations(BaseModel):  # Ligação das Licenças das Organizações
    organization = ForeignKeyField(Organization, backref='linkLicensesOrganizations')
    license = ForeignKeyField(License, backref='linkLicensesOrganizations')


pg_db.create_tables([License,
                     Student,
                     Teacher,
                     Organization,
                     Course,
                     AttendanceList,
                     LinkCoursesStudents,
                     LinkStudentsOrganizations,
                     LinkCoursesOrganizations,
                     LinkTeachersOrganizations,
                     LinkStudentsAttendanceLists,
                     LinkLicensesTeachers,
                     LinkLicensesOrganizations])


# TO DO
# Padronizar as querys de select, insert, update e delete


def insert_many_on_table(db, table: BaseModel, data: List[dict]):
    with db.atomic():
        query = table.insert_many(data)
        query.execute()


def select_students():
    query = Student.select()
    for student in query:
        print(student.username)


def select_attendance_list_by_id(list_id: int):
    query = (LinkStudentsAttendanceLists
             .select()
             .where(LinkStudentsAttendanceLists.attendanceList == list_id))
    for attendanceList in query:
        print(attendanceList.attendanceList.id,
              attendanceList.student.username,
              attendanceList.attendanceList.date)
    return list(query)


def select_licenses_of_teacher(teacher_id: int):
    query = (LinkLicensesTeachers
             .select()
             .where(LinkLicensesTeachers.teacher == teacher_id))
    return list((row.license for row in query))


def select_teachers_of_organization(organization_id):
    query = (LinkTeachersOrganizations
             .select()
             .where(LinkTeachersOrganizations.organization == organization_id))
    return list((row.teacher for row in query))


def select_users():
    query_student = (Student.select())
    query_teacher = (Teacher.select())
    query_organization = (Organization.select())
    users = dict()
    for user in query_student:
        users[user.username] = user.__dict__['__data__']
    for user in query_teacher:
        users[user.username] = user.__dict__['__data__']
    for user in query_organization:
        users[user.username] = user.__dict__['__data__']
    return users


def select_users_by_condition(table_and_condition: List[tuple]):
    lista = list()
    for table, condition in table_and_condition:
        query = table.select().where(condition)
        lista += list(query)
    return lista


def get_username_by_email(email: str):
    table_and_condition = [(Student, Student.email == email),
                           (Teacher, Teacher.email == email),
                           (Organization, Organization.email == email)]
    try:
        user = select_users_by_condition(table_and_condition)[0]
        return user.username
    except IndexError:
        return None


if __name__ == "__main__":
    if str(input('Insert com dados de teste(yes or not)? ')) in ['y', 'yes']:
        data = [
            {'username': 'lucas',
             'full_name': 'Lucas Santos',
             'email': 'lucas@email.com',
             'hashed_password': '$2b$12$IJwfYdrdxZbjuyJ8ZQsA7.E7bP8dpuf..9UNhgdbQ0rd.ia1RbXtS'},
            {'username': 'pedro',
             'full_name': 'Pedro Alfonço',
             'email': 'pedro@email.com',
             'hashed_password': '$2b$12$IJwfYdrdxZbjuyJ8ZQsA7.E7bP8dpuf..9UNhgdbQ0rd.ia1RbXtS' },
            {'username': 'joão',
             'full_name': 'João Gomes',
             'email': 'joao@email.com',
             'hashed_password': '$2b$12$IJwfYdrdxZbjuyJ8ZQsA7.E7bP8dpuf..9UNhgdbQ0rd.ia1RbXtS'},
            {'username': 'maria',
             'full_name': 'Maria de Fatima',
             'email': 'maria@email.com',
             'hashed_password': '$2b$12$IJwfYdrdxZbjuyJ8ZQsA7.E7bP8dpuf..9UNhgdbQ0rd.ia1RbXtS'},
            {'username': 'paula',
             'full_name': 'Paula Fernandes',
             'email': 'paula@email.com',
             'hashed_password': '$2b$12$IJwfYdrdxZbjuyJ8ZQsA7.E7bP8dpuf..9UNhgdbQ0rd.ia1RbXtS'},
            {'username': 'ana',
             'full_name': 'Ana Cleia',
             'email': 'ana@email.com',
             'hashed_password': '$2b$12$IJwfYdrdxZbjuyJ8ZQsA7.E7bP8dpuf..9UNhgdbQ0rd.ia1RbXtS'}
        ]
        insert_many_on_table(pg_db, Student, data)

        data = [
            {'date': datetime.today()},
        ]
        insert_many_on_table(pg_db, AttendanceList, data)

        data = [
            {'username': 'raimundo',
             'full_name': 'Raimundo Nonato',
             'email': 'raimundo@email.com',
             'hashed_password': '$2b$12$IJwfYdrdxZbjuyJ8ZQsA7.E7bP8dpuf..9UNhgdbQ0rd.ia1RbXtS'},
            {'username': 'juliana',
             'full_name': 'Juliana de Sousa',
             'email': 'juliana@email.com',
             'hashed_password': '$2b$12$IJwfYdrdxZbjuyJ8ZQsA7.E7bP8dpuf..9UNhgdbQ0rd.ia1RbXtS'},
            {'username': 'romulo',
             'full_name': 'Romulo Buzar',
             'email': 'romulo@email.com',
             'hashed_password': '$2b$12$IJwfYdrdxZbjuyJ8ZQsA7.E7bP8dpuf..9UNhgdbQ0rd.ia1RbXtS'}
        ]
        insert_many_on_table(pg_db, Teacher, data)

        data = [
            {'username': 'UFMA',
             'full_name': 'Universidade Federal do Maranhão',
             'email': 'ufma@ufma.br',
             'hashed_password': '$2b$12$IJwfYdrdxZbjuyJ8ZQsA7.E7bP8dpuf..9UNhgdbQ0rd.ia1RbXtS'},
            {'username': 'UEMA',
             'full_name': 'Universidade Estadual do Maranhão',
             'email': 'euma@euma.br',
             'hashed_password': '$2b$12$IJwfYdrdxZbjuyJ8ZQsA7.E7bP8dpuf..9UNhgdbQ0rd.ia1RbXtS'},
            {'username': 'IFMA',
             'full_name': 'Instituto Federal do Maranhão',
             'email': 'ifma@ifma.br',
             'hashed_password': '$2b$12$IJwfYdrdxZbjuyJ8ZQsA7.E7bP8dpuf..9UNhgdbQ0rd.ia1RbXtS'}
        ]
        insert_many_on_table(pg_db, Organization, data)

        data = [
            {'payment_id': 'invoice'}
        ]
        insert_many_on_table(pg_db, License, data)

        data = [
            {'name': 'python basic', 'teacher_id': 1}
        ]
        insert_many_on_table(pg_db, Course, data)

        for i in range(1, 4):
            table = LinkCoursesStudents(student=i, course=1)
            table.save()
        for i in range(1, 3):
            table = LinkCoursesOrganizations(organization=i, course=1)
            table.save()
        for i in range(1, 3):
            table = LinkTeachersOrganizations(organization=1, teacher=i)
            table.save()
        for i in range(1, 4):
            table = LinkStudentsAttendanceLists(student=i, attendanceList=1)
            table.save()
        for i in range(1, 4):
            table = LinkStudentsOrganizations(organization=2, student=i)
            table.save()
        for i in range(1, 3):
            table = LinkLicensesTeachers(teacher=i, license=1)
            table.save()
        for i in range(2, 4):
            table = LinkLicensesOrganizations(organization=i, license=1)
            table.save()

    #print(select_attendance_list_by_id(1))
    #for i in range(1, 4):
    #    print(select_licenses_of_teacher(i))

    #print(select_teachers_of_organization(1))
    #print(select_users())
    print(get_username_by_email("lucas@email.com"))
