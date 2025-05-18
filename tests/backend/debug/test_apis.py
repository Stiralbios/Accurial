class TestApisClass:
    async def test_get_status(self, client_fixture):
        # When
        response = await client_fixture.get("/api/debug/healthcheck/status")
        # Then
        assert response.status_code == 200
        assert response.json() == {
            "stack": {"python": "3.12.10 (main, May  9 2025, 23:47:03) [GCC 10.2.1 20210110]"},
            "status": "ok",
        }
