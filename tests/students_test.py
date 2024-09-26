def test_get_assignments_student_1(client, h_student_1):
    response = client.get(
        '/student/assignments',
        headers=h_student_1
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['student_id'] == 1


def test_get_assignments_student_2(client, h_student_2):
    response = client.get(
        '/student/assignments',
        headers=h_student_2
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['student_id'] == 2


def test_post_assignment_null_content(client, h_student_1):
    """
    failure case: content cannot be null
    """

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': None
        })
    
    print(response.json)

    assert response.status_code == 400


def test_post_assignment_student_1(client, h_student_1):
    content = 'ABCD TESTPOST'

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': content
        })

    assert response.status_code == 200

    data = response.json['data']
    assert data['content'] == content
    assert data['state'] == 'DRAFT'
    assert data['teacher_id'] is None


def test_submit_assignment_student_1(client, h_student_1):
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': 2,
            'teacher_id': 2
        })

    assert response.status_code == 200

    data = response.json['data']
    assert data['student_id'] == 1
    assert data['state'] == 'SUBMITTED'
    assert data['teacher_id'] == 2


def test_assignment_resubmit_error(client, h_student_1):
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': 2,
            'teacher_id': 2
        })
    error_response = response.json
    assert response.status_code == 400
    assert error_response['error'] == 'FyleError'
    assert error_response["message"] == 'only a draft assignment can be submitted'


# New Test Cases

def test_view_specific_assignment_student_1(client, h_student_1):
    """
    Success case: Fetch specific assignment
    """
    response = client.get(
        '/student/assignments/1',
        headers=h_student_1
    )

    assert response.status_code == 200
    data = response.json['data']
    assert data['id'] == 1
    assert data['student_id'] == 1


def test_view_specific_assignment_error(client, h_student_1):
    """
    Failure case: Trying to fetch an assignment that doesn't belong to the student
    """
    response = client.get(
        '/student/assignments/999',
        headers=h_student_1
    )

    assert response.status_code == 404


def test_list_submitted_assignments(client, h_student_1):
    """
    Success case: List all submitted assignments for student 1
    """
    response = client.get(
        '/student/assignments/submitted',
        headers=h_student_1
    )

    assert response.status_code == 200
    data = response.json['data']
    for assignment in data:
        assert assignment['state'] == 'SUBMITTED'
        assert assignment['student_id'] == 1


def test_delete_draft_assignment(client, h_student_1):
    """
    Success case: Delete a draft assignment
    """
    # Create a new draft assignment first
    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={'content': 'Draft to delete'}
    )
    assert response.status_code == 200
    assignment_id = response.json['data']['id']

    # Now delete it
    response = client.delete(
        f'/student/assignments/{assignment_id}',
        headers=h_student_1
    )

    assert response.status_code == 200
    assert response.json['message'] == "Assignment deleted successfully."


def test_delete_draft_assignment_error(client, h_student_1):
    """
    Failure case: Try to delete a non-draft assignment
    """
    response = client.delete(
        '/student/assignments/2',  # Assuming ID 2 is not a draft
        headers=h_student_1
    )

    assert response.status_code == 400
    error_response = response.json
    assert error_response["message"] == "Only draft assignments can be deleted"
