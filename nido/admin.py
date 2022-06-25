#  Nido admin.py
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

from flask import Blueprint, abort, flash, render_template, redirect, request, url_for
from .auth import login_required, current_user

from .models import db, User, Position, Authorization
from .main_menu import MenuLink

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required
def root():
    if not current_user.is_admin():
        return abort(403)
    menu_list = []
    menu_list.append(MenuLink("Edit Community Positions", url_for(".edit_positions")))
    menu_list.append(
        MenuLink("Edit Position Authorzations", url_for(".edit_authorizations"))
    )
    return render_template("admin.html", menu_list=menu_list)


@admin_bp.route("/edit-positions")
@login_required
def edit_positions():
    if not current_user.is_admin():
        return abort(403)
    positions = Position.query.filter_by(community_id=current_user.community_id).all()
    return render_template("edit-positions.html", positions=positions)


@admin_bp.post("/edit-positions")
@login_required
def edit_positions_post():
    delete_id = request.form.get("delete_id")
    if delete_id:
        delend = db.session.get(Position, int(delete_id))
        if delend.authorization.parent_id is None:
            pass
        elif current_user not in delend.members:
            pass
        else:
            db.session.delete(delend)
    return redirect(url_for(".edit_positions"))


@admin_bp.route("/edit-authorizations")
@login_required
def edit_authorizations():
    if not current_user.is_admin():
        return abort(403)
    authorizations = Authorization.query.filter_by(
        community_id=current_user.community_id
    ).all()
    return render_template("edit-authorizations.html", authorizations=authorizations)


@admin_bp.post("/edit-authorizations")
@login_required
def edit_authorizations_post():
    delete_id = request.form.get("delete_id")
    if delete_id:
        delend = db.session.get(Authorization, int(delete_id))
        if delend.parent_id is None:
            pass
        else:
            db.session.delete(delend)
    return redirect(url_for(".edit_authorizations"))
