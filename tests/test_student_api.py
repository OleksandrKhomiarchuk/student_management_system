from flask import url_for


def test_get_all_students(client, test_data):
    with client.application.app_context():
        url = url_for('studentapi')
    response = client.get(url)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(s['first_name'] == 'John' and s['last_name'] == 'Doe' for s in data)

def test_get_student_by_id(client, test_data):
    student_id = test_data["student"].id
    with client.application.app_context():
        url = url_for('studentapi', student_id=student_id)
    response = client.get(url)
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == 1
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["group_id"] == test_data["group"].id

def test_get_student_not_found(client):
    with client.application.app_context():
        url = url_for('studentapi', student_id=999)
    response = client.get(url)
    assert response.status_code == 404
    assert response.get_json()["message"] == "Student not found"

def test_create_student(client):
    new_student = {"first_name": "Alice", "last_name": "Smith", "group_id": 1}
    with client.application.app_context():
        url = url_for('studentapi')
    response = client.post(url, json=new_student)
    assert response.status_code == 201
    assert response.get_json()["message"] == "Student added"

def test_create_student_without_group(client):
    with client.application.app_context():
        url = url_for('studentapi')
    response = client.post(url, json={"first_name": "Bob", "last_name": "Builder"})
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data

def test_update_student(client, test_data):
    updated_data = {"first_name": "Johnny", "last_name": "Doe", "group_id": 1}
    with client.application.app_context():
        url = url_for('studentapi', student_id=1)
    response = client.put(url, json=updated_data)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Student updated"

def test_update_student_not_found(client):
    updated_data = {"first_name": "Unknown", "last_name": "Person", "group_id": 1}
    with client.application.app_context():
        url = url_for('studentapi', student_id=999)
    response = client.put(url, json=updated_data)
    assert response.status_code == 404
    assert response.get_json()["message"] == "Student not found"

def test_delete_student(client, test_data):
    with client.application.app_context():
        url = url_for('studentapi', student_id=1)
    response = client.delete(url)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Student deleted"
    response = client.get(url)
    assert response.status_code == 404

def test_delete_student_not_found(client):
    with client.application.app_context():
        url = url_for('studentapi', student_id=999)
    response = client.delete(url)
    assert response.status_code == 404
    assert response.get_json()["message"] == "Student not found"
