from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_random_quote():
    response = client.get("/random-quote")
    assert response.status_code == 200


def test_add_quote_form():
    response = client.get("/add-quote")
    assert response.status_code == 200


def test_add_quote():
    response = client.post(
        "/add-quote",
        data={"text": "Test quote", "author": "Test author"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/"
