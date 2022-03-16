import pytest

from nido import create_app


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_no_user_redirect(client):
    response = client.get("/")
    assert response.status_code == 302


def test_user_login(client):
    response = client.post("/login", data={"ident": "Test"}, follow_redirects=True)
    assert b"Hello, Test" in response.data
