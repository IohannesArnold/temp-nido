import pytest
from flask import session
from nido.models import Authorization


def test_authorizations_show_up(client):
    with client.session_transaction() as session:
        session["user_session_id"] = 1
    response = client.get("/admin/edit-authorizations")
    assert b"Omnipotent" in response.data


def test_create_new_valid_authorization(client, session):
    with client.session_transaction() as user_session:
        user_session["user_session_id"] = 1
    client.post(
        "/admin/edit-authorizations/new",
        data={
            "name": "Valid Test",
            "parent_id": "1",
            "MODIFY_BILLING_SETTINGS": "2",
            "MODIFY_ISSUE_SETTINGS": "4",
        },
    )

    assert session.query(Authorization).count() == 3
