import sys


async def test_get_status(client_fixture):
    # When
    response = await client_fixture.get("/api/debug/healthcheck/status")
    # Then
    assert response.status_code == 200
    assert response.json() == {
        "stack": {"python": sys.version},
        "status": "ok",
    }
