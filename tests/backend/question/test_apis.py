# import uuid

# import pytest


# @pytest.mark.parametrize(
#     "data",
#     [
#         pytest.param(
#             {
#                 "title": "My great question",
#                 "description": "What will my familly cook for chrismass ?",
#                 "prediction_type": "binary",
#             },
#             id="default",
#         )
#     ],
# )
# async def test_create_question(client_fixture, data):
#     # When
#     response = await client_fixture.post("/api/question", json=data)
#     # Then
#     assert response.status_code == 200
#     response_data = response.json()
#     identifier = response_data.pop("id")
#     owner_idenfier = response_data.pop("owner_id")
#     status = response_data.pop("status")
#     assert response_data == data
#     assert uuid.UUID(identifier)
#     assert uuid.UUID(owner_idenfier)
#     assert status == "draft"


# async def test_retrieve_question(client_fixture):
#     user = await UserFactory()
#     question = QuestionFactory()
#     assert user == 42
