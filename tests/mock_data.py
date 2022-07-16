#!/usr/bin/env python
from nido.models import (
    EmergencyContact,
    Community,
    User,
    UserSession,
    Residence,
    Position,
    Authorization,
    RootAuthorization,
    BillingCharge,
    Frequency,
    RecurringCharge,
)
from nido.permissions import Permissions

from datetime import date, timedelta

community_arr = [
    Community(name="Rolfson-Durgan", country="United States"),
]

resident_arr = [
    User(
        personal_name="Rudd",
        family_name="Thom",
        email="rthom0@com.com",
        phone="515-388-2986",
    ),
    User(personal_name="Ammamaria", family_name="Daley", email="adaley1@w3.org"),
    User(personal_name="Lise", family_name="Wittering"),
    User(
        personal_name="Nataline",
        family_name="Dominick",
        email="ndominick3@forbes.com",
        phone="560-735-4098",
    ),
]

residence_arr = [
    Residence(
        unit_no="Unit 1",
        street="97 Oakridge Terrace",
        locality="Bakersfield",
        postcode="93311",
        region="California",
    ),
    Residence(
        unit_no="Unit 2",
        street="97 Oakridge Terrace",
        locality="Bakersfield",
        postcode="93311",
        region="California",
    ),
    Residence(
        unit_no="Unit 3",
        street="97 Oakridge Terrace",
        locality="Bakersfield",
        postcode="93311",
        region="California",
    ),
    Residence(
        unit_no="Unit 4",
        street="97 Oakridge Terrace",
        locality="Bakersfield",
        postcode="93311",
        region="California",
    ),
    Residence(
        unit_no="Unit 5",
        street="97 Oakridge Terrace",
        locality="Bakersfield",
        postcode="93311",
        region="California",
    ),
]
er_arr = [
    EmergencyContact(
        personal_name="Sheena",
        family_name="Hamman",
        email="shamman2c@1688.com",
        phone="133-792-9156",
        relation="Friend",
    )
]


def seed_db(db_session):
    two_weeks = timedelta(days=14)

    for a in residence_arr:
        a.community = community_arr[0]
        billing_charge = BillingCharge(
            name="Example Residence Charge",
            base_amount=1000,
            paid=False,
            charge_date=date.today() - two_weeks,
            due_date=date.today() + two_weeks,
        )
        recurring_charge = RecurringCharge(
            name="Example Monthly Charge",
            base_amount=1000,
            frequency=Frequency.MONTHLY,
            frequency_skip=1,
            grace_period=timedelta(days=10),
            next_charge=date.today().replace(day=1),
        )
        recurring_charge.next_charge = recurring_charge.find_next_date()
        a.residence_charges.append(billing_charge)
        a.recurring_charges.append(recurring_charge)
        db_session.add(a)

    omni = RootAuthorization(name="Omnipotent", id=1, parent_id=1, community_id=1)
    db_session.add(omni)
    board = Position(
        name="Board of Directors",
        min_size=1,
        max_size=3,
        authorization=omni,
        community=community_arr[0],
    )
    db_session.add(board)

    for i, r in enumerate(resident_arr):
        r.community = community_arr[0]
        r.residences.append(residence_arr[i])

        if i < 3:
            board.members.append(r)

        billing_charge = BillingCharge(
            name="Example Personal Charge",
            base_amount=50000,
            paid=False,
            charge_date=date.today() - two_weeks,
            due_date=date.today() + two_weeks,
        )
        late_charge = BillingCharge(
            name="Example Late Charge",
            base_amount=1050,
            paid=False,
            charge_date=date.today() - two_weeks - two_weeks,
            due_date=date.today() - two_weeks,
        )
        user_session = UserSession(user=r)
        db_session.add(user_session)
        r.direct_charges.append(billing_charge)
        r.direct_charges.append(late_charge)
        db_session.add(r)

    sys_admin = Authorization(
        name="Sys Admin", parent=omni, permissions=Permissions.MODIFY_BILLING_SETTINGS
    )
    prez = Position(
        name="President",
        community=community_arr[0],
        min_size=1,
        max_size=1,
        authorization=sys_admin,
    )
    prez.members.append(resident_arr[0])
    db_session.add(prez)

    er_arr[0].user = resident_arr[0]
    db_session.add(er_arr[0])
    db_session.commit()


if __name__ == "__main__":
    from nido import create_app
    from nido.models import Base
    from flask import current_app

    with create_app().app_context():
        db_session = current_app.Session()

        Base.metadata.create_all(bind=db_session.get_bind())
        seed_db(db_session)
