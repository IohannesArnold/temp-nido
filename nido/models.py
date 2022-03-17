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

    def __repr__(self):
        return "<Community %r>" % self.name


class Residence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey("community.id"), nullable=False)

    unit_no = db.Column(db.String(40))
    street = db.Column(db.String(80), nullable=False)
    locality = db.Column(db.String(40), nullable=False)
    postcode = db.Column(db.String(20), nullable=False)
    region = db.Column(db.String(40), nullable=False)
    ownership_stake = db.Column(db.Numeric(3, 10))

    occupants = db.relationship(
        "User", lazy=True, backref=db.backref("residence", lazy=True)
    )

    def __repr__(self):
        return "<Residence %r %r>" % self.unit_no, self.street


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey("community.id"), nullable=False)
    residence_id = db.Column(db.Integer, db.ForeignKey("residence.id"), nullable=False)

    personal_name = db.Column(db.String(80), nullable=False)
    family_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True)
    phone = db.Column(db.String(40), unique=True)

    er_contacts = db.relationship(
        "EmergencyContact", lazy=True, backref=db.backref("user", lazy=True)
    )

    def __repr__(self):
        return "<User %r %r>" % self.personal_name, self.family_name

    def is_authenticated(self):
        return True


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
        return "<ERContact %r %r>" % self.first_name, self.last_name
