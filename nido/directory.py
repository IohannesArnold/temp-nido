#  Nido directory.py
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

from flask import Blueprint, current_app, render_template, request
from sqlalchemy.orm import joinedload
from .auth import login_required, get_community_id

from .models import Community, Residence, User

directory_bp = Blueprint("directory", __name__)


@directory_bp.route("/")
@login_required
def root():
    community_id = get_community_id()
    hide = request.args.get("hide_vacant", False)
    try:
        page = int(request.args.get("p"))
    except:
        page = 0

    community_name = (
        current_app.Session.query(Community.name).filter_by(id=community_id).scalar()
    )
    show_street = (
        current_app.Session.query(Residence.street)
        .filter_by(community_id=community_id)
        .distinct()
        .count()
        != 1
    )
    listings = (
        current_app.Session.query(Residence)
        .options(joinedload(Residence.occupants, innerjoin=hide))
        .filter_by(community_id=community_id)
        .order_by(Residence.unit_no)
        .limit(15)
        .offset(15 * page)
        .all()
    )
    return render_template(
        "directory.html",
        community_name=community_name,
        listings=listings,
        page=page,
        show_street=show_street,
        hide_vacant=hide,
    )
