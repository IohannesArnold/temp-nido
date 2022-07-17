import pytest
from flask import session
from nido.models import Role


def test_roles_show_up(client):
    with client.session_transaction() as session:
        session["user_session_id"] = 1
    response = client.get("/admin/edit-permissions")
    assert b"Omnipotent" in response.data


def test_new_valid_role_is_created(client, session):
    with client.session_transaction() as user_session:
        user_session["user_session_id"] = 1
    client.post(
        "/admin/edit-permissions/new",
        data={
            "name": "Valid Test",
            "parent_id": "1",
            "MODIFY_BILLING_SETTINGS": "2",
            "MODIFY_ISSUE_SETTINGS": "4",
        },
    )

    assert session.query(Role).count() == 3


def test_new_invalid_role_from_no_delegate_parent_raises_err(client):
    with client.session_transaction() as user_session:
        user_session["user_session_id"] = 1
    with pytest.raises(Exception):
        client.post(
            "/admin/edit-permissions/new",
            data={
                "name": "Invalid Test",
                "parent_id": "2",
                "MODIFY_BILLING_SETTINGS": "2",
                "MODIFY_ISSUE_SETTINGS": "4",
            },
        )
