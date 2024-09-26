from core.models.assignments import AssignmentStateEnum, GradeEnum
from unittest.mock import patch

def test_get_assignments(client, h_principal):
    response = client.get(
        '/principal/assignments',
        headers=h_principal
    )
    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]

def test_grade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.C.value
        },
        headers=h_principal
    )

    assert response.status_code == 200
    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.C.value

def test_grade_assignment_draft_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 5,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )

    assert response.status_code == 400
    assert response.json['message'] == "Draft assignment cannot be graded"

def test_grade_assignment_missing_payload(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json=None,
        headers=h_principal
    )

    assert response.status_code == 400
    assert response.json['message'] == "Payload not found"

def test_regrade_assignment(client, h_principal):
    response = client.put(
        '/principal/assignments/4/regrade',
        json={
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 200
    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.B.value

def test_regrade_assignment_not_found(client, h_principal):
    response = client.put(
        '/principal/assignments/9999/regrade',
        json={
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 404
    assert response.json['message'] == "Assignment not found"

def test_regrade_draft_assignment(client, h_principal):
    response = client.put(
        '/principal/assignments/5/regrade',
        json={
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 400
    assert response.json['message'] == "Draft assignment cannot be graded"

def test_list_teachers(client, h_principal):
    response = client.get(
        '/principal/teachers',
        headers=h_principal
    )

    assert response.status_code == 200
    assert 'data' in response.json
    assert isinstance(response.json['data'], list)

    for teacher in response.json['data']:
        assert 'id' in teacher
        assert 'user_id' in teacher
        assert 'created_at' in teacher
        assert 'updated_at' in teacher

def test_grade_assignment_not_found(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 9999,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )

    assert response.status_code == 404
    assert response.json['message'] == "Assignment not found"

def test_grade_assignment_no_payload(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        headers=h_principal
    )

    assert response.status_code == 400
    assert response.json['message'] == "Payload not found"

def test_grade_assignment_generic_error(client, h_principal):
    with patch('core.models.assignments.Assignment.mark_grade', side_effect=Exception("Test error")):
        response = client.post(
            '/principal/assignments/grade',
            json={
                'id': 4,
                'grade': GradeEnum.B.value
            },
            headers=h_principal
        )

    assert response.status_code == 500
    assert response.json['error'] == "ServerError"
    assert response.json['message'] == "Test error"

def test_regrade_assignment_successful(client, h_principal):
    response = client.put(
        '/principal/assignments/4/regrade',
        json={'grade': GradeEnum.A.value},
        headers=h_principal
    )

    assert response.status_code == 200
    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.A.value

def test_list_teachers_empty(client, h_principal):
    with patch('core.models.teachers.Teacher.query') as mock_query:
        mock_query.all.return_value = []
        response = client.get('/principal/teachers', headers=h_principal)

    assert response.status_code == 200
    assert response.json['data'] == []

def test_grade_assignment_missing_id(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={'grade': GradeEnum.A.value},
        headers=h_principal
    )

    assert response.status_code == 400
    assert 'id' in str(response.json['message'])