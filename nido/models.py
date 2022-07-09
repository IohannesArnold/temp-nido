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

from flask import current_app
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
import sqlalchemy.orm as orm
import sqlalchemy.types as sql_types
import sqlalchemy.schema as sql_schema
import sqlalchemy.sql.expression as sql_expr

import enum
import datetime
import decimal

Base = orm.declarative_base()


class Community(Base):
    __tablename__ = "community"

    id = Column(sql_types.Integer, primary_key=True)

    name = Column(sql_types.String(120), nullable=False)
    country = Column(sql_types.String(80), nullable=False)
    issue_handler = Column(sql_types.String(20))
    issue_config = Column(sql_types.JSON())

    residences = orm.relationship(
        "Residence", lazy=True, backref=orm.backref("community", lazy=True)
    )
    members = orm.relationship(
        "User", lazy=True, backref=orm.backref("community", lazy=True)
    )
    positions = orm.relationship(
        "Position", lazy=True, backref=orm.backref("community", lazy=True)
    )
    abilities = orm.relationship(
        "Authorization", lazy=True, backref=orm.backref("community", lazy=True)
    )

    def __repr__(self):
        return f"Community(name={self.name}, country={self.country})"


class IssueHandler(Base):
    __table__ = Community.__table__
    __mapper_args__ = {
        "include_properties": ["id", "issue_handler", "issue_config"],
        "polymorphic_on": "issue_handler",
    }

    def issue_categories(self):
        return None

    def custom_submit_form(self):
        return None

    def handle_new_submission(self, issue_subject, issue_body, issue_category=None):
        pass


class Residence(Base):
    __tablename__ = "residence"
    __table_args__ = (sql_schema.UniqueConstraint("id", "community_id"),)

    id = Column(sql_types.Integer, primary_key=True)
    community_id = Column(sql_types.Integer, ForeignKey("community.id"), nullable=False)

    unit_no = Column(sql_types.String(40))
    street = Column(sql_types.String(80), nullable=False)
    locality = Column(sql_types.String(40), nullable=False)
    postcode = Column(sql_types.String(20), nullable=False)
    region = Column(sql_types.String(40), nullable=False)
    ownership_stake = Column(sql_types.Numeric(3, 10))

    occupants = orm.relationship(
        "User",
        secondary="residence_occupancy",
        lazy=True,
        backref=orm.backref("residences", lazy=True),
    )
    residence_charges = orm.relationship(
        "BillingCharge", lazy=True, backref=orm.backref("charged_residence", lazy=True)
    )
    recurring_charges = orm.relationship(
        "RecurringCharge",
        lazy=True,
        backref=orm.backref("charged_residence", lazy=True),
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


class ResidenceOccupancy(Base):
    __tablename__ = "residence_occupancy"
    __table_args__ = (
        sql_schema.ForeignKeyConstraint(
            ["user_id", "u_community_id"], ["user.id", "user.community_id"]
        ),
        sql_schema.ForeignKeyConstraint(
            ["residence_id", "r_community_id"],
            ["residence.id", "residence.community_id"],
        ),
        sql_schema.CheckConstraint("u_community_id = r_community_id"),
    )

    residence_id = Column(sql_types.Integer, nullable=False, primary_key=True)
    user_id = Column(sql_types.Integer, nullable=False, primary_key=True)
    r_community_id = Column(sql_types.Integer, nullable=False)
    u_community_id = Column(sql_types.Integer, nullable=False)
    relationship_name = Column(sql_types.String(40), nullable=False, default="Occupant")
    is_owner = Column(sql_types.Boolean, nullable=False, default=False)

    residence = orm.relationship("Residence", lazy=True, viewonly=True)
    user = orm.relationship("User", lazy=True, viewonly=True)

    def __repr__(self):
        return "ResidenceOccupancy()"


user_positions = Table(
    "user_positions",
    Base.metadata,
    Column("user_id", sql_types.Integer, ForeignKey("user.id"), primary_key=True),
    Column(
        "position_id", sql_types.Integer, ForeignKey("position.id"), primary_key=True
    ),
)


class Position(Base):
    __tablename__ = "position"
    __table_args__ = (sql_schema.UniqueConstraint("id", "community_id"),)

    id = Column(sql_types.Integer, primary_key=True)
    community_id = Column(sql_types.Integer, ForeignKey("community.id"), nullable=False)
    authorization_id = Column(
        sql_types.Integer, ForeignKey("authorization.id"), nullable=False
    )

    name = Column(sql_types.String(80), nullable=False)
    max_size = Column(sql_types.Integer, nullable=True)
    min_size = Column(sql_types.Integer, nullable=True)

    members = orm.relationship(
        "User",
        lazy=True,
        secondary=user_positions,
        backref=orm.backref("positions", lazy=True),
    )

    def __repr__(self):
        return f"Position(" f"name={self.name}," f"max_size={self.max_size}" f")"

    @orm.validates("members", include_removes=True)
    def validate_members(self, _key, member, is_remove):
        if (
            not is_remove
            and self.max_size
            and self.max_size
            <= current_app.Session.query(user_positions)
            .filter_by(position_id=self.id)
            .distinct()
            .count()
        ):
            raise Exception

        if (
            is_remove
            and self.min_size
            and self.min_size
            >= current_app.Session.query(user_positions)
            .filter_by(position_id=self.id)
            .distinct()
            .count()
        ):
            raise Exception

        return member


class Authorization(Base):
    __tablename__ = "authorization"
    __table_args__ = (sql_schema.UniqueConstraint("id", "community_id"),)

    id = Column(sql_types.Integer, primary_key=True)
    community_id = Column(sql_types.Integer, ForeignKey("community.id"), nullable=False)
    parent_id = Column(sql_types.Integer, ForeignKey("authorization.id"))

    name = Column(sql_types.String(80), nullable=False)

    positions = orm.relationship(
        "Position",
        lazy=True,
        backref=orm.backref("authorization", lazy=True),
    )
    children = orm.relationship(
        "Authorization",
        lazy=True,
        backref=orm.backref("parent", lazy=True, remote_side=[id]),
    )

    __mapper_args__ = {
        "polymorphic_on": sql_expr.case(
            (parent_id == None, "root_authorization"),
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


class User(Base):
    __tablename__ = "user"
    __table_args__ = (sql_schema.UniqueConstraint("id", "community_id"),)

    id = Column(sql_types.Integer, primary_key=True)
    community_id = Column(sql_types.Integer, ForeignKey("community.id"), nullable=False)

    personal_name = Column(sql_types.String(80), nullable=False)
    family_name = Column(sql_types.String(80), nullable=False)
    email = Column(sql_types.String(80), unique=True)
    phone = Column(sql_types.String(40), unique=True)

    er_contacts = orm.relationship(
        "EmergencyContact", lazy=True, backref=orm.backref("user", lazy=True)
    )
    direct_charges = orm.relationship(
        "BillingCharge", lazy=True, backref=orm.backref("charged_user", lazy=True)
    )
    login_sessions = orm.relationship(
        "UserSession", lazy=True, backref=orm.backref("user", lazy=True)
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


class UserSession(Base):
    __tablename__ = "user_session"
    __table_args__ = (
        sql_schema.ForeignKeyConstraint(
            ["user_id", "community_id"], ["user.id", "user.community_id"]
        ),
        {"sqlite_autoincrement": True},
    )

    id = Column(
        sql_types.Integer, sql_schema.Identity(start=100, cycle=True), primary_key=True
    )
    user_id = Column(sql_types.Integer, nullable=False)
    community_id = Column(sql_types.Integer, nullable=False)
    last_activity = Column(
        sql_types.DateTime, nullable=False, server_default=func.now()
    )


class EmergencyContact(Base):
    __tablename__ = "er_contact"
    id = Column(sql_types.Integer, primary_key=True)
    user_id = Column(sql_types.Integer, ForeignKey("user.id"), nullable=False)
    personal_name = Column(sql_types.String(80), nullable=False)
    family_name = Column(sql_types.String(80), nullable=False)
    relation = Column(sql_types.String(80), nullable=False)
    email = Column(sql_types.String(80))
    phone = Column(sql_types.String(40))
    notes = Column(sql_types.Text)

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


class BillingCharge(Base):
    __tablename__ = "billing_charge"
    __table_args__ = (
        sql_schema.ForeignKeyConstraint(
            ["user_id", "u_community_id"], ["user.id", "user.community_id"]
        ),
        sql_schema.ForeignKeyConstraint(
            ["residence_id", "r_community_id"],
            ["residence.id", "residence.community_id"],
        ),
        sql_schema.CheckConstraint("u_community_id = r_community_id"),
        sql_schema.CheckConstraint("residence_id is null or user_id is null"),
    )
    id = Column(sql_types.Integer, primary_key=True)
    residence_id = Column(sql_types.Integer, nullable=True)
    user_id = Column(sql_types.Integer, nullable=True)
    r_community_id = Column(sql_types.Integer, nullable=True)
    u_community_id = Column(sql_types.Integer, nullable=True)

    name = Column(sql_types.String(200), nullable=False)
    base_amount = Column(sql_types.Integer, nullable=False)
    paid = Column(sql_types.Boolean, nullable=False)
    charge_date = Column(sql_types.Date, nullable=False)
    due_date = Column(sql_types.Date, nullable=False)

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


class RecurringCharge(Base):
    __tablename__ = "recurring_charge"
    __table_args__ = (
        sql_schema.ForeignKeyConstraint(
            ["user_id", "u_community_id"], ["user.id", "user.community_id"]
        ),
        sql_schema.ForeignKeyConstraint(
            ["residence_id", "r_community_id"],
            ["residence.id", "residence.community_id"],
        ),
        sql_schema.CheckConstraint("u_community_id = r_community_id"),
        sql_schema.CheckConstraint("residence_id is null or user_id is null"),
    )
    id = Column(sql_types.Integer, primary_key=True)
    residence_id = Column(sql_types.Integer, nullable=True)
    user_id = Column(sql_types.Integer, nullable=True)
    r_community_id = Column(sql_types.Integer, nullable=True)
    u_community_id = Column(sql_types.Integer, nullable=True)

    name = Column(sql_types.String(200), nullable=False)
    base_amount = Column(sql_types.Integer, nullable=False)
    frequency = Column(sql_types.Enum(Frequency), nullable=False)
    frequency_skip = Column(sql_types.Integer, nullable=False, default=1)
    grace_period = Column(sql_types.Interval, nullable=False)
    next_charge = Column(sql_types.Date, nullable=False)

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
