async def test_get_status(client_fixture):
    # When
    response = await client_fixture.get("/api/debug/healthcheck/status")
    # Then
    assert response.status_code == 200
    assert response.json() == {
        "stack": {"python": "3.12.12 (main, Oct  9 2025, 11:07:00) [GCC 15.2.0]"},
        "status": "ok",
    }
