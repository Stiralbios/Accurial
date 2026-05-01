async def test_get_status(client_fixture):
    # When
    response = await client_fixture.get("/api/debug/healthcheck/status")
    # Then
    assert response.status_code == 200
    assert response.json() == {
        "stack": {"python": "3.13.11 (main, Dec  5 2025, 16:06:33) [GCC 15.2.0]"},
        "status": "ok",
    }
