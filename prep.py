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
    except KeyError:
        return "Login failed!"

    return (pin, chk)


def apply_wa(pin, chk, headers):
    cookies = {
        "pin": pin,
    }

    data = {"action": "join_UN", "chk": chk, "submit": "1"}

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
