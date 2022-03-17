#  Nido er_contacts.py
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

from flask import Blueprint, abort, render_template, request
from .auth import login_required, current_user

from .models import db, EmergencyContact

er_bp = Blueprint("er_contacts", __name__)


@er_bp.route("/", methods=["GET", "POST"])
@login_required
def root():
    if request.method == "POST":
        delete_id = request.form.get("delete_id")
        if delete_id:
            delend = EmergencyContact.query.get(int(delete_id))
            if delend.user != current_user:
                abort(403)
            db.session.delete(delend)
            db.session.commit()
        else:
            f_name = request.form.get("first_name")
            l_name = request.form.get("last_name")
            relation = request.form.get("relation")

            # If not filled out, the form returns an empty string, not None.
            # We want None in the db, so force the conversion (since the
            # empty string is still falsy)
            phone = request.form.get("phone") or None
            email = request.form.get("email") or None
            notes = request.form.get("notes") or None
            new_ec = EmergencyContact(
                personal_name=f_name,
                family_name=l_name,
                relation=relation,
                phone=phone,
                email=email,
                notes=notes,
                user=current_user,
            )
            db.session.add(new_ec)
            db.session.commit()

    return render_template("er_contacts.html")
