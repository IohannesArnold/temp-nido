#  Nido admin_view __init__.py
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

from flask import Blueprint
from .dashboard import dash_bp, dashboard
from .groups import posit_bp
from .permissions import bp as perm_bp


admin_bp = Blueprint("admin", __name__)

admin_bp.add_url_rule("/", endpoint="root", view_func=dashboard)
admin_bp.register_blueprint(perm_bp)
admin_bp.register_blueprint(dash_bp)
admin_bp.register_blueprint(posit_bp)
