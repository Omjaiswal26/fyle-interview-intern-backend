from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment
from marshmallow import ValidationError
from core.models.teachers import Teacher
from core.models.assignments import Assignment, AssignmentStateEnum


from .schema import AssignmentSchema, AssignmentSubmitSchema
student_assignments_resources = Blueprint('student_assignments_resources', __name__)


@student_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments"""
    students_assignments = Assignment.get_assignments_by_student(p.student_id)
    students_assignments_dump = AssignmentSchema().dump(students_assignments, many=True)
    return APIResponse.respond(data=students_assignments_dump)


@student_assignments_resources.route('/assignments', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def upsert_assignment(p, incoming_payload):
    """Create or Edit an assignment"""
    
    if not incoming_payload or 'content' not in incoming_payload or incoming_payload['content'] is None:
        return APIResponse.error(message="Content cannot be null.", status_code=400)
    
    try:
        assignment = AssignmentSchema().load(incoming_payload)
    except ValidationError as err:
        return APIResponse.error(message=err.messages, status_code=400)

    assignment.student_id = p.student_id
    assignment.state = "DRAFT"  # Default state for a new or updated assignment
    assignment.teacher_id = None  # Default teacher_id should be None
    
    upserted_assignment = Assignment.upsert(assignment)
    db.session.commit()
    upserted_assignment_dump = AssignmentSchema().dump(upserted_assignment)
    return APIResponse.respond(data=upserted_assignment_dump)


@student_assignments_resources.route('/assignments/submit', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal  # Change to `@decorators.authenticate_student` if necessary
def submit_assignment(p, incoming_payload):
    """Submit an assignment"""
    
    try:
        submit_assignment_payload = AssignmentSubmitSchema().load(incoming_payload)
    except ValidationError as err:
        return APIResponse.error(message=err.messages, status_code=400)

    # Fetch the assignment by ID
    assignment = Assignment.get_by_id(submit_assignment_payload.id)

    # Ensure the assignment exists and belongs to the authenticated student
    if assignment is None or assignment.student_id != p.student_id:
        return APIResponse.error(message="Assignment not found or access denied.", status_code=404)

    # Validate that the teacher exists
    teacher = Teacher.query.filter_by(id=submit_assignment_payload.teacher_id).first()
    if not teacher:
        return APIResponse.error(message="Teacher not found", status_code=404)

    # Check if the assignment is in the correct state to be submitted
    if assignment.state != AssignmentStateEnum.DRAFT:
        return APIResponse.error(message="only a draft assignment can be submitted", status_code=400, error="FyleError")

    # Mark the assignment as submitted
    assignment.state = AssignmentStateEnum.SUBMITTED
    assignment.teacher_id = submit_assignment_payload.teacher_id

    db.session.commit()
    submitted_assignment_dump = AssignmentSchema().dump(assignment)
    return APIResponse.respond(data=submitted_assignment_dump)



@student_assignments_resources.route('/assignments/<int:assignment_id>', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def view_assignment(p, assignment_id):
    """View a specific assignment"""
    assignment = Assignment.get_by_id(assignment_id)
    
    # Ensure assignment belongs to the student
    if not assignment or assignment.student_id != p.student_id:
        return APIResponse.error(message="Assignment not found", status_code=404)

    assignment_dump = AssignmentSchema().dump(assignment)
    return APIResponse.respond(data=assignment_dump)



@student_assignments_resources.route('/assignments/submitted', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_submitted_assignments(p):
    """List all submitted assignments"""
    submitted_assignments = Assignment.get_submitted_assignments_by_student(p.student_id)
    submitted_assignments_dump = AssignmentSchema().dump(submitted_assignments, many=True)
    return APIResponse.respond(data=submitted_assignments_dump)



@student_assignments_resources.route('/assignments/<int:assignment_id>', methods=['DELETE'], strict_slashes=False)
@decorators.authenticate_principal  # This should be `@decorators.authenticate_student`
def delete_draft_assignment(p, assignment_id):
    """Delete a draft assignment"""
    assignment = Assignment.get_by_id(assignment_id)

    # Ensure assignment is in draft state and belongs to the student
    if not assignment or assignment.student_id != p.student_id:
        return APIResponse.error(message="Assignment not found", status_code=404)
    if assignment.state != AssignmentStateEnum.DRAFT:
        return APIResponse.error(message="Only draft assignments can be deleted", status_code=400)

    # Delete the assignment
    Assignment.delete(assignment_id)
    db.session.commit()
    return APIResponse.respond(data=None, message="Assignment deleted successfully.")

