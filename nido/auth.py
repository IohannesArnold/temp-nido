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

from flask import (
    Blueprint,
    current_app,
    g,
    render_template,
    redirect,
    request,
    url_for,
    session,
)
from werkzeug.local import LocalProxy

from .models import User, UserSession


## Create login_required attribute


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        try:
            current_app.Session.query(UserSession).filter_by(
                id=session["user_session_id"]
            ).one()
        except:
            session.pop("user_session_id", None)
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
        try:
            g.user = (
                current_app.Session.query(User)
                .join(UserSession)
                .filter(UserSession.id == session["user_session_id"])
                .one()
            )
        except:
            g.user = NullUser()
    return g.user


current_user = LocalProxy(lambda: get_user())


## Create blueprint for auth pages


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ident = request.form.get("ident")
        user = current_app.Session.query(User).filter_by(email=ident).first()
        if user:
            new_session = UserSession(user=user)
            current_app.Session.add(new_session)
            current_app.Session.commit()
            session["user_session_id"] = new_session.id
            # The flask-login docs insist that you need to validate the next
            # parameter, but that's for when it's a url query. Since here
            # it's passed as a secure server-generated cookie, this should be fine.
            next_url = session.pop("next", None)

            return redirect(next_url or url_for("index"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    current_app.Session.query(UserSession).filter_by(
        id=session["user_session_id"]
    ).delete()
    current_app.Session.commit()
    session.pop("user_session_id")
    return redirect(url_for("login"))
