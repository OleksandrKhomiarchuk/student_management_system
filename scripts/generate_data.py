import random
import string
from faker import Faker
from database.models import db, Group, Student, Course

fake = Faker()
courses_list = ['Algebra', 'Biology', 'Physics', 'Chemistry', 'History',
    'Geography', 'Geometry', 'Technology', 'Music', 'Physical education']

def random_group_name():
    """
    Generate a random group name in the format 'XX-00',
    where X is an uppercase letter and 0 is a digit.
    Returns:
        str: A random group name.
    """
    return (''.join(random.choices(string.ascii_uppercase, k=2))
            + '-' + ''.join(random.choices(string.digits, k=2)))

def init_db():
    """
    Drop all tables and create them again in the database.
    Used to reset the database state before generating new data.
    """
    db.drop_all()
    db.create_all()

def distribute_students_to_groups(students, groups):
    """
    Assign students to groups, aiming for an even distribution.
    Initially assigns 10 students per group, then fills up to 30 per group if needed.
    Args:
        students (list): List of Student objects.
        groups (list): List of Group objects.
    Returns:
        dict: A dictionary mapping group IDs to the list of assigned students.
    """
    students_per_group = {group.id: [] for group in groups}
    remaining_students = students.copy()

    for group in groups:
        for _ in range(10):
            if remaining_students:
                student = remaining_students.pop()
                students_per_group[group.id].append(student)
                student.group_id = group.id

    while remaining_students:
        available_groups = [
            group for group in groups
            if len(students_per_group[group.id]) < 30
        ]
        if not available_groups:
            break #pragma: no cover
        group = random.choice(available_groups)
        student = remaining_students.pop()
        students_per_group[group.id].append(student)
        student.group_id = group.id

    return students_per_group

def generate_data():
    """
    Populate the database with fake data:
    - 10 random groups
    - 10 predefined courses
    - 200 fake students
    - Random distribution of students into groups and courses
    Commits data to the database at each major step.
    """
    init_db()

    groups = [Group(name=random_group_name()) for _ in range(10)]
    db.session.add_all(groups)
    db.session.commit()

    courses = [Course(name=course, description=f'Description of {course}') for course in courses_list]
    db.session.add_all(courses)
    db.session.commit()

    students = [
        Student(first_name=fake.first_name(), last_name=fake.last_name(), group_id=None)
        for _ in range(200)
    ]
    db.session.add_all(students)
    db.session.commit()

    random.shuffle(students)
    distribute_students_to_groups(students, groups)
    db.session.commit()

    for student in students:
        student_courses = random.sample(courses, random.randint(1, 3))
        student.courses.extend(student_courses)
    db.session.commit()
