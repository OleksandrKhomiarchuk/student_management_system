from flask import url_for
from database.models import Group, Student


def test_get_all_groups(client, test_data):
    with client.application.app_context():
        url = url_for('groupapi')
    response = client.get(url)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(g['name'] == 'A1' for g in data)

def test_get_group_by_id(client, test_data):
    group_id = test_data["group"].id
    with client.application.app_context():
        url = url_for('groupapi', group_id=group_id)
    response = client.get(url)
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "A1"
    assert "students_count" in data

def test_get_group_not_found(client, test_data):
    with client.application.app_context():
        url = url_for('groupapi', group_id=999)
    response = client.get(url)
    assert response.status_code == 404
    assert response.get_json()["message"] == "Group not found"

def test_filter_groups_by_student_count(client, db_session):
    g1 = Group(name="F2")
    g2 = Group(name="B5")
    db_session.add_all([g1, g2])
    db_session.commit()
    s1 = Student(first_name="Test", last_name="One", group=g2)
    s2 = Student(first_name="Test", last_name="Two", group=g2)
    db_session.add_all([s1, s2])
    db_session.commit()
    with client.application.app_context():
        url = url_for('groupapi', students_count=1)
    response = client.get(url)
    assert response.status_code == 200
    data = response.get_json()
    assert all(g["students_count"] <= 1 for g in data)

def test_create_groups(client):
    with client.application.app_context():
        url = url_for('groupapi')
    response = client.post(url, json={"name": "A1"})
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["message"] == "Group added"

def test_create_duplicate_group(client, test_data):
    with client.application.app_context():
        url = url_for('groupapi')
    response = client.post(url, json={"name": "A1"})
    assert response.status_code == 400
    assert response.get_json()["message"] == "Group with this name already exists"

def test_update_group(client, test_data):
    group_id = test_data["group"].id
    with client.application.app_context():
        url = url_for('groupapi', group_id=group_id)
    response = client.put(url, json={"name": "U9"})
    assert response.status_code == 200
    assert response.get_json()["message"] == "Group updated"

def test_update_group_not_found(client, test_data):
    with client.application.app_context():
        url = url_for('groupapi', group_id=999)
    response = client.put(url, json={"name": "X6"})
    assert response.status_code == 404
    assert response.get_json()["message"] == "Group not found"

def test_delete_group(client, test_data):
    group_id = test_data["group"].id
    with client.application.app_context():
        url = url_for('groupapi', group_id=group_id)
    response = client.delete(url)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Group deleted"

def test_delete_group_not_found(client, test_data):
    with client.application.app_context():
        url = url_for('groupapi', group_id=999)
    response = client.delete(url)
    assert response.status_code == 404
    assert response.get_json()["message"] == "Group not found"
