#  Nido models.py
#  Copyright (C) 2022 John Arnold
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import case
from sqlalchemy.orm import validates

db = SQLAlchemy()


class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    country = db.Column(db.String(80), nullable=False)

    residences = db.relationship(
        "Residence", lazy=True, backref=db.backref("community", lazy=True)
    )
    members = db.relationship(
        "User", lazy=True, backref=db.backref("community", lazy=True)
    )
    positions = db.relationship(
        "Position", lazy=True, backref=db.backref("community", lazy=True)
    )
    abilities = db.relationship(
        "Authorization", lazy=True, backref=db.backref("community", lazy=True)
    )

    def __repr__(self):
        return f"Community(name={self.name}, country={self.country})"


class Residence(db.Model):
    __table_args__ = (db.UniqueConstraint("id", "community_id"),)

    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey("community.id"), nullable=False)

    unit_no = db.Column(db.String(40))
    street = db.Column(db.String(80), nullable=False)
    locality = db.Column(db.String(40), nullable=False)
    postcode = db.Column(db.String(20), nullable=False)
    region = db.Column(db.String(40), nullable=False)
    ownership_stake = db.Column(db.Numeric(3, 10))

    occupants = db.relationship(
        "User",
        secondary="residence_occupancy",
        lazy=True,
        backref=db.backref("residences", lazy=True),
    )

    def __repr__(self):
        return (
            f"Residence("
            f"unit_no={self.unit_no},"
            f"street={self.street},"
            f"locality={self.locality},"
            f"postcode={self.postcode},"
            f"region={self.region}"
            f")"
        )


class ResidenceOccupancy(db.Model):
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["user_id", "u_community_id"], ["user.id", "user.community_id"]
        ),
        db.ForeignKeyConstraint(
            ["residence_id", "r_community_id"],
            ["residence.id", "residence.community_id"],
        ),
        db.CheckConstraint("u_community_id = r_community_id"),
    )

    residence_id = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, primary_key=True)
    r_community_id = db.Column(db.Integer, nullable=False)
    u_community_id = db.Column(db.Integer, nullable=False)
    relationship_name = db.Column(db.String(40), nullable=False, default="Occupant")
    is_owner = db.Column(db.Boolean, nullable=False, default=False)

    residence = db.relationship("Residence", lazy=True, viewonly=True)
    user = db.relationship("User", lazy=True, viewonly=True)

    def __repr__(self):
        return "ResidenceOccupancy()"


user_positions = db.Table(
    "user_positions",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column(
        "position_id", db.Integer, db.ForeignKey("position.id"), primary_key=True
    ),
)


class Position(db.Model):
    __table_args__ = (db.UniqueConstraint("id", "community_id"),)

    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey("community.id"), nullable=False)
    authorization_id = db.Column(
        db.Integer, db.ForeignKey("authorization.id"), nullable=False
    )

    name = db.Column(db.String(80), nullable=False)
    max_size = db.Column(db.Integer, nullable=True)
    min_size = db.Column(db.Integer, nullable=True)

    members = db.relationship(
        "User",
        lazy=True,
        secondary=user_positions,
        backref=db.backref("positions", lazy=True),
    )

    def __repr__(self):
        return f"Position(" f"name={self.name}," f"max_size={self.max_size}" f")"

    @validates("members", include_removes=True)
    def validate_members(self, _key, member, is_remove):
        if (
            not is_remove
            and self.max_size
            and self.max_size
            <= db.session.query(user_positions)
            .filter_by(position_id=self.id)
            .distinct()
            .count()
        ):
            raise Exception

        if (
            is_remove
            and self.min_size
            and self.min_size
            >= db.session.query(user_positions)
            .filter_by(position_id=self.id)
            .distinct()
            .count()
        ):
            raise Exception

        return member


class Authorization(db.Model):
    __table_args__ = (db.UniqueConstraint("id", "community_id"),)

    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey("community.id"), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("authorization.id"))

    name = db.Column(db.String(80), nullable=False)

    positions = db.relationship(
        "Position",
        lazy=True,
        backref=db.backref("authorization", lazy=True),
    )
    children = db.relationship(
        "Authorization",
        lazy=True,
        backref=db.backref("parent", lazy=True, remote_side=[id]),
    )

    __mapper_args__ = {
        "polymorphic_on": case(
            [
                (parent_id == None, "root_authorization"),
            ],
            else_="authorization",
        ),
        "polymorphic_identity": "authorization",
    }

    def __repr__(self):
        return f"Authorization(" f"name={self.name}" f")"

    def permits(self):
        return False


class RootAuthorization(Authorization):
    __mapper_args__ = {"polymorphic_identity": "root_authorization"}

    def permits(self):
        return True

    def delegate(self, name):
        return Authorization(name=name, parent=self)


class User(db.Model):
    __table_args__ = (db.UniqueConstraint("id", "community_id"),)

    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey("community.id"), nullable=False)

    personal_name = db.Column(db.String(80), nullable=False)
    family_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True)
    phone = db.Column(db.String(40), unique=True)

    er_contacts = db.relationship(
        "EmergencyContact", lazy=True, backref=db.backref("user", lazy=True)
    )

    def __repr__(self):
        return (
            f"User("
            f"personal_name={self.personal_name},"
            f"family_name={self.family_name},"
            f"email={self.email},"
            f"phone={self.phone}"
            f")"
        )

    def is_authenticated(self):
        return True

    def is_admin(self):
        return (
            Position.query.filter_by(community_id=self.community_id)
            .join(user_positions)
            .filter_by(user_id=self.id)
            .join(Authorization)
            .count()
            > 0
        )


class EmergencyContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    personal_name = db.Column(db.String(80), nullable=False)
    family_name = db.Column(db.String(80), nullable=False)
    relation = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80))
    phone = db.Column(db.String(40))
    notes = db.Column(db.Text)

    def __repr__(self):
        return (
            f"EmergencyContact("
            f"personal_name={self.personal_name},"
            f"family_name={self.family_name},"
            f"relation={self.relation},"
            f"email={self.email},"
            f"phone={self.phone},"
            f"notes={self.notes}"
            f")"
        )
