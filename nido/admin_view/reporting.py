#  Nido admin_view/reporting.py
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
    Markup,
    abort,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)
from nido.auth import login_required, get_community_id, get_user_id, requires_permission
from nido.models import ReportingHandler
from nido.permissions import Permissions

report_bp = Blueprint("reporting", __name__)


@report_bp.route("/manage-reporting")
@login_required
@requires_permission(Permissions.MODIFY_REPORTING_SETTINGS)
def root():
    community_id = get_community_id()
    current_handler = current_app.Session.get(ReportingHandler, community_id)
    possibilities = ReportingHandler.__subclasses__()
    config_form = current_handler.config_form()
    if config_form:
        config_form = Markup(config_form)
    return render_template(
        "manage-reporting.html",
        current_handler=current_handler,
        possibilities=possibilities,
        config_form = config_form,
    )


@report_bp.post("/manage-reporting/change-handler")
@login_required
@requires_permission(Permissions.MODIFY_REPORTING_SETTINGS)
def change_handler():
    community_id = get_community_id()
    current_handler = current_app.Session.get(ReportingHandler, community_id)
    current_handler.reporting_handler = request.form.get("handler_type")
    current_handler.rh_config = current_handler.default_config()
    current_app.Session.add(current_handler)
    current_app.Session.commit()
    # We commit the session and then reload it so that the new_handler object
    # belongs to the correct subclass and returns the correct default_config.
    # TODO: This seems hacky; is there a better way?
    new_handler = current_app.Session.get(ReportingHandler, community_id)
    new_handler.rh_config = new_handler.default_config()
    current_app.Session.add(new_handler)
    current_app.Session.commit()
    return redirect(url_for(".root"))
