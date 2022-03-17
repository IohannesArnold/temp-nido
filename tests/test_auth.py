def test_no_user_redirect(client):
    response = client.get("/")
    assert response.status_code == 302


def test_user_login(client):
    response = client.post(
        "/login", data={"ident": "rthom0@com.com"}, follow_redirects=True
    )
    assert b"Hello Rudd" in response.data
