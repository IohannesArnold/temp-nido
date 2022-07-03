#  Nido main_menu.py
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

from flask import url_for
from .auth import current_user


class MenuLink:
    def __init__(self, name, href, submenu=None):
        self.name = name
        self.href = href
        self.submenu = submenu


def get_main_menu():
    menu_list = []
    menu_list.append(MenuLink("Dashboard", url_for("dash.dashboard")))
    menu_list.append(MenuLink("My Household", url_for("household.root")))
    menu_list.append(MenuLink("Billing", "/billing/"))
    menu_list.append(MenuLink("Resident Directory", url_for("directory.root")))
    menu_list.append(MenuLink("Emergency Contacts", url_for("er_contacts.root")))
    if current_user.is_admin():
        menu_list.append(MenuLink("Admin Center", url_for("admin.root")))
    menu_list.append(MenuLink("Logout", url_for("logout")))
    return menu_list
