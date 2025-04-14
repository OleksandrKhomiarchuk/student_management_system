from flask_restful import Resource, reqparse
from flask import request, jsonify
from sqlalchemy import func
from database.models import db, Group, Student

group_parser = reqparse.RequestParser()
group_parser.add_argument("name", type=str, required=True, help="Group name is required")

class GroupAPI(Resource):
    """
    API resource for managing student groups.
    """
    def get(self, group_id=None):
        """
        Retrieve one or multiple groups.
        If a group ID is provided, return the group details.
        Otherwise, return a list of all groups, optionally filtered by student count.
        Query Parameters:
            students_count (int, optional): Maximum number of students in the group.
        Path Parameters:
            group_id (int, optional): ID of the group.
        Returns:
            JSON response containing group information or a list of groups.
        """
        if group_id:
            group = db.session.get(Group, group_id)
            if group:
                return jsonify({
                    "id": group.id,
                    "name": group.name,
                    "students_count": len(group.students)
                })
            return {"message": "Group not found"}, 404
        students_count = request.args.get("students_count", type=int)
        query = db.session.query(
            Group.id,
            Group.name,
            func.count(Student.id).label("students_count")
        ).outerjoin(Student).group_by(Group.id)
        if students_count is not None:
            query = query.having(func.count(Student.id) <= students_count)
        groups = query.all()
        return jsonify([
            {"id": g.id, "name": g.name, "students_count": g.students_count}
            for g in groups
        ])

    def post(self):
        """
        Create a new group.
        Request Body:
            name (str): The name of the group (required).
        Returns:
            JSON response with a success message and the new group's ID,
            or an error message if the name already exists.
        """
        args = group_parser.parse_args()
        if Group.query.filter_by(name=args["name"]).first():
            return {"message": "Group with this name already exists"}, 400
        new_group = Group(name=args["name"])
        db.session.add(new_group)
        db.session.commit()
        return {"message": "Group added", "id": new_group.id}, 201

    def put(self, group_id):
        """
        Update an existing group.
        Path Parameters:
            group_id (int): ID of the group to update.
        Request Body:
            name (str): The new name for the group (required).
        Returns:
            JSON response with a success or error message.
        """
        args = group_parser.parse_args()
        group = db.session.get(Group, group_id)
        if not group:
            return {"message": "Group not found"}, 404
        group.name = args["name"]
        db.session.commit()
        return {"message": "Group updated"}, 200

    def delete(self, group_id):
        """
        Delete an existing group.
        Path Parameters:
            group_id (int): ID of the group to delete.
        Returns:
            JSON response with a success or error message.
        """
        group = db.session.get(Group, group_id)
        if not group:
            return {"message": "Group not found"}, 404
        db.session.delete(group)
        db.session.commit()
        return {"message": "Group deleted"}, 200
