from bs4 import BeautifulSoup
import requests
import PySimpleGUI as sg
import config


def gui():
    sg.theme("SystemDefaultForReal")

    layout = [
        [sg.Text("Main Nation:"), sg.Input(key="-MAIN-")],
        [sg.Text("JP:"), sg.Input(key="-JP-", size=(38, 1))],
        [
            sg.Button("Login", key="-ACTION-", size=(12, 1)),
            sg.Text("Not logged into any nation!", key="-OUT-"),
        ],
    ]

    return sg.Window("NS Prepping Helper", layout, size=(325, 90))


def login():
    try:
        params = (
            ("nation", config.NATIONS[current_nation]),
            ("password", config.PASSWORD),
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


def apply_wa():
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


def get_local_id():
    cookies = {
        "pin": pin,
    }

    response = requests.get(
        "https://www.nationstates.net/template-overall=none/page=settings",
        headers=headers,
        cookies=cookies,
    )

    soup = BeautifulSoup(response.text, "html.parser")
    local_id = soup.find("input", {"name": "localid"}).attrs["value"]
    return local_id


def move_to_jp():
    cookies = {
        "pin": pin,
    }

    data = {
        "localid": local_id,
        "region_name": jp,
        "move_region": "1",
    }

    response = requests.post(
        "https://www.nationstates.net/template-overall=none/page=change_region",
        headers=headers,
        cookies=cookies,
        data=data,
    )
    print(response.text)


if __name__ == "__main__":
    window = gui()
    input_allowed = True
    current_nation = 1

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:  # da window is closed
            break

        elif event == "-ACTION-":  # did u click the button to do the things
            main_nation = values["-MAIN-"]
            jp = values["-JP-"]
            current_action = window["-ACTION-"].get_text()
            if main_nation == "" or jp == "":
                sg.popup("Please enter a nation and jump point.")
            else:
                headers = {
                    "User-Agent": f"Puppet Prep Helper devved by nation=sweeze in use by nation={main_nation}",
                }

                if input_allowed:
                    if current_action == "Login":  # i miss switch statements D:
                        window.perform_long_operation(login, "-LOGIN DONE-")
                    elif current_action == "Apply WA":
                        window.perform_long_operation(apply_wa, "-WA DONE-")
                    elif current_action == "Get Local ID":
                        window.perform_long_operation(get_local_id, "-LOCALID DONE-")
                    elif current_action == "Move to JP":
                        window.perform_long_operation(
                            move_to_jp,
                            "-MOVED TO JP-",
                        )
                    input_allowed = False  # follow simultaneity, lock you out of input
        # respond to the threads!
        elif event is not None:

            if event == "-LOGIN DONE-":

                if values["-LOGIN DONE-"] == "Out of nations!":
                    window["-OUT-"].update("No more nations!")
                elif values["-LOGIN DONE-"] == "Login failed!":
                    window["-OUT-"].update("Login failed!")
                    current_nation += 1
                else:
                    window["-OUT-"].update(
                        f"Logged in: {config.NATIONS[current_nation]}"
                    )
                    pin = values["-LOGIN DONE-"][0]
                    chk = values["-LOGIN DONE-"][1]
                    window["-ACTION-"].update("Apply WA")

            elif event == "-WA DONE-":
                window["-OUT-"].update(f"Applied: {config.NATIONS[current_nation]}")
                window["-ACTION-"].update("Get Local ID")

            elif event == "-LOCALID DONE-":
                window["-OUT-"].update(f"Local ID: {config.NATIONS[current_nation]}")
                local_id = values["-LOCALID DONE-"]
                window["-ACTION-"].update("Move to JP")

            elif event == "-MOVED TO JP-":
                window["-OUT-"].update(f"Moved: {config.NATIONS[current_nation]}")
                current_nation += 1
                window["-ACTION-"].update("Login")

            input_allowed = True  # follow simultaneity, give you back input

    window.close()  # kill da process
