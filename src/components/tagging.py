# This file is part of Swarm.
#
# Swarm is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Swarm is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Swarm. If not, see <https://www.gnu.org/licenses/>.

# i really should have just used bs4 instead of .split() a bunch, oh well it works
import contextlib, json
import requests


def login(nation: str, password: str, headers: dict) -> dict:
    """Generates a CHK, Pin, and region name from a nation and password.

    Args:
        nation (str): Nation Name
        password (str): Password
        headers (dict): Headers, primarily for a user agent but you could shove other stuff there too ig

    Returns:
        dict: Dictionary containing a bunch of attributes of the region
    """
    url = "https://www.nationstates.net/template-overall=none/page=region_control/"

    data = {
        "logging_in": "1",
        "nation": nation,
        "password": password,
    }

    response = requests.post(url, data=data, headers=headers)
    # get all the information we need
    try:
        chk = response.text.split('<input type="hidden" name="chk" value="')[1].split(
            '"'
        )[0]
        pin = response.cookies["pin"]
    except Exception:
        return "Login failed."

    region_name = response.text.split('<a href="/region=')[1].split('"')[0]
    permissions = get_ro_perms(response.text)
    embassies = get_embassies(response.text)
    dispatches = get_dispatches(response.text)
    tags = get_tags(response.text)
    has_poll = "is currently running." in response.text
    return {
        "chk": chk,
        "pin": pin,
        "region_name": region_name,
        "has_poll": has_poll,
        "permissions": permissions,
        "dispatches": dispatches,
        "tags": tags,
        "embassies": embassies,
    }


def get_dispatches(region_control_page: str) -> list:
    """Takes the region_control_page and returns a list of the dispatches the region currently has.

    Args:
        region_control_page (str): HTML of template-overall=none/page=region_control, logged in or not

    Returns:
        list: List containing all current dispatches of the region. Empty if none
    """
    dispatches = []
    try:
        dispatch_block = region_control_page.split('<div class="dispatchlist">')[
            1
        ].split("</ol>")[0]
    except IndexError:
        return dispatches
    for dispatch in dispatch_block.split("<li>"):
        if '<a href="/page=dispatch/id=' in dispatch:
            dispatches.append(
                dispatch.split('<a href="/page=dispatch/id=')[1].split('">')[0]
            )
    return dispatches


def get_tags(region_control_page: str) -> list:
    """Takes the region_control_page and returns a list of the tags the region currently has.

    Args:
        region_control_page (str): HTML of template-overall=none/page=region_control, logged in or not

    Returns:
        list: List containing all current tags of the region.
    """
    try:
        tags_block = region_control_page.split(
            "<option value='_invalid'>------------------------</option>"
        )[2].split("</select>")[0]
    except Exception:
        return []
    tags = []
    for tag in tags_block.split("\n"):
        with contextlib.suppress(IndexError):
            tags.append(tag.split("<option value='")[1].split("'")[0])
    return tags


def get_embassies(region_control_page: str) -> list:
    """Takes the region_control_page and returns a list of the embassies the current region has.

    Args:
        region_control_page (str): HTML of template-overall=none/page=region_control, logged in or not.

    Returns:
        list: List containing all embassy regions
    """
    embassies = []
    try:
        embassy_block = region_control_page.split('shiny wide embassies mcollapse">')[
            1
        ].split("</tbody>")[0]
    except IndexError:
        return embassies
    embassy_rows = embassy_block.split("<tr>")[1:]
    for row in embassy_rows:
        with contextlib.suppress(
            IndexError
        ):  # suppress indexerrors because im too lazy to get rid of the header row
            embassies.append(
                row.split("Promote ")[1].split(" to the top of the embassy list")[0]
            )
    return embassies


def get_ro_perms(region_control_page: str) -> list:
    """Takes the region_control_page and returns a list of the RO Permissions your signed-in nation has.

    Args:
        region_control_page (str): HTML of the region_control_page, logged in.

    Returns:
        list: List containing all permissions of the nation
    """
    ro_block = region_control_page.split("<p>")[1].split("</p>")[0]
    return (
        [
            perm
            for perm in [
                "Executive",
                "Appearance",
                "Communications",
                "Border Control",
                "Embassies",
                "Communications",
                "Polls",
            ]
            if perm in ro_block
        ]
        if ('<span class="minorinfo">' in ro_block)
        else []
    )


# Done getting region information, now onto actually changing said information.


def change_wfe(wfe: str, chk: str, pin: str, headers: dict) -> str:
    """Changes the WFE of a region.

    Args:
        wfe (str): The new WFE
        chk (str): The CHK
        pin (str): The Pin
        headers (dict): Headers, primarily for a user agent but you could shove other stuff there too ig

    Returns:
        str: String saying whether the change was successful or not
    """
    url = "https://www.nationstates.net/template-overall=none/page=region_control/"
    cookies = {"pin": pin}

    data = {
        "chk": chk,
        "message": wfe,
        "setwfebutton": "1",
    }

    response = requests.post(url, data=data, headers=headers, cookies=cookies)

    if "updated!" in response.text:
        return "WFE changed."
    else:
        return "Failed to change WFE."


def upload_flag(
    flag_path: str, region_name: str, chk: str, pin: str, headers: dict
) -> str:
    url = "https://www.nationstates.net/cgi-bin/upload.cgi"
    cookies = {"pin": pin}
    data = {
        "chk": chk,
        "uploadtype": "rflag",
        "expect": "json",
        "page": "region_control",
        "region": region_name,
    }
    files = {"file_upload_rflag": open(flag_path, "rb")}
    response = requests.post(
        url, data=data, headers=headers, cookies=cookies, files=files
    )
    try:
        json_response = json.loads(response.text)
        if json_response["ok"] == 1:
            return json_response["id"]
        return "Failed to upload flag."
    except Exception:
        return "Failed to upload flag."


def upload_banner(
    banner_path: str, region_name: str, chk: str, pin: str, headers: dict
) -> str:
    """Uploads a banner to a region.

    Args:
        banner_path (str): Path to the banner file on the end user's computer
        region_name (str): Name of the region you're uploading the banner to
        chk (str): CHK Value of the nation you're uploading from
        pin (str): Pin of the nation you're uploading from
        headers (dict): Headers, primarily for user agent but could shove other stuff there too ig

    Returns:
        str: ID of the banner on the nationstates server. If it fails, it returns "Failed to upload banner."
    """
    url = "https://www.nationstates.net/cgi-bin/upload.cgi"
    cookies = {"pin": pin}
    data = {
        "chk": chk,
        "uploadtype": "rbanner",
        "expect": "json",
        "page": "region_control",
        "region": region_name,
    }
    files = {"file_upload_rbanner": open(banner_path, "rb")}
    response = requests.post(
        url, data=data, headers=headers, cookies=cookies, files=files
    )
    print(response.text)
    try:
        json_response = json.loads(response.text)
        if json_response["ok"] == 1:
            return {"path": json_response["path"], "id": json_response["id"]}
        else:
            return "Failed to upload banner."
    except Exception:
        return "Failed to upload banner."


def change_flag_and_banner(flag: str, banner: str, chk: str, pin: str, headers: dict) -> str:
    """Changes the Flag and Banner of a region.

    Args:
        flag (str): The filename of the flag on the nationstates server. e.g. "sweeze__336870.jpg"
        banner (str): The ID of the banner on the nationstates server. e.g. "843179"
        chk (str): The CHK
        pin (str): The Pin
        headers (dict): Headers, primarily for a user agent but you could shove other stuff there too ig

    Returns:
        str: "Flag/banner changed." if successful, "Failed to change flag/banner." if not.
    """
    url = "https://www.nationstates.net/template-overall=none/page=region_control/"
    cookies = {"pin": pin}

    data = {
        "chk": chk,
        "newflag": flag,
        "saveflagandbannerchanges": "1",
    }

    response = requests.post(url, data=data, headers=headers, cookies=cookies)

    if "updated!" in response.text:
        return "Flag/banner changed."
    else:
        return "Failed to change flag/banner."


def withdraw_embassy(region: str, chk: str, pin: str, headers: dict) -> str:
    """Closes a specified embassy from the region.

    Args:
        region (str): The name of the region whose embassy you're closing
        chk (str): CHK of the nation you're withdrawing from
        pin (str): PIN of the nation you're withdrawing from
        headers (dict): Headers, primarily for user-agent but could shove whatever your heart desired there

    Returns:
        str: "Embassy closed." if successful, "Failed to close embassy." if not.
    """
    url = "https://www.nationstates.net/template-overall=none/page=region_control/"
    cookies = {"pin": pin}

    data = {
        "chk": chk,
        "embassyregion": region,
        "cancelembassy": " Withdraw Embassy ",
    }

    response = requests.post(url, data=data, headers=headers, cookies=cookies)

    if "has been scheduled for demolition." in response.text:
        return "Embassy closed."
    else:
        return "Failed to close embassy."


def request_embassy(region: str, chk: str, pin: str, headers: dict) -> str:
    """Changes the Flag of a region.

    Args:
        flag (str): The filename of the flag on the nationstates server.
        banner (str): The ID of the banner on the nationstates server.
        chk (str): The CHK
        pin (str): The Pin
        headers (dict): Headers, primarily for a user agent but you could shove other stuff there too ig

    Returns:
        str: "Embassy closed." if successful, "Failed to close embassy." if not.
    """
    url = "https://www.nationstates.net/template-overall=none/page=region_control/"
    cookies = {"pin": pin}

    data = {
        "chk": chk,
        "embassyregion": region,
        "embassyrequest": "1",
    }

    response = requests.post(url, data=data, headers=headers, cookies=cookies)

    if "has been scheduled for demolition." in response.text:
        return "Embassy closed."
    else:
        return "Failed to close embassy."
