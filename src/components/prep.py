# This file is part of Swarm.
#
# Swarm is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Swarm is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Swarm. If not, see <https://www.gnu.org/licenses/>.

import requests
from bs4 import BeautifulSoup


def login(nation, password, headers):
    try:
        params = (
            ("nation", nation),
            ("password", password),
            ("logging_in", "1"),
        )
    except IndexError:
        return "Out of nations!"

    response = requests.get(
        "https://www.nationstates.net/template-overall=none/page=un/",
        headers=headers,
        params=params,
    )
    try:
        soup = BeautifulSoup(response.text, "html.parser")
        chk = soup.find("input", {"name": "chk"}).attrs["value"]
        pin = response.headers["Set-Cookie"].split("; ")[0].split("=")[1]
    except Exception:
        return "Login failed!"

    return (pin, chk)


def apply_wa(pin, chk, headers):
    cookies = {
        "pin": pin,
    }

    data = {"action": "join_UN", "chk": chk, "submit": "1", "resend": "1"}

    requests.post(
        "https://www.nationstates.net/template-overall=none/page=UN_status",
        headers=headers,
        cookies=cookies,
        data=data,
    )


def get_local_id(pin, headers):
    cookies = {
        "pin": pin,
    }

    response = requests.get(
        "https://www.nationstates.net/template-overall=none/page=settings",
        headers=headers,
        cookies=cookies,
    )

    soup = BeautifulSoup(response.text, "html.parser")
    return soup.find("input", {"name": "localid"}).attrs["value"]


def move_to_jp(jp, pin, local_id, headers):
    cookies = {
        "pin": pin,
    }

    data = {
        "localid": local_id,
        "region_name": jp,
        "move_region": "1",
    }

    requests.post(
        "https://www.nationstates.net/template-overall=none/page=change_region",
        headers=headers,
        cookies=cookies,
        data=data,
    )
