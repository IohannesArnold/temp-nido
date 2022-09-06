#  Nido issue.py
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

from flask import Blueprint, Markup, current_app, render_template, request
import sqlalchemy.sql.expression as sql_expr
from email.headerregistry import Address
from email.message import EmailMessage
from email import policy

from .auth import login_required, get_community_id
from .email import send_email
from .models import ReportingHandler


class ReportingDisabled(ReportingHandler):
    __mapper_args__ = {"polymorphic_identity": "disabled"}

    @classmethod
    def display_name(cls):
        return "Disabled"


class EmailIssue(ReportingHandler):
    __mapper_args__ = {"polymorphic_identity": "email"}

    @classmethod
    def display_name(cls):
        return "Email"

    def default_config(self):
        return {"issue_address": "example" }

    def config_form(self):
        return render_template("email-issue-handler-config.html")

    def handle_new_submission(self, issue_subject, issue_body, issue_category=None):
        msg = EmailMessage(policy.SMTP)
        msg["From"] = current_app.config.get("STMP_USER")
        msg["To"] = self.issue_config["issue_address"]
        msg["Subject"] = issue_subject
        msg.set_content(issue_body)
        send_email(msg)


issue_bp = Blueprint("issue", __name__)


@issue_bp.route("/", methods=["GET", "POST"])
@login_required
def root():
    community_id = get_community_id()
    handler = current_app.Session.get(ReportingHandler, community_id)
    if request.method == "POST":
        issue_subject = request.form.get("issue_subject")
        issue_body = request.form.get("issue_body")
        handler.handle_new_submission(issue_subject, issue_body)
    custom_form = handler.custom_submit_form()
    if custom_form:
        return render_template("issue.html", custom_form=Markup(custom_form))

    issue_categories = handler.issue_categories()
    return render_template("issue.html", issue_categories=issue_categories)
