import re
import uuid
from datetime import datetime, timezone

import pytest
import uuid6
from backend.prediction.constants import PredictionStatus, PredictionType
from freezegun import freeze_time

from tests.backend.conftest import get_auth_userdo
from tests.backend.prediction.factories import PredictionFactory
from tests.backend.question.factories import QuestionFactory
from tests.backend.user.facories import UserFactory


@freeze_time("2024-01-03")
@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            {
                "title": "Turkey will win Euro 2024",
                "description": "My prediction about football championship",
                "type": PredictionType.BINARY,
                "value": {"binary": True},
                "question_id": "22004aea-b8d8-4dec-97ab-4fe55c0a19ff",
            },
            id="binary-prediction",
        )
    ],
)
async def test_create_prediction(client_fixture, data):
    # Given
    QuestionFactory(id=data["question_id"])
    # When
    response = await client_fixture.post("/api/prediction", json=data)
    # Then
    assert response.status_code == 200
    response_data = response.json()
    identifier = response_data.pop("id")
    owner_id = response_data.pop("owner_id")
    created_at = response_data.pop("created_at")
    published_at = response_data.pop("published_at")

    assert response_data == {
        **data,
        "status": PredictionStatus.DRAFT,
    }
    assert uuid.UUID(identifier)
    assert uuid.UUID(owner_id)
    assert created_at == datetime.now(timezone.utc).strftime(format="%Y-%m-%dT%H:%M:%S")
    assert published_at is None


@pytest.mark.parametrize("client_fixture", [False], indirect=True)
@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            {
                "title": "Turkey will win Euro 2024",
                "type": PredictionType.BINARY,
                "value": {"binary": True},
                "question_id": "22004aea-b8d8-4dec-97ab-4fe55c0a19ff",
            },
            id="minimal-data",
        )
    ],
)
async def test_create_prediction_no_user(client_fixture, data):
    response = await client_fixture.post("/api/prediction", json=data)
    assert response.status_code == 401


async def test_retrieve_prediction(client_fixture):
    prediction = PredictionFactory()
    response = await client_fixture.get(f"/api/prediction/{prediction.id}")
    assert response.status_code == 200
    assert response.json() == PredictionFactory.to_api_response_data(prediction)


async def test_retrieve_nonexistent_prediction(client_fixture):
    fake_id = uuid6.uuid7()
    response = await client_fixture.get(f"/api/prediction/{fake_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Prediction {fake_id} not found"


@pytest.mark.parametrize("client_fixture", [False], indirect=True)
async def test_retrieve_prediction_no_user(client_fixture):
    prediction = PredictionFactory()
    response = await client_fixture.get(f"/api/prediction/{prediction.id}")
    assert response.status_code == 401


@freeze_time("2024-01-03")
@pytest.mark.parametrize(
    "data",
    [
        pytest.param({"title": "Updated prediction title"}, id="update-title"),
        pytest.param({"description": "New description"}, id="update-description"),
        pytest.param({"value": {"binary": False}}, id="update-value"),
        pytest.param({"status": PredictionStatus.PUBLISHED}, id="update-status"),
        pytest.param(
            {
                "title": "Full update",
                "description": "New description",
                "value": {"binary": False},
                "status": PredictionStatus.PUBLISHED,
            },
            id="full-update",
        ),
    ],
)
async def test_update_prediction(client_fixture, data):
    # Given
    prediction = PredictionFactory(owner=await get_auth_userdo(), status=PredictionStatus.DRAFT)
    # When
    response = await client_fixture.patch(f"/api/prediction/{prediction.id}", json=data)
    # Then
    assert response.status_code == 200
    for key, value in data.items():
        setattr(prediction, key, value)
    if data.get("status") == PredictionStatus.PUBLISHED:
        setattr(prediction, "published_at", datetime.now())
    assert response.json() == PredictionFactory.to_api_response_data(prediction)


async def test_update_prediction_wrong_user(client_fixture):
    other_user = UserFactory()
    prediction = PredictionFactory(owner=other_user)

    response = await client_fixture.patch(f"/api/prediction/{prediction.id}", json={"title": "Unauthorized update"})

    assert response.status_code == 403
    assert re.match(r"User [0-9a-f-]{36} is not allowed to update prediction [0-9a-f-]{36}", response.json()["detail"])


async def test_update_non_draft_prediction(client_fixture):
    user = await get_auth_userdo()
    prediction = PredictionFactory(owner=user, status=PredictionStatus.PUBLISHED)

    response = await client_fixture.patch(
        f"/api/prediction/{prediction.id}", json={"title": "Should fail", "value": {"binary": False}}
    )

    assert response.status_code == 403
    assert "Cannot change the title, description, value" in response.json()["detail"]


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            {"query_params": {"status": PredictionStatus.DRAFT}, "nb_expected_results": 2},
            id="status_draft",
        ),
        pytest.param(
            {"query_params": {"status": PredictionStatus.PUBLISHED}, "nb_expected_results": 1},
            id="status_created",
        ),
        pytest.param(
            {"query_params": {"type": PredictionType.BINARY}, "nb_expected_results": 3},
            id="type_binary",
        ),
        pytest.param(
            {
                "query_params": {"status": PredictionStatus.DRAFT, "type": PredictionType.BINARY},
                "nb_expected_results": 2,
            },
            id="status_draft_and_type_binary",
        ),
        pytest.param(
            {"query_params": {}, "nb_expected_results": 3},
            id="all",
        ),
    ],
)
async def test_list_predictions(client_fixture, data):
    # Given
    user = await get_auth_userdo()
    PredictionFactory.create_batch(2, owner=user, status=PredictionStatus.DRAFT)
    PredictionFactory(owner=user, status=PredictionStatus.PUBLISHED)
    # When
    response = await client_fixture.get("/api/prediction/", params=data["query_params"])
    # Then
    assert response.status_code == 200
    results = response.json()
    assert len(results) == data["nb_expected_results"]
    for result in results:
        if "status" in data["query_params"]:
            assert result["status"] == data["query_params"]["status"]
        if "type" in data["query_params"]:
            assert result["type"] == data["query_params"]["type"]


@pytest.mark.parametrize("client_fixture", [False], indirect=True)
async def test_list_predictions_no_user(client_fixture):
    PredictionFactory.create_batch(2)
    response = await client_fixture.get("/api/prediction/")
    assert response.status_code == 401
