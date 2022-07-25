#  Nido admin_view/billing.py
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
    redirect,
    render_template,
    request,
    url_for,
)
from nido.auth import login_required, get_community_id, get_user_id, requires_permission
from nido.models import BillingCharge, Frequency, Residence, RecurringCharge, User
from nido.permissions import Permissions

from datetime import date, timedelta
import decimal
import functools

bill_bp = Blueprint("billing", __name__)


@bill_bp.route("/manage-billing")
@login_required
@requires_permission(Permissions.MODIFY_BILLING_SETTINGS)
def root():
    user_list = (
        current_app.Session.query(User)
        .filter_by(community_id=get_community_id())
        .order_by(User.family_name)
        .all()
    )
    residence_list = (
        current_app.Session.query(Residence)
        .filter_by(community_id=get_community_id())
        .order_by(Residence.unit_no)
        .all()
    )
    return render_template(
        "manage-billing.html", users=user_list, residences=residence_list
    )


@bill_bp.route("/manage-billing/edit-billing-records")
@login_required
@requires_permission(Permissions.MODIFY_BILLING_SETTINGS)
def billing_records():
    today = date.today()
    lookup_id = int(request.args["lookup_id"][1:])
    current_charges = current_app.Session.query(BillingCharge).order_by(
        BillingCharge.due_date
    )
    recurring_charges = current_app.Session.query(RecurringCharge)
    if request.args["lookup_id"][0] == "u":
        current_charges = current_charges.filter(BillingCharge.user_id == lookup_id)
        recurring_charges = recurring_charges.filter(
            RecurringCharge.user_id == lookup_id
        )
    else:
        current_charges = current_charges.filter(
            BillingCharge.residence_id == lookup_id
        )
        recurring_charges = recurring_charges.filter(
            RecurringCharge.residence_id == lookup_id
        )
    return render_template(
        "edit-billing-records.html",
        today=today,
        current_charges=current_charges.all(),
        recurring_charges=recurring_charges.all(),
        lookup_id=request.args["lookup_id"],
    )


@bill_bp.post("/manage-billing/new-recurring-charge")
@login_required
@requires_permission(Permissions.MODIFY_BILLING_SETTINGS)
def new_recurring_charge():
    lookup_id = int(request.form["lookup_id"][1:])
    new_charge = RecurringCharge(
        name=request.form["name"],
        grace_period=timedelta(days=int(request.form["grace"])),
        base_amount=int(
            decimal.Decimal(request.form["amount"]) / decimal.Decimal(".01")
        ),
        next_charge=date.fromisoformat(request.form["starting"]),
        frequency=Frequency[request.form["frequency"]],
    )
    try:
        new_charge.frequency_skip = int(request.form[new_charge.frequency.name])
    except:
        pass
    if request.form["lookup_id"][0] == "u":
        new_charge.user_id = lookup_id
        new_charge.u_community_id = get_community_id()
    else:
        new_charge.residence_id = lookup_id
        new_charge.r_community_id = get_community_id()
    current_app.Session.add(new_charge)
    current_app.Session.commit()
    return redirect(url_for(".billing_records", lookup_id=request.form["lookup_id"]))


@bill_bp.post("/manage-billing/new-single-charge")
@login_required
@requires_permission(Permissions.MODIFY_BILLING_SETTINGS)
def new_single_charge():
    lookup_id = int(request.form["lookup_id"][1:])
    new_charge = BillingCharge(
        name=request.form["name"],
        base_amount=int(
            decimal.Decimal(request.form["amount"]) / decimal.Decimal(".01")
        ),
        charge_date=date.today(),
        due_date=date.fromisoformat(request.form["due"]),
        paid=False,
    )
    if request.form["lookup_id"][0] == "u":
        new_charge.user_id = lookup_id
        new_charge.u_community_id = get_community_id()
    else:
        new_charge.residence_id = lookup_id
        new_charge.r_community_id = get_community_id()
    current_app.Session.add(new_charge)
    current_app.Session.commit()
    return redirect(url_for(".billing_records", lookup_id=request.form["lookup_id"]))


@bill_bp.post("/manage-billing/delete-charge")
@login_required
@requires_permission(Permissions.MODIFY_BILLING_SETTINGS)
def delete_charge():
    delete_id = int(request.form["delete_id"][1:])
    if request.form["delete_id"][0] == "r":
        delend = RecurringCharge
    else:
        delend = BillingCharge
    current_app.Session.query(delend).filter_by(id=delete_id).delete()
    current_app.Session.commit()

    return redirect(url_for(".billing_records", lookup_id=request.form["lookup_id"]))
