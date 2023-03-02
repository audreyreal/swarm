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


def login(nation, password, headers, poll_id, userclick):
    params = (
        ("nation", nation),
        ("password", password),
        ("logging_in", "1"),
    )

    response = requests.get(
        f"https://www.nationstates.net/template-overall=none/page=poll/p={poll_id}&userclick={userclick}",
        headers=headers,
        params=params,
    )
    try:
        soup = BeautifulSoup(response.text, "html.parser")
        chk = soup.find("input", {"name": "chk"}).attrs["value"]
        pin = response.headers["Set-Cookie"].split("; ")[0].split("=")[1]
    except:
        return "Login failed!"

    return (pin, chk)


def vote(pin, chk, poll_id, choice, headers, userclick):
    cookies = {
        "pin": pin,
    }

    data = {"pollid": poll_id, "chk": chk, "q1": choice, "poll_submit": "1"}

    requests.post(
        f"https://www.nationstates.net/template-overall=none/page=poll/p=181445&userclick={userclick}",
        headers=headers,
        cookies=cookies,
        data=data,
    )
