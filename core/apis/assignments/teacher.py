from flask import Blueprint, request
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, AssignmentStateEnum
from marshmallow import ValidationError

from .schema import AssignmentSchema, AssignmentGradeSchema

teacher_assignments_resources = Blueprint('teacher_assignments_resources', __name__)

@teacher_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns a list of assignments submitted to the teacher."""
    teachers_assignments = Assignment.get_assignments_by_teacher(p.teacher_id)
    if not teachers_assignments:  # Check if there are no assignments
        return APIResponse.respond(data=[], status_code=200)
    teachers_assignments_dump = AssignmentSchema().dump(teachers_assignments, many=True)
    return APIResponse.respond(data=teachers_assignments_dump)

@teacher_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """Grade an assignment."""
    try:
        grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)

        assignment = Assignment.get_by_id(grade_assignment_payload.id)

        if assignment is None:
            return APIResponse.error(message="Assignment not found", status_code=404, error="FyleError")

        # Check if the assignment belongs to the same teacher
        if assignment.teacher_id == p.teacher_id:
            return APIResponse.error(message="You cannot grade your own assignment", status_code=400, error="FyleError")

        if assignment.state == AssignmentStateEnum.DRAFT:
            return APIResponse.error(message="Draft assignment cannot be graded", status_code=400, error="FyleError")

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

# Additional APIs to be added

@teacher_assignments_resources.route('/assignments/<int:assignment_id>', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def get_assignment_detail(p, assignment_id):
    """Get details of a specific assignment submitted to the teacher."""
    assignment = Assignment.get_by_id(assignment_id)
    
    if assignment is None:
        return APIResponse.error(message="Assignment not found", status_code=404, error="FyleError")
    
    if assignment.teacher_id != p.teacher_id:
        return APIResponse.error(message="You do not have permission to view this assignment", status_code=403, error="FyleError")

    assignment_dump = AssignmentSchema().dump(assignment)
    return APIResponse.respond(data=assignment_dump)

@teacher_assignments_resources.route('/assignments/<int:assignment_id>/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def update_assignment_grade(p, assignment_id, incoming_payload):
    """Update the grade of an assignment."""
    try:
        grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)

        assignment = Assignment.get_by_id(assignment_id)

        if assignment is None:
            return APIResponse.error(message="Assignment not found", status_code=404, error="FyleError")

        if assignment.teacher_id != p.teacher_id:
            return APIResponse.error(message="You cannot grade this assignment", status_code=400, error="FyleError")

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
