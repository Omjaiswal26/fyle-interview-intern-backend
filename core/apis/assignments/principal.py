from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, AssignmentStateEnum
from core.models.teachers import Teacher
from marshmallow import ValidationError
from .schema import AssignmentSchema, AssignmentGradeSchema, TeacherSchema

principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)

@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments"""
    principal_assignments = Assignment.get_all_graded_and_submitted_assignments()
    principal_assignments_dump = AssignmentSchema().dump(principal_assignments, many=True)
    return APIResponse.respond(data=principal_assignments_dump)

@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """Grade an assignment"""
    try:
        if not incoming_payload:
            return APIResponse.error(message="Payload not found", status_code=400)
        
        grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
        assignment = Assignment.get_by_id(grade_assignment_payload.id)

        if not assignment:
            return APIResponse.error(message="Assignment not found", status_code=404)

        if assignment.state == AssignmentStateEnum.DRAFT:
            return APIResponse.error(message="Draft assignment cannot be graded", status_code=400)

        graded_assignment = Assignment.mark_grade(
            _id=grade_assignment_payload.id,
            grade=grade_assignment_payload.grade,
            auth_principal=p
        )

        db.session.commit()
        graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
        return APIResponse.respond(data=graded_assignment_dump)

    except ValidationError as err:
        return APIResponse.error(message=err.messages, status_code=400, error="ValidationError")
    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500, error="ServerError")

@principal_assignments_resources.route('/teachers', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_teachers(p):
    """Returns list of all teachers"""
    teachers = Teacher.query.all()
    teachers_dump = TeacherSchema().dump(teachers, many=True)
    return APIResponse.respond(data=teachers_dump)

@principal_assignments_resources.route('/assignments/<int:assignment_id>/regrade', methods=['PUT'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def regrade_assignment(p, incoming_payload, assignment_id):
    """Re-grade an already graded assignment"""
    try:
        if not incoming_payload:
            return APIResponse.error(message="Payload not found", status_code=400)
        
        grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
        assignment = Assignment.get_by_id(assignment_id)

        if not assignment:
            return APIResponse.error(message="Assignment not found", status_code=404)

        if assignment.state == AssignmentStateEnum.DRAFT:
            return APIResponse.error(message="Draft assignment cannot be graded", status_code=400)

        graded_assignment = Assignment.mark_grade(
            _id=assignment_id,
            grade=grade_assignment_payload.grade,
            auth_principal=p
        )
        
        db.session.commit()
        graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
        return APIResponse.respond(data=graded_assignment_dump)

    except ValidationError as err:
        return APIResponse.error(message=err.messages, status_code=400, error="ValidationError")
    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500, error="ServerError")