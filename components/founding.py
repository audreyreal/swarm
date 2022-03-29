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


def make_puppet(nation: str, password: str, email: str, headers: dict) -> str:
    params = (
        ("name", nation),
        ("currency", "Swarma"),
        ("slogan", "I love 9003"),
        ("animal", "Sweezelicous"),
        ("email", email),
        ("password", password),
        ("type", "101"),
        ("flag", "Default.svg"),
        ("confirm_password", password),
        ("legal", "1"),
        ("style,", "100.100.100"),
        ("history", ""),
        ("q0", ""),
        ("q1", ""),
        ("q2", ""),
        ("q3", ""),
        ("q4", ""),
        ("q5", ""),
        ("q6", ""),
        ("q7", ""),
        ("create_nation", "1"),
    )
    r = requests.post(
        "https://www.nationstates.net/cgi-bin/build_nation.cgi",
        headers=headers,
        data=params,
    )
    if "was founded in" in r.text:
        return f"Created {nation}"
    else:
        return "Failed to create nation"
