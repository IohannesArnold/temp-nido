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

from .models import User, UserSession, Position, user_positions, Authorization


## Create functions to get id of active user and community
def get_user_id():
    if "user_id" not in g:
        try:
            session_id = session["user_session_id"]
        except:
            return None
        try:
            redis_result = current_app.redis.get(f"user_session:{session_id}:user_id")
        except:
            redis_result = None

        if redis_result is None:
            (user_id, community_id) = (
                current_app.Session.query(UserSession.user_id, UserSession.community_id)
                .filter(UserSession.id == session["user_session_id"])
                .one()
            )
            g.user_id = user_id
            g.community_id = community_id
            try:
                current_app.redis.set(f"user_session:{session_id}:user_id", user_id)
                current_app.redis.set(
                    f"user_session:{session_id}:community_id", community_id
                )
            except:
                pass
        else:
            g.user_id = int(redis_result)
    return g.user_id


def get_community_id():
    if "community_id" not in g:
        try:
            session_id = session["user_session_id"]
        except:
            return None
        try:
            redis_result = current_app.redis.get(
                f"user_session:{session_id}:community_id"
            )
        except:
            redis_result = None

        if redis_result is None:
            (user_id, community_id) = (
                current_app.Session.query(UserSession.user_id, UserSession.community_id)
                .filter(UserSession.id == session["user_session_id"])
                .one()
            )
            g.user_id = user_id
            g.community_id = community_id
            try:
                current_app.redis.set(f"user_session:{session_id}:user_id", user_id)
                current_app.redis.set(
                    f"user_session:{session_id}:community_id", community_id
                )
            except:
                pass
        else:
            g.community_id = int(redis_result)
    return g.community_id


## Create login_required attribute
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if get_user_id() is None:
            session.pop("user_session_id", None)
            session["next"] = request.url
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


## Create function to check if a giver user is an admin
def is_admin(community_id, user_id):
    return (
        current_app.Session.query(Position)
        .filter_by(community_id=community_id)
        .join(user_positions)
        .filter_by(user_id=user_id)
        .join(Authorization)
        .count()
        > 0
    )


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
