"""Step by Step to putting up tags
1. Login
2. Go to page=region_control (can combine this with above in the same request)
3. Change WFE
4. Change Flag
5. Close All Embassies (if desired)
6. Send Embassy to Holder Region
"""
import requests


def login(nation: str, password: str, headers: dict) -> dict:
    """Generates a CHK, Pin, and region name from a nation and password.

    Args:
        nation (str): Nation Name
        password (str): Password
        headers (dict): Headers, primarily for a user agent but you could shove other stuff there too ig

    Returns:
        dict: A dictionary containing the CHK, Pin, and region name.
    """
    url = "https://www.nationstates.net/template-overall=none/page=region_control/"

    data = {
        "logging_in": "1",
        "nation": nation,
        "password": password,
    }

    r = requests.post(url, data=data, headers=headers)

    # get all the information we need
    chk = r.text.split('<input type="hidden" name="chk" value="')[1].split('"')[0]
    pin = r.cookies["pin"]
    region_name = r.text.split('<span class="dull">')[1].split("</span>")[0].lower()
    return {"chk": chk, "pin": pin, "region_name": region_name}


def change_wfe(wfe: str, chk: str, pin: str, region_name, headers: dict) -> None:
    """Changes the WFE of a region.

    Args:
        wfe (str): The new WFE
        chk (str): The CHK
        pin (str): The Pin
        region_name (str): The Region Name
        headers (dict): Headers, primarily for a user agent but you could shove other stuff there too ig
    """
    url = "https://www.nationstates.net/template-overall=none/page=region_control/"

    data = {
        "chk": chk,
        "pin": pin,
        "region": region_name,
        "wfe": wfe,
    }

    requests.post(url, data=data, headers=headers)
