#  Nido auth.py
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

import functools

from flask import Blueprint, g, render_template, redirect, request, url_for, session
from werkzeug.local import LocalProxy

from .models import User


## Create login_required attribute


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user_id") is None:
            session["next"] = request.url
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


## Create 'current_user' function for insertion into templates


class NullUser:
    def is_authenticated(self):
        return False


def get_user():
    if "user" not in g:
        session_id = session.get("user_id")
        if session_id:
            try:
                g.user = User.query.get(session_id)
            except:
                g.user = NullUser()
        else:
            g.user = NullUser()
    return g.user


current_user = LocalProxy(lambda: get_user())


## Create blueprint for auth pages


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ident = request.form.get("ident")
        user = User.query.filter_by(email=ident).first()
        if user:
            session["user_id"] = user.id
            return redirect(url_for("index"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.pop("user_id")
    return redirect(url_for("login"))
