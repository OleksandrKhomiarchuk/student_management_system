from flask_restful import Resource, reqparse
from flask import jsonify
from sqlalchemy import func
from database.models import db, Course, Student


course_parser = reqparse.RequestParser()
course_parser.add_argument("name", type=str, required=True, help="Course name is required")
course_parser.add_argument("description", type=str, required=False)
student_course_parser = reqparse.RequestParser()
student_course_parser.add_argument("student_id", type=int, required=True, help="Student ID is required")

class CourseAPI(Resource):
    """
    API resource for managing courses.
    """
    def get(self, course_id=None):
        """
        Retrieve a course by ID or return a list of all courses.
        Args:
            course_id (int, optional): The ID of the course. If not provided, returns all courses.
        Returns:
            Response: JSON with course details or a list of courses.
        """
        if course_id:
            course = db.session.query(Course).filter_by(id=course_id).first()
            if course:
                students = db.session.query(Student).join(Course.students).filter(
                    Course.id == course_id).all()
                return jsonify({
                    "id": course.id,
                    "name": course.name,
                    "description": course.description,
                    "students": [
                        {"id": s.id, "first_name": s.first_name, "last_name": s.last_name}
                        for s in students
                    ]
                })
            return {"message": "Course not found"}, 404
        courses = db.session.query(
            Course.id,
            Course.name,
            Course.description,
            func.count(Student.id).label("students_count")
        ).outerjoin(Course.students).group_by(Course.id).all()
        return jsonify([
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "students_count": c.students_count
            } for c in courses
        ])

    def post(self):
        """
        Create a new course.
        Returns:
            dict: A message and the new course ID, or an error message if it already exists.
        """
        args = course_parser.parse_args()
        existing_course = db.session.query(Course).filter_by(name=args["name"]).first()
        if existing_course:
            return {"message": "Course with this name already exists"}, 400
        new_course = Course(name=args["name"], description=args.get("description"))
        db.session.add(new_course)
        db.session.commit()
        return {"message": "Course added", "id": new_course.id}, 201

    def put(self, course_id):
        """
        Update an existing course by ID.
        Args:
            course_id (int): The ID of the course to update.
        Returns:
            dict: A message indicating success or failure.
        """
        args = course_parser.parse_args()
        course = db.session.query(Course).filter_by(id=course_id).first()
        if not course:
            return {"message": "Course not found"}, 404
        course.name = args["name"]
        course.description = args.get("description")
        db.session.commit()
        return {"message": "Course updated"}, 200

    def delete(self, course_id):
        """
        Delete a course by ID.
        Args:
            course_id (int): The ID of the course to delete.
        Returns:
            dict: A message indicating success or failure.
        """
        course = db.session.query(Course).filter_by(id=course_id).first()
        if not course:
            return {"message": "Course not found"}, 404
        db.session.delete(course)
        db.session.commit()
        return {"message": "Course deleted"}, 200

class CourseStudentsAPI(Resource):
    """
    API resource for managing students in a course.
    """
    def get(self, course_id):
        """
        Retrieve all students enrolled in a course.
        Args:
            course_id (int): The ID of the course.
        Returns:
            Response: JSON list of students in the course.
        """
        course_exist = db.session.query(Course.id).filter_by(id=course_id).scalar()
        if not course_exist:
            return {"message": "Course not found"}, 404
        students = db.session.query(Student).join(Student.courses).filter(Course.id == course_id).all()
        return jsonify([
            {"id": s.id, "first_name": s.first_name, "last_name": s.last_name, "group_id": s.group_id}
            for s in students
        ])

    def post(self, course_id):
        """
        Enroll a student in a course.
        Args:
            course_id (int): The ID of the course.
        Returns:
            dict: A message indicating success or failure.
        """
        args = student_course_parser.parse_args()
        student = db.session.query(Student).filter_by(id=args["student_id"]).first()
        course = db.session.query(Course).filter_by(id=course_id).first()
        if not course or not student:
            return {"message": "Course or student not found"}, 404
        exists = db.session.query(Course).join(Course.students).filter(
            Course.id == course_id,
            Student.id == args["student_id"]
        ).first()
        if exists:
            return {"message": "Student already in course"}, 400
        course.students.append(student)
        db.session.commit()
        return {"message": "Student added to course"}, 201

    def delete(self, course_id, student_id):
        """
        Remove a student from a course.
        Args:
            course_id (int): The ID of the course.
            student_id (int): The ID of the student to remove.
        Returns:
            dict: A message indicating success or failure.
        """
        course = db.session.query(Course).filter_by(id=course_id).first()
        student = db.session.query(Student).filter_by(id=student_id).first()
        if not course or not student:
            return {"message": "Course or student not found"}, 404
        enrolled = db.session.query(Student.id).join(Student.courses).filter(
            Course.id == student_id,
            Course.id == course_id
        ).scalar()
        if not enrolled:
            return {"message": "Student is not enrolled in the course"}, 400
        course.students.remove(student)
        db.session.commit()
        return {"message": "Student removed from course"}, 200
