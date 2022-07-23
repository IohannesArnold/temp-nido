from datetime import date, timedelta
from flask import session
from nido.models import BillingCharge, RecurringCharge


def test_new_valid_charge_is_created(client, session):
    with client.session_transaction() as user_session:
        user_session["user_session_id"] = 1
    old_count = session.query(BillingCharge).count()
    due_date = date.today() + timedelta(days=14)
    client.post(
        "/admin/manage-billing/new-single-charge",
        data={
            "name": "Valid New Charge",
            "amount": "12.34",
            "due": due_date,
            "lookup_id": "u1",
        },
    )

    assert session.query(BillingCharge).count() == old_count + 1


def test_new_valid_recurring_charge_is_created(client, session):
    with client.session_transaction() as user_session:
        user_session["user_session_id"] = 1
    old_count = session.query(RecurringCharge).count()
    start_date = date.today() + timedelta(days=14)
    client.post(
        "/admin/manage-billing/new-recurring-charge",
        data={
            "name": "Valid New Charge",
            "amount": "56.78",
            "grace": "20",
            "starting": start_date,
            "frequency": "MONTHLY",
            "MONTHLY": "6",
            "lookup_id": "u1",
        },
    )

    assert session.query(RecurringCharge).count() == old_count + 1
