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

from flask import Blueprint, render_template, request
from .auth import login_required, current_user

from .models import db, Residence, User

directory_bp = Blueprint("directory", __name__)


@directory_bp.route("/")
@login_required
def root():
    hide = request.args.get("hide_vacant")
    try:
        page = int(request.args.get("p"))
    except:
        page = None

    show_street = (
        db.session.query(Residence.street)
        .filter_by(community_id=current_user.community_id)
        .distinct()
        .count()
        != 1
    )
    q_opts = db.joinedload(Residence.occupants)

    listings = Residence.query.options(q_opts).filter_by(
        community_id=current_user.community_id
    )
    if hide:
        # TODO figure out how to filter units without occupants
        pass

    listings = listings.paginate(page=page, max_per_page=15)
    return render_template(
        "directory.html",
        listings_page=listings,
        show_street=show_street,
        hide_vacant=hide,
    )
