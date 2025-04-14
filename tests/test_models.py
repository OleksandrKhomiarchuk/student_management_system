import pytest
from database.models import Group, Student, Course, student_course


def test_group_model(db_session):
    group = Group(name="Group A")
    db_session.add(group)
    db_session.commit()
    assert group.id is not None
    assert group.name == "Group A"
    assert repr(group) == f'Group(id={group.id}, name=Group A)'
    assert group.students == []

def test_student_model(db_session):
    group = Group(name="Group B")
    student = Student(first_name="John", last_name="Doe", group=group)
    db_session.add_all([group, student])
    db_session.commit()
    assert student.id is not None
    assert student.first_name == "John"
    assert student.last_name == "Doe"
    assert student.group_id == group.id
    assert repr(student) == f'Student(id={student.id}, first_name=John, last_name=Doe)'
    assert student.group == group
    assert group.students == [student]
    assert student.courses == []

def test_course_model(db_session):
    course = Course(name="Math", description="Mathematics course")
    db_session.add(course)
    db_session.commit()
    assert course.id is not None
    assert course.name == "Math"
    assert course.description == "Mathematics course"
    assert repr(course) == f'Course(id={course.id}, name=Math)'
    assert course.students == []

def test_student_course_relationship(db_session):
    group = Group(name="Group C")
    student = Student(first_name="Alice", last_name="Smith", group=group)
    course1 = Course(name="Physics", description="Physics course")
    course2 = Course(name="Chemistry", description="Chemistry course")
    student.courses.extend([course1, course2])
    db_session.add_all([group, student, course1, course2])
    db_session.commit()
    assert len(student.courses) == 2
    assert course1 in student.courses
    assert course2 in student.courses
    assert student in course1.students
    assert student in course2.students
    stmt = student_course.select().where(student_course.c.student_id == student.id)
    result = db_session.execute(stmt).fetchall()
    assert len(result) == 2
    assert {row.course_id for row in result} == {course1.id, course2.id}

def test_group_deletion_cascade(db_session):
    group = Group(name="Group D")
    student = Student(first_name="Bob", last_name="Johnson", group=group)
    db_session.add_all([group, student])
    db_session.commit()
    db_session.delete(group)
    db_session.commit()
    student = db_session.query(Student).filter_by(first_name="Bob").one()
    assert student.group_id is None
    assert student.group is None

def test_uniqueness_constraints(db_session):
    group1 = Group(name="Group12345")
    db_session.add(group1)
    db_session.commit()
    group2 = Group(name="Group12345")
    db_session.add(group2)
    with pytest.raises(Exception):
        db_session.commit()
    db_session.rollback()
    course1 = Course(name="Unique Course 1", description="Desc")
    db_session.add(course1)
    db_session.commit()
    course2 = Course(name="Unique Course 1", description="Another desc")
    db_session.add(course2)
    with pytest.raises(Exception):
        db_session.commit()
