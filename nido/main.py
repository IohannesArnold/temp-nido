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

from .models import db, User
from .main_menu import get_main_menu
from .auth import auth_bp, current_user
from .admin import admin_bp
from .dashboard import dash_bp
from .directory import directory_bp
from .er_contacts import er_bp
from .household import bp as house_bp


def create_app(testing_config=None):
    app = Flask(
        __name__,
        instance_path=os.environ.get("NIDO_VARDIR"),
        instance_relative_config=True,
    )

    # Only used for pytest
    if testing_config:
        app.config.from_mapping(testing_config)
    else:
        conf_file = os.environ.get("NIDO_CONFIG_FILE") or "nido.cfg"
        app.config.from_pyfile(conf_file)

    if app.env == "development":
        # Don't import sassuntils until now since it's not installed for prod
        from sassutils.wsgi import SassMiddleware

        app.wsgi_app = SassMiddleware(
            app.wsgi_app,
            {
                "nido": {
                    "sass_path": "static/sass",
                    "css_path": "static/css",
                    "wsgi_path": "/static/css",
                    "strip_extension": True,
                }
            },
        )

    db.init_app(app)

    app.jinja_env.globals.update(get_main_menu=get_main_menu)
    app.jinja_env.globals.update(current_user=current_user)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dash_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(directory_bp, url_prefix="/directory")
    app.register_blueprint(er_bp, url_prefix="/emergency-contacts")
    app.register_blueprint(house_bp, url_prefix="/my-household")
    app.add_url_rule("/login", endpoint="login")
    app.add_url_rule("/logout", endpoint="logout")
    app.add_url_rule("/", endpoint="index")

    return app
