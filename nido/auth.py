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

from flask import Blueprint, g, render_template, redirect, request, url_for, session

from .models import User

auth_bp = Blueprint("auth", __name__)


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
