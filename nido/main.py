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
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from .main_menu import get_main_menu
from .auth import auth_bp
from .admin import admin_bp
from .billing import bill_bp
from .directory import directory_bp
from .er_contacts import er_bp
from .household import bp as house_bp, root as house_root
from .issue import issue_bp


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

    db_engine = create_engine(
        app.config["DATABASE_URL"],
        echo=app.config.get("LOG_SQL", app.env == "development"),
    )
    app.Session = scoped_session(sessionmaker(bind=db_engine))

    @app.teardown_appcontext
    def end_db_session(response):
        app.Session.remove()

    try:
        import redis

        app.redis = redis.from_url(app.config["REDIS_URL"])
    except:
        app.redis = None

    app.jinja_env.globals.update(get_main_menu=get_main_menu)

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(bill_bp, url_prefix="/billing")
    app.register_blueprint(directory_bp, url_prefix="/directory")
    app.register_blueprint(er_bp, url_prefix="/emergency-contacts")
    app.register_blueprint(house_bp, url_prefix="/my-household")
    app.register_blueprint(issue_bp, url_prefix="/report-issue")
    app.add_url_rule("/login", endpoint="login")
    app.add_url_rule("/logout", endpoint="logout")
    app.add_url_rule("/", view_func=house_root)

    return app
