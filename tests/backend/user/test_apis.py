import uuid

import pytest

from tests.backend.user.facories import UserFactory


@pytest.mark.parametrize("client_fixture", [False], indirect=True)
@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            {
                "email": "test_user@test.lan",
                "password": "1234",
            },
            id="default",
        )
    ],
)
async def test_create_user(client_fixture, data):
    # When
    response = await client_fixture.post("/api/user", json=data)
    # Then
    assert response.status_code == 200
    response_data = response.json()
    identifier = response_data.pop("id")
    is_active = response_data.pop("is_active")

    assert response_data == {"email": data["email"]}
    assert uuid.UUID(identifier)
    assert is_active is True
    # await UserFactory()


@pytest.mark.parametrize("client_fixture", [False], indirect=True)
async def test_list_user(client_fixture):
    users = UserFactory.create_batch(3)
    response = await client_fixture.get("/api/user/")
    assert response.status_code == 200
    assert response.json() == UserFactory.to_api_response_data(users)


async def test_get_user_me(client_fixture):
    response = await client_fixture.get("/api/user/me")
    # Then
    assert response.status_code == 200
    assert response.json()["email"] == "admin@test.lan"


async def test_get_user(client_fixture):
    user = UserFactory()
    response = await client_fixture.get(f"/api/user/{user.id}")
    assert response.status_code == 200
    assert response.json() == UserFactory.to_api_response_data(user)
