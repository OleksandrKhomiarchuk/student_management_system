import pytest
from scripts.generate_data import (random_group_name,
distribute_students_to_groups, courses_list, generate_data)
from database.models import Group, Student, Course

def test_random_group_name():
    name = random_group_name()
    assert len(name) == 5
    assert name[2] == '-'
    assert name[:2].isalpha()
    assert name[:2].isupper()
    assert name[3:].isdigit()

def test_distribute_students_to_groups(db_session):
    groups = [Group(name="G1"), Group(name="G2")]
    students = [Student(first_name="S", last_name=str(i)) for i in range(25)]
    db_session.add_all(groups + students)
    db_session.commit()
    result = distribute_students_to_groups(students, groups)
    assert len(result) == 2
    assert sum(len(v) for v in result.values()) == 25
    for group in groups:
        assert 10 <= len(result[group.id]) <= 15

def test_generate_groups(db_session):
    groups = [Group(name=random_group_name()) for _ in range(10)]
    db_session.add_all(groups)
    db_session.commit()
    assert len(groups) == 10
    names = {g.name for g in groups}
    assert len(names) == 10

def test_generate_courses(db_session):
    courses = [Course(name=c, description=f"Desc {c}") for c in courses_list]
    db_session.add_all(courses)
    db_session.commit()
    assert len(courses) == len(courses_list)
    names = {c.name for c in courses}
    assert names == set(courses_list)

def test_model_constraints(db_session):
    group1 = Group(name="G1")
    group2 = Group(name="G1")
    db_session.add_all([group1, group2])
    with pytest.raises(Exception):
        db_session.commit()
    db_session.rollback()
    course1 = Course(name="Math", description="Desc1")
    course2 = Course(name="Math", description="Desc2")
    db_session.add_all([course1, course2])
    with pytest.raises(Exception):
        db_session.commit()
    db_session.rollback()
    with pytest.raises(Exception):
        student = Student(first_name=None, last_name="Test")
        db_session.add(student)
        db_session.commit()
    db_session.rollback()

def test_generate_data(app):
    with app.app_context():
        generate_data()
        groups = Group.query.all()
        assert len(groups) == 10
        courses = Course.query.all()
        assert len(courses) == len(courses_list)
        students = Student.query.all()
        assert len(students) == 200
        for student in students:
            assert student.group_id is not None
            assert 1 <= len(student.courses) <= 3
