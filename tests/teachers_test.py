def test_grade_assignment_not_found(client, h_teacher_1):
    """
    Failure case: Attempt to grade a non-existent assignment should return 404.
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={"id": 9999, "grade": "A"}
    )
    assert response.status_code == 404
    assert response.json['error'] == 'FyleError'


def test_grade_assignment_unauthorized(client, h_teacher_2):
    """
    Failure case: Teacher 2 attempts to grade an assignment assigned to Teacher 1.
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={"id": 1, "grade": "B"}
    )
    assert response.status_code == 400
    assert response.json['error'] == 'FyleError'


def test_grade_assignment_draft(client, h_teacher_1):
    """
    Failure case: Teacher should not be able to grade an assignment that is in draft state.
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={"id": 2, "grade": "C"}  # Assume assignment 2 is a draft
    )
    assert response.status_code == 400
    assert response.json['error'] == 'FyleError'


# Existing tests...


def test_grade_assignment_valid(client, h_teacher_1):
    """
    success case: grading an assignment that the teacher is authorized to grade
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 1,  # Assume this assignment belongs to teacher 1
            "grade": "A"
        }
    )

    assert response.status_code == 200
    data = response.json
    assert data['data']['grade'] == "A"  # Confirm the grade is set correctly


def test_grade_assignment_own_assignment(client, h_teacher_1):
    """
    failure case: teacher cannot grade their own assignments
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 1,  # Assume this assignment was created by teacher 1
            "grade": "B"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'


def test_get_assignment_detail(client, h_teacher_1):
    """
    success case: retrieve details of a specific assignment for the teacher
    """
    response = client.get(
        '/teacher/assignments/1',  # Assuming assignment 1 belongs to teacher 1
        headers=h_teacher_1
    )

    assert response.status_code == 200
    data = response.json['data']
    assert data['id'] == 1
    assert data['teacher_id'] == 1  # Check that it's the correct assignment


def test_get_assignment_detail_unauthorized(client, h_teacher_2):
    """
    failure case: teacher tries to access an assignment they do not own
    """
    response = client.get(
        '/teacher/assignments/1',  # Assuming assignment 1 belongs to teacher 1
        headers=h_teacher_2
    )

    assert response.status_code == 403
    data = response.json
    assert data['error'] == 'FyleError'


def test_grade_assignment_invalid_state(client, h_teacher_2):
    """
    failure case: a teacher tries to grade an assignment in DRAFT state
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={
            "id": 2,  # Assume this assignment is in DRAFT state
            "grade": "A"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_non_existent_assignment(client, h_teacher_1):
    """
    failure case: grading an assignment that does not exist
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 99999,  # A non-existent assignment ID
            "grade": "A"
        }
    )

    assert response.status_code == 404
    data = response.json

    assert data['error'] == 'FyleError'


def test_teacher_access_denied(client, h_student_1):
    """
    failure case: student tries to access teacher-specific assignments
    """
    response = client.get(
        '/teacher/assignments',
        headers=h_student_1  # Using a student header
    )

    assert response.status_code == 403
    data = response.json
    assert data['error'] == 'FyleError'


def test_list_assignments_empty(client, h_teacher_1):
    """
    Test case when there are no assignments for a teacher.
    """
    response = client.get('/teacher/assignments', headers=h_teacher_1)
    assert response.status_code == 200
    assert response.json['data'] == []  # Expecting empty list if no assignments exist.


def test_grade_assignment_valid(client, h_teacher_1):
    """
    Test case for successful grading of an assignment.
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={"id": 1, "grade": "A"}  # Assume assignment 1 belongs to teacher 1
    )
    
    assert response.status_code == 200
    assert response.json['data']['grade'] == "A"  # Ensure the grade was set.


def test_grade_assignment_invalid_state(client, h_teacher_2):
    """
    Failure case for grading an assignment that is still in draft state.
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={"id": 2, "grade": "A"}  # Assume assignment 2 is a draft
    )

    assert response.status_code == 400
    assert response.json['error'] == 'FyleError'


def test_grade_assignment_own_assignment(client, h_teacher_1):
    """
    Failure case: teacher should not be able to grade their own assignment.
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={"id": 1, "grade": "B"}  # Assume assignment 1 was created by teacher 1
    )

    assert response.status_code == 400
    assert response.json['error'] == 'FyleError'


def test_get_assignment_detail(client, h_teacher_1):
    """
    Test case for successfully retrieving assignment details.
    """
    response = client.get('/teacher/assignments/1', headers=h_teacher_1)
    assert response.status_code == 200
    assert response.json['data']['id'] == 1  # Ensure the correct assignment is returned.


def test_get_assignment_detail_not_found(client, h_teacher_1):
    """
    Failure case for retrieving a non-existent assignment.
    """
    response = client.get('/teacher/assignments/999', headers=h_teacher_1)
    assert response.status_code == 404
    assert response.json['error'] == 'FyleError'


def test_get_assignment_detail_unauthorized(client, h_teacher_2):
    """
    Failure case: ensure teacher cannot access another teacher's assignment details.
    """
    response = client.get('/teacher/assignments/1', headers=h_teacher_2)  # Assume this is teacher 2
    assert response.status_code == 403
    assert response.json['error'] == 'FyleError'
