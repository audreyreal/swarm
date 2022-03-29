# This file is part of Swarm.
#
# Swarm is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Swarm is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Swarm. If not, see <https://www.gnu.org/licenses/>.

import time
import requests


def login(nation: str, password: str, headers: dict) -> str:
    """Logs into a nation via the API

    Args:
        nation (str): The nation you want to log into.
        password (str): The password to said nation you want to log into.
        headers (dict): Headers, mostly for a user agent but you could shove other stuff there too ig

    Returns:
        str: Whether the login was successful or not.
    """
    headers["X-Password"] = password

    url = f"https://www.nationstates.net/cgi-bin/api.cgi?nation={nation}&q=ping"
    try:
        requests.get(url, headers=headers).raise_for_status()
    except:
        return f"Failed to login to {nation}."
    return f"Successfully logged in to {nation}."


def login_loop(nation_dictionary: dict, headers: dict, window) -> str:
    """Logs into all of your nations via the API

    Args:
        nation_dictionary (dict): Dictionary of all of your nations and their passwords.
        headers (dict): Headers, mostly for a user agent but you could shove other stuff there too ig
        window (_type_): PySimpleGUI window to write the output to.

    Returns:
        str: When you're done logging into all the nations.
    """
    for nation, password in nation_dictionary.items():
        status = login(nation, password, headers)
        window["-MISCOUT-"].update(status)
        time.sleep(0.6)
    return "Done logging into nations"  # End of login section


def find_wa(nations: list, headers: dict) -> str or None:
    """Finds the WA nation in a list of nations.

    Args:
        nations (list): List of all of your nations.
        headers (dict): Headers, mostly for a user agent but you could shove other stuff there too ig

    Returns:
        str or None: str is the WA nation if it's found, None if it isn't.
    """
    url = "https://www.nationstates.net/cgi-bin/api.cgi?wa=1&q=members"
    wa_list = requests.get(url, headers=headers).text
    for nation in nations:
        nation = nation.replace(" ", "_").lower()
        if f",{nation}," in wa_list:
            # reason i have to do trailing commas is because im not properly parsing the xml out of laziness, and i dont want accidental false positives
            return nation
