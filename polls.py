import requests
from bs4 import BeautifulSoup


def login(nation, password, headers, poll_id):
    params = (
        ("nation", nation),
        ("password", password),
        ("logging_in", "1"),
    )

    response = requests.get(
        f"https://www.nationstates.net/template-overall=none/page=poll/p={poll_id}",
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


def vote(pin, chk, poll_id, choice, headers):
    cookies = {
        "pin": pin,
    }

    data = {"pollid": poll_id, "chk": chk, "q1": choice, "poll_submit": "1"}

    requests.post(
        "https://www.nationstates.net/template-overall=none/page=poll/p=181445",
        headers=headers,
        cookies=cookies,
        data=data,
    )
