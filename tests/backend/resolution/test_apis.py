import uuid

import pytest
from backend.question.constants import QuestionStatus
from backend.question.stores import QuestionStore
from backend.resolution.stores import ResolutionStore

from tests.backend.conftest import get_auth_userdo
from tests.backend.question.factories import QuestionFactory
from tests.backend.resolution.factories import ResolutionFactory


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            {
                "question_id": "123e4567-e89b-12d3-a456-426614174000",
                "date": "2024-12-25T12:00:00Z",
                "value": "true",
                "description": "See link: http://127.0.0.1",
            },
            id="default",
        )
    ],
)
async def test_create_resolution(client_fixture, data):
    question = QuestionFactory(owner=await get_auth_userdo(), status=QuestionStatus.OPEN)
    data["question_id"] = str(question.id)
    response = await client_fixture.post("/api/resolutions", json=data)
    assert response.status_code == 200
    response_data = response.json()
    identifier = response_data.pop("id")
    owner_idenfier = response_data.pop("owner_id")
    assert response_data["question_id"] == data["question_id"]
    assert response_data["value"] == data["value"]
    assert response_data["description"] == data["description"]
    assert uuid.UUID(identifier)
    assert uuid.UUID(owner_idenfier)
    updated_question = await QuestionStore.retrieve(question.id)
    assert updated_question.status == QuestionStatus.CLOSED


@pytest.mark.parametrize("client_fixture", [False], indirect=True)
async def test_create_resolution_no_user(client_fixture):
    question = QuestionFactory(status=QuestionStatus.OPEN)
    data = {
        "question_id": str(question.id),
        "date": "2024-12-25T12:00:00Z",
        "value": "true",
        "description": "See link: http://127.0.0.1",
    }
    response = await client_fixture.post("/api/resolutions", json=data)
    assert response.status_code == 401


async def test_create_resolution_user_not_allowed(client_fixture):
    question = QuestionFactory(status=QuestionStatus.OPEN)
    data = {
        "question_id": str(question.id),
        "date": "2024-12-25T12:00:00Z",
        "value": "true",
        "description": "See link: http://127.0.0.1",
    }
    response = await client_fixture.post("/api/resolutions", json=data)
    assert response.status_code == 403


async def test_create_resolution_question_not_open(client_fixture):
    question = QuestionFactory(owner=await get_auth_userdo(), status=QuestionStatus.CLOSED)
    data = {
        "question_id": str(question.id),
        "date": "2024-12-25T12:00:00Z",
        "value": "true",
        "description": "See link: http://127.0.0.1",
    }
    response = await client_fixture.post("/api/resolutions", json=data)
    assert response.status_code == 403

    question_check = await QuestionStore.retrieve(question.id)
    assert question_check.status == QuestionStatus.CLOSED


async def test_create_resolution_question_not_found(client_fixture):
    fake_id = uuid.uuid4()
    data = {
        "question_id": str(fake_id),
        "date": "2024-12-25T12:00:00Z",
        "value": "true",
        "description": "See link: http://127.0.0.1",
    }
    response = await client_fixture.post("/api/resolutions", json=data)
    assert response.status_code == 404


async def test_retrieve_resolution(client_fixture):
    resolution = ResolutionFactory()
    response = await client_fixture.get(f"/api/resolutions/{resolution.id}")
    assert response.status_code == 200
    assert response.json() == ResolutionFactory.to_api_response_data(resolution)


@pytest.mark.parametrize("client_fixture", [False], indirect=True)
async def test_retrieve_resolution_no_user(client_fixture):
    resolution = ResolutionFactory()
    response = await client_fixture.get(f"/api/resolutions/{resolution.id}")
    assert response.status_code == 401


async def test_retrieve_resolution_not_found(client_fixture):
    fake_id = uuid.uuid4()
    response = await client_fixture.get(f"/api/resolutions/{fake_id}")
    assert response.status_code == 404


@pytest.mark.parametrize(
    "query_params",
    [
        pytest.param(
            {},
            id="all",
        ),
        pytest.param(
            {"question_id": "123e4567-e89b-12d3-a456-426614174000"},
            id="by_question_id",
        ),
    ],
)
async def test_list_resolutions(client_fixture, query_params):
    question = QuestionFactory()
    resolution = ResolutionFactory(question=question)
    ResolutionFactory.create_batch(2)
    if "question_id" in query_params and query_params["question_id"]:
        query_params["question_id"] = str(question.id)
    response = await client_fixture.get("/api/resolutions", params=query_params)
    assert response.status_code == 200
    if query_params.get("question_id"):
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == str(resolution.id)
    else:
        assert len(response.json()) == 3


@pytest.mark.parametrize("client_fixture", [False], indirect=True)
async def test_list_resolutions_no_user(client_fixture):
    ResolutionFactory.create_batch(2)
    response = await client_fixture.get("/api/resolutions", params={})
    assert response.status_code == 401


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            {
                "value": "false",
            },
            id="value",
        ),
        pytest.param(
            {
                "description": "Updated description",
            },
            id="description",
        ),
        pytest.param(
            {
                "description": "Updated description",
            },
            id="all_possible_fields",
        ),
    ],
)
async def test_update_resolution(client_fixture, data):
    resolution = ResolutionFactory(owner=await get_auth_userdo())
    response = await client_fixture.patch(f"/api/resolutions/{resolution.id}", json=data)
    assert response.status_code == 200
    for key, value in data.items():
        setattr(resolution, key, value)
    assert response.json() == ResolutionFactory.to_api_response_data(resolution)


@pytest.mark.parametrize("client_fixture", [False], indirect=True)
async def test_update_resolution_no_user(client_fixture):
    resolution = ResolutionFactory()
    data = {"value": "false"}
    response = await client_fixture.patch(f"/api/resolutions/{resolution.id}", json=data)
    assert response.status_code == 401


async def test_update_resolution_wrong_user(client_fixture):
    resolution = ResolutionFactory()
    data = {"value": "false"}
    response = await client_fixture.patch(f"/api/resolutions/{resolution.id}", json=data)
    assert response.status_code == 403


async def test_update_resolution_not_found(client_fixture):
    fake_id = uuid.uuid4()
    data = {"value": "false"}
    response = await client_fixture.patch(f"/api/resolutions/{fake_id}", json=data)
    assert response.status_code == 404


async def test_delete_resolution(client_fixture):
    resolution = ResolutionFactory(owner=await get_auth_userdo())
    response = await client_fixture.delete(f"/api/resolutions/{resolution.id}")
    assert response.status_code == 204

    retrieved_resolution = await ResolutionStore.retrieve(resolution.id)
    assert retrieved_resolution is None


@pytest.mark.parametrize("client_fixture", [False], indirect=True)
async def test_delete_resolution_no_user(client_fixture):
    resolution = ResolutionFactory()
    response = await client_fixture.delete(f"/api/resolutions/{resolution.id}")
    assert response.status_code == 401


async def test_delete_resolution_wrong_user(client_fixture):
    resolution = ResolutionFactory()
    response = await client_fixture.delete(f"/api/resolutions/{resolution.id}")
    assert response.status_code == 403

    retrieved_resolution = await ResolutionStore.retrieve(resolution.id)
    assert retrieved_resolution is not None


async def test_delete_resolution_not_found(client_fixture):
    fake_id = uuid.uuid4()
    response = await client_fixture.delete(f"/api/resolutions/{fake_id}")
    assert response.status_code == 404
