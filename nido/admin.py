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

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    render_template,
    redirect,
    request,
    url_for,
)
from sqlalchemy.orm import load_only, selectinload
from .auth import login_required, get_user_id, get_community_id, is_admin

from .models import User, Position, Authorization, user_positions
from .permissions import Permissions
from .main_menu import MenuLink

from functools import reduce


def check_edit_auth_allowed(auth_id):
    subquery = (
        current_app.Session.query(Authorization.parent_id)
        .filter_by(id=auth_id)
        .subquery()
    )
    return (
        current_app.Session.query(Authorization)
        .filter_by(id=subquery)
        .join(Position)
        .join(user_positions)
        .filter_by(user_id=get_user_id())
        .count()
        > 0
    )


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required
def root():
    if not is_admin(get_community_id(), get_user_id()):
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
    community_id = get_community_id()
    if not is_admin(community_id, get_user_id()):
        return abort(403)
    positions = (
        current_app.Session.query(Position).filter_by(community_id=community_id).all()
    )
    return render_template("edit-positions.html", positions=positions)


@admin_bp.post("/edit-positions")
@login_required
def edit_positions_post():
    delete_id = request.form.get("delete_id")
    if delete_id:
        delend = current_app.Session.get(Position, int(delete_id))
        if delend.authorization.parent_id is None:
            pass
        else:
            current_app.Session.delete(delend)
            current_app.Session.commit()
    return redirect(url_for(".edit_positions"))


@admin_bp.route("/edit-authorizations")
@login_required
def edit_authorizations():
    community_id = get_community_id()
    user_id = get_user_id()
    if not is_admin(community_id, user_id):
        return abort(403)
    authorizations = (
        current_app.Session.query(Authorization)
        .filter_by(community_id=community_id)
        .options(selectinload(Authorization.positions).load_only(Position.name))
        .all()
    )
    parents = (
        current_app.Session.query(Authorization.id, Authorization.name)
        .filter_by(community_id=community_id, CAN_DELEGATE=True)
        .join(Position)
        .join(user_positions)
        .filter_by(user_id=user_id)
        .all()
    )
    return render_template(
        "edit-authorizations.html",
        authorizations=authorizations,
        parents=parents,
        perms=Permissions,
    )


@admin_bp.post("/edit-authorizations/new")
@login_required
def create_new_authorization():
    parent = current_app.Session.get(Authorization, request.form["parent_id"])
    new = Authorization(
        name=request.form["name"],
        parent=parent,
        permissions=reduce(
            lambda a, b: a | b,
            [Permissions(int(request.form.get(m.name, 0))) for m in Permissions],
        ),
    )
    current_app.Session.add(new)
    current_app.Session.commit()
    return redirect(url_for(".edit_authorizations"))


@admin_bp.route("/edit-authorizations/<int:auth_id>")
@login_required
def edit_single_authorization(auth_id):
    if not check_edit_auth_allowed(auth_id):
        return abort(403)
    modificand = current_app.Session.get(Authorization, auth_id)
    return render_template(
        "edit-single-authorization.html", auth=modificand, perms=Permissions
    )


@admin_bp.post("/edit-authorizations/<int:auth_id>")
@login_required
def update_single_authorization(auth_id):
    if not check_edit_auth_allowed(auth_id):
        return abort(403)
    modificand = current_app.Session.get(Authorization, auth_id)
    modificand.name = request.form["name"]
    for m in Permissions:
        setattr(modificand, m.name, Permissions(int(request.form.get(m.name, 0))))

    current_app.Session.commit()
    return redirect(url_for(".edit_authorizations"))


@admin_bp.post("/edit-authorizations/<int:auth_id>/delete")
@login_required
def delete_authorization(auth_id):
    if not check_edit_auth_allowed(auth_id):
        return abort(403)
    else:
        current_app.Session.query(Authorization).filter(
            Authorization.id == auth_id, Authorization.parent_id != Authorization.id
        ).delete()
        current_app.Session.commit()
    return redirect(url_for(".edit_authorizations"))
