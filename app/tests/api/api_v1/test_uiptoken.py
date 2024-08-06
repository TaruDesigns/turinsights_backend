from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings

"""
def test_fetch_token_withoutcrud(client: TestClient, db: Session) -> None:
    data = {"cruddb": False}
    response = client.post(
        f"{settings.API_V1_STR}/uipath/auth/fetch",
        data=data,
    )
    assert response.status_code == 201
    content = response.json()
    # assert content["title"] == data["title"]
    # assert content["description"] == data["description"]
    # assert "access_token" in content


def test_fetch_token_withcrud(client: TestClient, db: Session) -> None:
    data = {"cruddb": True}
    response = client.post(
        f"{settings.API_V1_STR}/uipath/auth/fetch",
        data=data,
    )
    assert response.status_code == 201
    content = response.json()
    # assert content["title"] == data["title"]
    # assert content["description"] == data["description"]
    # assert "access_token" in content
"""
