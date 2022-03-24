import pytest
from nido.models import Community, Residence, User
from sqlalchemy.exc import IntegrityError


def test_disjoint_residence_community_and_user_community(db):
    c1 = Community(name="Com1", country="US")
    c2 = Community(name="Com2", country="US")
    u = User(personal_name="Lise", family_name="Wittering")
    r = Residence(
        street="235 Larry Trail", locality="El Paso", postcode="79934", region="TX"
    )

    db.session.add(c1)
    db.session.add(c2)
    c1.members.append(u)
    r.community = c2
    u.residences.append(r)

    db.session.add(u)
    with pytest.raises(IntegrityError):
        db.session.commit()
