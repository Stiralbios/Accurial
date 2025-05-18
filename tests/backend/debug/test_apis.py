class TestApisClass:
    async def test_get_status(self, client_fixture):
        # When
        response = await client_fixture.get("/api/debug/healthcheck/status")
        # Then
        assert response.status_code == 200
        assert response.json() == {
            "stack": {"python": "3.12.10 (main, Apr  8 2025, 11:35:47) [GCC 14.2.1 20250322]"},
            "status": "ok",
        }
