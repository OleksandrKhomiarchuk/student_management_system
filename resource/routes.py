from flask_restful import Api
from flask import Blueprint
from .course_api import CourseAPI, CourseStudentsAPI
from .group_api import GroupAPI
from .student_api import StudentAPI


def reg_resources(api: Api):
    """
    Register all routes
    """
    api.add_resource(CourseAPI, '/courses/', '/courses/<int:course_id>')
    api.add_resource(CourseStudentsAPI,'/courses/<int:course_id>/students',
                                            '/courses/<int:course_id>/students/<int:student_id>')
    api.add_resource(GroupAPI, '/groups/', '/groups/<int:group_id>')
    api.add_resource(StudentAPI, '/students/', '/students/<int:student_id>')

api_bp = Blueprint('api_bp', __name__)
@api_bp.route('/favicon.ico')
def favicon(): #pragma: no cover
    """
    Imitation favicon
    """
    return "", 202
