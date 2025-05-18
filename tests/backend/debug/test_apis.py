class TestApisClass:
    async def test_get_status(self, client_fixture):
        # When
        response = await client_fixture.get("/api/debug/healthcheck/status")
        # Then
        assert response.status_code == 200
        assert response.json() == {
            "stack": {"python": "3.12.7 (main, Nov 12 2024, 05:03:56) [GCC 10.2.1 20210110]"},
            "status": "ok",
        }
