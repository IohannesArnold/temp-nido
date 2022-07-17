#  Nido permissions.py
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
from nido.auth import login_required, get_user_id, get_community_id, is_admin

from nido.models import User, Group, Role, user_groups
from nido.permissions import Permissions
from nido.main_menu import MenuLink

from functools import reduce


def check_edit_role_allowed(role_id):
    subquery = (
        current_app.Session.query(Role.parent_id).filter_by(id=role_id).subquery()
    )
    return (
        current_app.Session.query(Role)
        .filter_by(id=subquery)
        .join(Group)
        .join(user_groups)
        .filter_by(user_id=get_user_id())
        .count()
        > 0
    )


bp = Blueprint("roles", __name__)


@bp.route("/edit-permissions")
@login_required
def edit_roles():
    community_id = get_community_id()
    user_id = get_user_id()
    if not is_admin(community_id, user_id):
        return abort(403)
    roles = (
        current_app.Session.query(Role)
        .filter_by(community_id=community_id)
        .options(selectinload(Role.groups).load_only(Group.name))
        .all()
    )
    parents = (
        current_app.Session.query(Role.id, Role.name)
        .filter_by(community_id=community_id, CAN_DELEGATE=True)
        .join(Group)
        .join(user_groups)
        .filter_by(user_id=user_id)
        .all()
    )
    return render_template(
        "edit-permissions.html",
        roles=roles,
        parents=parents,
        perms=Permissions,
    )


@bp.post("/edit-permissions/new")
@login_required
def create_new_role():
    parent = current_app.Session.get(Role, request.form["parent_id"])
    new = Role(
        name=request.form["name"],
        parent=parent,
        permissions=reduce(
            lambda a, b: a | b,
            [Permissions(int(request.form.get(m.name, 0))) for m in Permissions],
        ),
    )
    current_app.Session.add(new)
    current_app.Session.commit()
    return redirect(url_for(".edit_roles"))


@bp.route("/edit-permissions/<int:role_id>")
@login_required
def edit_single_role(role_id):
    if not check_edit_role_allowed(role_id):
        return abort(403)
    modificand = current_app.Session.get(Role, role_id)
    return render_template(
        "edit-single-perm-role.html", role=modificand, perms=Permissions
    )


@bp.post("/edit-permissions/<int:role_id>")
@login_required
def update_single_role(role_id):
    if not check_edit_role_allowed(role_id):
        return abort(403)
    modificand = current_app.Session.get(Role, role_id)
    modificand.name = request.form["name"]
    for m in Permissions:
        setattr(modificand, m.name, Permissions(int(request.form.get(m.name, 0))))

    current_app.Session.commit()
    return redirect(url_for(".edit_roles"))


@bp.post("/edit-permissions/<int:role_id>/delete")
@login_required
def delete_role(role_id):
    if not check_edit_role_allowed(role_id):
        return abort(403)
    else:
        current_app.Session.query(Role).filter(
            Role.id == role_id, Role.parent_id != Role.id
        ).delete()
        current_app.Session.commit()
    return redirect(url_for(".edit_roles"))
