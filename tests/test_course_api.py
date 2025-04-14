from flask import url_for
from database.models import Course, Student


def test_get_all_courses(client, test_data):
    with client.application.app_context():
        url = url_for('courseapi')
    response = client.get(url)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(course['name'] == 'Math' for course in data)

def test_get_single_course(client, test_data):
    course_id = test_data["course"].id
    with client.application.app_context():
        url = url_for('courseapi', course_id=course_id)
    response = client.get(url)
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Math"

def test_get_nonexistent_course(client, test_data):
    with client.application.app_context():
        url = url_for('courseapi', course_id=999)
    response = client.get(url)
    assert response.status_code == 404

def test_create_course(client, test_data):
    with client.application.app_context():
        url = url_for('courseapi')
    response = client.post(url, json={"name": "Physics", "description": "Physics Course"})
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data

def test_create_duplicate_course(client, test_data):
    with client.application.app_context():
        url = url_for('courseapi')
    response = client.post(url, json={"name": "Math"})
    assert response.status_code == 400

def test_update_course(client, test_data):
    course_id = test_data["course"].id
    with client.application.app_context():
        url = url_for('courseapi', course_id=course_id)
    response = client.put(url, json={"name": "Updated Math", "description": "Updated"})
    assert response.status_code == 200
    updated = Course.query.get(course_id)
    assert updated.name == "Updated Math"

def test_update_nonexistent_course(client, test_data):
    with client.application.app_context():
        url = url_for('courseapi', course_id=999)
    response = client.put(url, json={"name": "XXX"})
    assert response.status_code == 404

def test_delete_course(client, test_data):
    course_id = test_data["course"].id
    with client.application.app_context():
        url = url_for('courseapi', course_id=course_id)
    response = client.delete(url)
    assert response.status_code == 200
    assert Course.query.get(course_id) is None

def test_delete_nonexistent_course(client, test_data):
    with client.application.app_context():
        url = url_for('courseapi', course_id=999)
    response = client.delete(url)
    assert response.status_code == 404

def test_get_course_students(client, test_data):
    course_id = test_data['course'].id
    with client.application.app_context():
        url = url_for('coursestudentsapi', course_id=course_id)
    response = client.get(url)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(s['first_name'] == 'John' for s in data)

def test_add_students_to_course(client, test_data, db_session):
    course = Course(name="Biology", description="Bio")
    db_session.add(course)
    db_session.commit()
    with client.application.app_context():
        url = url_for('coursestudentsapi', course_id=course.id)
    response = client.post(url, json={"student_id": test_data['student'].id})
    assert response.status_code == 201

def test_add_existing_students_to_course(client, test_data):
    with client.application.app_context():
        url = url_for('coursestudentsapi', course_id=test_data['course'].id)
    response = client.post(url, json={"student_id": test_data["student"].id})
    assert response.status_code == 400

def test_add_student_to_nonexistent_course(client, test_data):
    with client.application.app_context():
        url = url_for('coursestudentsapi', course_id=999)
    response = client.post(url, json={"student_id": test_data['student'].id})
    assert response.status_code == 404
    assert response.get_json()['message'] == "Course or student not found"

def test_delete_student_from_course(client, test_data):
    with client.application.app_context():
        url = url_for('coursestudentsapi', course_id=test_data['course'].id,
                                                    student_id=test_data['student'].id)
    response = client.delete(url)
    assert response.status_code == 200

def test_delete_student_from_nonexistent_course(client, test_data, db_session):
    new_student = Student(first_name="Jane", last_name="Smith", group=test_data["group"])
    db_session.add(new_student)
    db_session.commit()
    with client.application.app_context():
        url = url_for('coursestudentsapi', course_id=test_data['course'].id,
                                                    student_id=new_student.id)
    response = client.delete(url)
    assert response.status_code == 400

def test_remove_student_from_nonexistent_course(client, test_data):
    with client.application.app_context():
        url = url_for('coursestudentsapi', course_id=999,
                                                    student_id=test_data['student'].id)
    response = client.delete(url)
    assert response.status_code == 404

def test_get_students_of_nonexistent_course(client):
    with client.application.app_context():
        url = url_for('coursestudentsapi', course_id=999)
    response = client.get(url)
    assert response.status_code == 404
    assert response.get_json() == {"message": "Course not found"}