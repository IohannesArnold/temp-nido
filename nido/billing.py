#  Nido billing.py
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

from flask import Blueprint, abort, current_app, render_template, request
from .auth import login_required, current_user

from .models import BillingCharge, ResidenceOccupancy, RecurringCharge

from datetime import date

bill_bp = Blueprint("billing", __name__)


@bill_bp.route("/")
@login_required
def root():
    today = date.today()
    current_charges = (
        current_app.Session.query(BillingCharge)
        .outerjoin(
            ResidenceOccupancy,
            BillingCharge.residence_id == ResidenceOccupancy.residence_id,
        )
        .filter(
            (BillingCharge.user_id == current_user.id)
            | (
                (ResidenceOccupancy.user_id == current_user.id)
                & (ResidenceOccupancy.is_owner == True)
            )
        )
        .filter(
            BillingCharge.charge_date <= today,
            BillingCharge.paid == False,
        )
        .order_by(BillingCharge.due_date)
        .all()
    )
    recurring_charges = (
        current_app.Session.query(RecurringCharge)
        .outerjoin(
            ResidenceOccupancy,
            RecurringCharge.residence_id == ResidenceOccupancy.residence_id,
        )
        .filter(
            (RecurringCharge.user_id == current_user.id)
            | (
                (ResidenceOccupancy.user_id == current_user.id)
                & (ResidenceOccupancy.is_owner == True)
            )
        )
        .all()
    )

    return render_template(
        "billing.html",
        today=today,
        current_charges=current_charges,
        recurring_charges=recurring_charges,
    )
