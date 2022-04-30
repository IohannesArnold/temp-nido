#  Nido household.py
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

from flask import Blueprint, abort, render_template, redirect, request, url_for
from .auth import login_required, current_user

from .models import db, Residence, ResidenceOccupancy, User

bp = Blueprint("household", __name__)


@bp.route("/")
@login_required
def root():
    occupancies = (
        db.session.query(ResidenceOccupancy)
        .join(Residence)
        .filter(
            ResidenceOccupancy.user_id == current_user.id,
        )
        .order_by(ResidenceOccupancy.is_owner.desc())
        .all()
    )
    if len(occupancies) == 0:
        abort(404)
    return render_template("my_household.html", occupancies=occupancies)
