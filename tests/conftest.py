import pytest
from app import create_app
from database.models import db, Group, Student, Course
from config import TestConfig


@pytest.fixture(scope='function')
def app():
    app = create_app(TestConfig)
    app.config.from_object('config.TestConfig')
    app.config['SERVER_NAME'] = 'localhost'
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    yield db.session
    db.session.rollback()


@pytest.fixture(scope='function')
def test_data(db_session):
    group = Group(name="A1")
    student = Student(first_name="John", last_name="Doe", group=group)
    course = Course(name="Math", description="Mathematics Course")
    student.courses.append(course)
    db_session.add_all([group, student, course])
    db_session.commit()
    return {"group": group, "student": student, "course": course}
