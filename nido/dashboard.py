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

from flask import Blueprint, render_template, redirect, url_for
from .auth import login_required

dash_bp = Blueprint("dash", __name__)


@dash_bp.route("/")
@login_required
def index():
    return redirect(url_for(".dashboard"))


@dash_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")
