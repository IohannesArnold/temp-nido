from nido.models import EmergencyContact, Community, User, Residence

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


def seed_db(db):
    for a in residence_arr:
        a.community = community_arr[0]
        db.session.add(a)

    for i, r in enumerate(resident_arr):
        r.community = community_arr[0]
        r.residence = residence_arr[i]
        db.session.add(r)

    er_arr[0].user = resident_arr[0]
    db.session.add(er_arr[0])

    db.session.commit()
