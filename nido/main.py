#  Nido main.py
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

import os

from flask import Flask


def create_app(testing_config=None):
    app = Flask(
        __name__,
        instance_path=os.environ.get("NIDO_VARDIR"),
        instance_relative_config=True,
    )

    # Only used for pytest
    if testing_config:
        app.config.from_mapping(testing_config)

    # a simple page that says hello
    @app.route("/")
    def hello():
        return "Hello, World!"

    return app
