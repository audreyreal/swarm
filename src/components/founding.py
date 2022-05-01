# This file is part of Swarm.
#
# Swarm is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Swarm is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Swarm. If not, see <https://www.gnu.org/licenses/>.
#
# this module is written by 9003, polished by sweeze
import requests


def make_puppet(nation: str, password: str, email, headers: dict) -> str:
    """Generates a puppet from a nation, password, and custom fields.

    Args:
        nation (str): Puppet name
        password (str): Password
        email (str): Email (for WA purposes, optional)
        headers (dict): Headers, primarily for a user agent but you could shove other stuff there too ig

    Returns:
        str: CHK of the puppet
    """
    data = {
        "name": nation,
        "currency": "Coin",
        "slogan": "I love 9003",
        "animal": "Sweezelicous",
        "email": email,
        "password": password,
        "type": "101",
        "flag": "Default.svg",
        "confirm_password": password,
        "legal": "1",
        "style,": "100.100.100",
        "create_nation": "1",
    }
    response = requests.post(
        "https://www.nationstates.net/cgi-bin/build_nation.cgi",
        headers=headers,
        data=data,
    )
    if "was founded in" in response.text:
        return f"Created {nation}."
    else:
        return "Failed to create nation. Is the name already in use?"
