#!/usr/bin/env python
from nido.models import (
    EmergencyContact,
    Community,
    User,
    Residence,
    Position,
    RootAuthorization,
    BillingCharge,
    Frequency,
    RecurringCharge,
)

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

pos_arr = [Position(name="President", min_size=1, max_size=1)]

omni = RootAuthorization(
    name="Omnipotent",
)


def seed_db(db):
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
        db.session.add(a)

    for i, r in enumerate(resident_arr):
        r.community = community_arr[0]
        r.residences.append(residence_arr[i])
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
        r.direct_charges.append(billing_charge)
        r.direct_charges.append(late_charge)
        db.session.add(r)

    omni.community = community_arr[0]

    for p in pos_arr:
        p.community = community_arr[0]
        p.authorization = omni
        p.members.append(resident_arr[0])
        db.session.add(p)

    er_arr[0].user = resident_arr[0]
    db.session.add(er_arr[0])
    db.session.commit()


if __name__ == "__main__":
    from nido import create_app
    from nido.models import db

    with create_app().app_context():
        db.create_all()
        seed_db(db)
