from flask import session


def test_contacts_show_up(client):
    with client.session_transaction() as session:
        session["user_session_id"] = 1
    response = client.get("/emergency-contacts/")
    assert b"Sheena Hamman" in response.data
