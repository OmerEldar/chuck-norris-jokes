from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_403():
    response = client.get("/joke")
    assert response.status_code == 403

def test_200():
    response = client.get("/joke", headers={"Authorization": "1111-2222-3333"})
    assert response.status_code == 200
    ## TODO: verify the response