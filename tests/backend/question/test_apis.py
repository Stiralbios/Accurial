import re
import uuid

import pytest
from backend.question.constants import QuestionStatus

from tests.backend.conftest import get_auth_userdo
from tests.backend.question.factories import QuestionFactory


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            {
                "title": "My great question",
                "description": "What will my familly cook for chrismass ?",
                "prediction_type": "binary",
            },
            id="default",
        )
    ],
)
async def test_create_question(client_fixture, data):
    # When
    response = await client_fixture.post("/api/question", json=data)
    # Then
    assert response.status_code == 200
    response_data = response.json()
    identifier = response_data.pop("id")
    owner_idenfier = response_data.pop("owner_id")
    status = response_data.pop("status")
    assert response_data == data
    assert uuid.UUID(identifier)
    assert uuid.UUID(owner_idenfier)
    assert status == "draft"


@pytest.mark.parametrize("client_fixture", [False], indirect=True)
@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            {
                "title": "My great question",
                "description": "What will my familly cook for chrismass ?",
                "prediction_type": "binary",
            },
            id="default",
        )
    ],
)
async def test_create_question_no_user(client_fixture, data):
    response = await client_fixture.post("/api/question", json=data)
    # Then
    assert response.status_code == 401


async def test_retrieve_question(client_fixture):
    question = QuestionFactory()
    response = await client_fixture.get(f"/api/question/{question.id}")
    assert response.status_code == 200
    assert response.json() == QuestionFactory.to_api_response_data(question)


@pytest.mark.parametrize("client_fixture", [False], indirect=True)
async def test_retrieve_question_no_user(client_fixture):
    question = QuestionFactory()
    response = await client_fixture.get(f"/api/question/{question.id}")
    assert response.status_code == 401


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            {
                "title": "My great question",
            },
            id="title",
        ),
        pytest.param(
            {
                "description": "What will my familly cook for chrismass ?",
            },
            id="description",
        ),
        pytest.param(
            {
                "title": "My great question",
                "description": "What will my familly cook for chrismass ?",
                "prediction_type": "binary",
                "status": QuestionStatus.OPEN,
            },
            id="all_possible_fields",
        ),
    ],
)
async def test_update_question(client_fixture, data):
    question = QuestionFactory(owner=await get_auth_userdo())
    response = await client_fixture.patch(f"/api/question/{question.id}", json=data)
    assert response.status_code == 200
    for key, value in data.items():
        setattr(question, key, value)
    assert response.json() == QuestionFactory.to_api_response_data(question)


@pytest.mark.parametrize("client_fixture", [False], indirect=True)
async def test_update_question_no_user(client_fixture):
    question = QuestionFactory()
    data = {"title": "My great question"}
    response = await client_fixture.patch(f"/api/question/{question.id}", json=data)
    assert response.status_code == 401


async def test_update_question_wrong_user(client_fixture):
    question = QuestionFactory()
    data = {"title": "My great question"}
    response = await client_fixture.patch(f"/api/question/{question.id}", json=data)
    assert response.status_code == 403
    pattern = (
        r"User [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12} is not allowed to update question "
        + str(question.id)
        + "."
    )
    assert re.match(pattern, response.json()["detail"])


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            {"query_params": {"status": QuestionStatus.DRAFT}, "nb_expected_results": 2},
            id="draft",
        ),
        pytest.param(
            {"query_params": {"status": QuestionStatus.OPEN}, "nb_expected_results": 1},
            id="open",
        ),
        pytest.param(
            {"query_params": {}, "nb_expected_results": 3},
            id="all",
        ),
    ],
)
async def test_list_questions(client_fixture, data):
    QuestionFactory.create_batch(2)
    QuestionFactory(status=QuestionStatus.OPEN)
    response = await client_fixture.get("api/question/", params=data["query_params"])
    assert response.status_code == 200
    assert len(response.json()) == data["nb_expected_results"]


@pytest.mark.parametrize("client_fixture", [False], indirect=True)
async def test_list_questions_no_user(client_fixture):
    QuestionFactory.create_batch(2)
    QuestionFactory(status=QuestionStatus.OPEN)
    response = await client_fixture.get("api/question/", params={})
    assert response.status_code == 401


async def test_delete_question(client_fixture):
    question = QuestionFactory(owner=await get_auth_userdo())
    response = await client_fixture.delete(f"/api/question/{question.id}")
    assert response.status_code == 204


@pytest.mark.parametrize("client_fixture", [False], indirect=True)
async def test_delete_question_no_user(client_fixture):
    question = QuestionFactory()
    response = await client_fixture.delete(f"/api/question/{question.id}")
    assert response.status_code == 401


async def test_delete_question_wrong_user(client_fixture):
    question = QuestionFactory()
    response = await client_fixture.delete(f"/api/question/{question.id}")
    assert response.status_code == 403
    pattern = (
        r"User [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12} is not allowed to delete question "
        + str(question.id)
        + "."
    )
    assert re.match(pattern, response.json()["detail"])


async def test_delete_question_not_draft(client_fixture):
    question = QuestionFactory(owner=await get_auth_userdo(), status=QuestionStatus.OPEN)
    response = await client_fixture.delete(f"/api/question/{question.id}")
    assert response.status_code == 403
    assert response.json()["detail"] == f"Question {question.id} isn't in draft, you should archive it"


async def test_delete_question_doesnt_exist(client_fixture):
    response = await client_fixture.delete(f"/api/question/{uuid.uuid4()}")
    assert response.status_code == 404
