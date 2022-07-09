#  Nido email.py
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

import smtplib, ssl

from flask import current_app


def send_email(message):
    smtp_server = current_app.config.get("STMP_SERVER")
    sender_email = current_app.config.get("STMP_USER")
    password = current_app.config.get("STMP_PASSWORD")
    port = current_app.config.get("STMP_PORT", 465)

    # Create a secure SSL context
    context = ssl.create_default_context()

    # with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    with smtplib.SMTP(smtp_server, port) as server:
        #    server.login(sender_email, password)
        server.send_message(message)
