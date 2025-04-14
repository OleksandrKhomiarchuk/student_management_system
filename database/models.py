from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

student_course = db.Table(
    'student_course',
    db.Column('student_id', db.Integer, db.ForeignKey('students.id', ondelete="CASCADE"), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id', ondelete="CASCADE"), primary_key=True)
)

class Group(db.Model):
    """
    Represents a student group.
    Attributes:
        id (int): Primary key for the group.
        name (str): Unique short name of the group.
        students (List[Student]): List of students in this group.
    """
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True, nullable=False)
    students = db.relationship('Student', back_populates='group')
    def __repr__(self):
        return f'Group(id={self.id}, name={self.name})'

class Student(db.Model):
    """
    Represents a student.
    Attributes:
        id (int): Primary key for the student.
        group_id (int): Foreign key to the group the student belongs to.
        first_name (str): Student's first name.
        last_name (str): Student's last name.
        group (Group): The group this student belongs to.
        courses (List[Course]): List of courses the student is enrolled in.
    """
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id', ondelete="SET NULL"), nullable=True, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    group = db.relationship('Group', back_populates='students')
    courses = db.relationship('Course', secondary=student_course, back_populates='students')
    def __repr__(self):
        return f'Student(id={self.id}, first_name={self.first_name}, last_name={self.last_name})'

class Course(db.Model):
    """
    Represents a course.
    Attributes:
        id (int): Primary key for the course.
        name (str): Unique name of the course.
        description (str): Optional description of the course.
        students (List[Student]): List of students enrolled in this course.
    """
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    students = db.relationship('Student', secondary=student_course, back_populates='courses')
    def __repr__(self):
        return f'Course(id={self.id}, name={self.name})'
