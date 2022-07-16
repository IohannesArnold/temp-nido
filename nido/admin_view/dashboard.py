#  Nido dashboard.py
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

from flask import Blueprint, current_app, render_template, redirect, url_for
from nido.auth import login_required, get_community_id
from nido.models import Community
from nido.main_menu import admin_menu

dash_bp = Blueprint("dash", __name__)


@dash_bp.route("/dashboard")
@login_required
def dashboard():
    community_id = get_community_id()
    community_name = (
        current_app.Session.query(Community.name).filter_by(id=community_id).scalar()
    )
    return render_template("dashboard.html", community_name=community_name)
