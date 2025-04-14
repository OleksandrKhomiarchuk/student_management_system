from flask_restful import Resource, reqparse
from flask import jsonify
from database.models import db, Student

student_parser = reqparse.RequestParser()
student_parser.add_argument("first_name", type=str, required=True, help="First name is required")
student_parser.add_argument("last_name", type=str, required=True, help="Last name is required")
student_parser.add_argument("group_id", type=int, required=False)

class StudentAPI(Resource):
    """
    API resource for managing students.
    """
    def get(self, student_id=None):
        """
        Retrieve one or multiple students.
        If a student ID is provided, returns the student's details.
        Otherwise, returns a list of all students.
        """
        if student_id is not None:
            student = db.session.query(Student).filter_by(id=student_id).first()
            if student:
                return jsonify({
                    "id": student.id,
                    "first_name": student.first_name,
                    "last_name": student.last_name,
                    "group_id": student.group_id
                })
            return {"message": "Student not found"}, 404
        students = db.session.query(Student).all()
        return jsonify([
            {
                "id": s.id,
                "first_name": s.first_name,
                "last_name": s.last_name,
                "group_id": s.group_id
            }
            for s in students
        ])

    def post(self):
        """
        Create a new student.
        """
        args = student_parser.parse_args()
        new_student = Student(
            first_name=args["first_name"],
            last_name=args["last_name"],
            group_id=args.get("group_id")
        )
        db.session.add(new_student)
        db.session.commit()
        return {"message": "Student added", "id": new_student.id}, 201

    def put(self, student_id):
        """
        Update an existing student.
        """
        args = student_parser.parse_args()
        student = db.session.query(Student).filter_by(id=student_id).first()
        if not student:
            return {"message": "Student not found"}, 404
        student.first_name = args["first_name"]
        student.last_name = args["last_name"]
        student.group_id = args.get("group_id")
        db.session.commit()
        return {"message": "Student updated"}, 200

    def delete(self, student_id):
        """
        Delete a student by ID.
        """
        student = db.session.query(Student).filter_by(id=student_id).first()
        if not student:
            return {"message": "Student not found"}, 404
        db.session.delete(student)
        db.session.commit()
        return {"message": "Student deleted"}, 200
