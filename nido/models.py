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
from sqlalchemy.ext.hybrid import hybrid_property

import enum
import datetime
import decimal

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
    residence_charges = db.relationship(
        "BillingCharge", lazy=True, backref=db.backref("charged_residence", lazy=True)
    )
    recurring_charges = db.relationship(
        "RecurringCharge", lazy=True, backref=db.backref("charged_residence", lazy=True)
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
    direct_charges = db.relationship(
        "BillingCharge", lazy=True, backref=db.backref("charged_user", lazy=True)
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


class BillingCharge(db.Model):
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["user_id", "u_community_id"], ["user.id", "user.community_id"]
        ),
        db.ForeignKeyConstraint(
            ["residence_id", "r_community_id"],
            ["residence.id", "residence.community_id"],
        ),
        db.CheckConstraint("u_community_id = r_community_id"),
        db.CheckConstraint("residence_id is null or user_id is null"),
    )
    id = db.Column(db.Integer, primary_key=True)
    residence_id = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, nullable=True)
    r_community_id = db.Column(db.Integer, nullable=True)
    u_community_id = db.Column(db.Integer, nullable=True)

    name = db.Column(db.String(200), nullable=False)
    base_amount = db.Column(db.Integer, nullable=False)
    paid = db.Column(db.Boolean, nullable=False)
    charge_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return (
            f"BillingCharge("
            f"name={self.name},"
            f"amount={self.amount},"
            f"paid={self.paid},"
            f"charge_date={self.charge_date},"
            f"due_date={self.due_date},"
            f")"
        )

    @hybrid_property
    def amount(self):
        return decimal.Decimal(".01") * self.base_amount

    @property
    def formatted_amount(self):
        return f"${self.amount}"


class Frequency(enum.Enum):
    YEARLY = 1
    MONTHLY = 2
    DAILY = 3


class RecurringCharge(db.Model):
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["user_id", "u_community_id"], ["user.id", "user.community_id"]
        ),
        db.ForeignKeyConstraint(
            ["residence_id", "r_community_id"],
            ["residence.id", "residence.community_id"],
        ),
        db.CheckConstraint("u_community_id = r_community_id"),
        db.CheckConstraint("residence_id is null or user_id is null"),
    )
    id = db.Column(db.Integer, primary_key=True)
    residence_id = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, nullable=True)
    r_community_id = db.Column(db.Integer, nullable=True)
    u_community_id = db.Column(db.Integer, nullable=True)

    name = db.Column(db.String(200), nullable=False)
    base_amount = db.Column(db.Integer, nullable=False)
    frequency = db.Column(db.Enum(Frequency), nullable=False)
    frequency_skip = db.Column(db.Integer, nullable=False, default=1)
    grace_period = db.Column(db.Interval, nullable=False)
    next_charge = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return (
            f"RecurringCharge("
            f"name={self.name},"
            f"amount={self.amount},"
            f"frequency={self.frequency},"
            f"frequency_skip={self.frequency_skip},"
            f"grace_period={self.grace_period},"
            f"next_charge={self.next_charge},"
            f")"
        )

    @hybrid_property
    def amount(self):
        return decimal.Decimal(".01") * self.base_amount

    @property
    def formatted_amount(self):
        return f"${self.amount}"

    def create_charge(self):
        new_charge = BillingCharge(
            name=self.name,
            amount=self.amount,
            paid=False,
            charge_date=self.next_charge,
            due_date=self.next_charge + self.grace_period,
        )
        return new_charge

    def find_next_date(self):
        if self.frequency == Frequency.YEARLY:
            return self.next_charge.replace(
                year=self.next_charge.year + self.frequency_skip
            )
        elif self.frequency == Frequency.MONTHLY:
            next_month = self.next_charge.month + self.frequency_skip
            return self.next_charge.replace(
                year=self.next_charge.year + next_month // 12, month=next_month % 12
            )
        elif self.frequency == Frequency.DAILY:
            return self.next_charge + datetime.timedelta(days=self.frequency_skip)
