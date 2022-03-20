import json, traceback, base64
import PySimpleGUI as sg
import requests
import prep, polls

VERSION = "1.0.0" # VERY IMPORTANT TO CHANGE EVERY UPDATE!

def gui():
    sg.theme("Reddit")
    sg.set_options(
        suppress_raise_key_errors=False,
        suppress_error_popups=False,
        suppress_key_guessing=False,
    )
    # define icon
    try:
        with open("swarm.png", "rb") as f:
            swarm_image = base64.b64encode(f.read())
    except FileNotFoundError: # in binaries this will not work but if i just download the image it will
        swarm_image = requests.get("https://gist.githubusercontent.com/sw33ze/c0ec6fca37a69ff1a90f6847affd3c5f/raw/818c73cf742e1356018cf3a07806673472cba75b/swarm.png").content

    # define layouts
    prep_layout = [
        [sg.Text("Main Nation:"), sg.Input(key="-MAIN-")],
        [sg.Text("JP:"), sg.Input(key="-JP-", size=(38, 1))],
        [
            sg.Button("Login", key="-ACTION-", size=(12, 1)),
            sg.Text("Not logged into any nation!", key="-OUT-"),
        ],
    ]

    poll_layout = [
        [sg.Text("Main Nation:"), sg.Input(key="-POLLMAIN-")],
        [
            sg.Text("Poll ID:"),
            sg.Input(key="-POLL-", size=(7, 1)),
            sg.Text("Option:"),
            sg.Input(key="-POLLOPTION-", size=(2, 1)),
        ],
        [
            sg.Button("Login", key="-POLLACTION-", size=(12, 1)),
            sg.Text("Not logged into any nation!", key="-POLLOUT-"),
        ],
    ]

    layout = [
        [
            sg.TabGroup(
                [
                    [sg.Tab("Prep", prep_layout)],
                    [sg.Tab("Polls", poll_layout)],
                ],
                enable_events=True,
                key="-CURRENT TAB-",
            )
        ]
    ]

    return sg.Window("Puppet Manager", layout, icon=swarm_image, size=(325, 120))


def main():
    try:  # parse the nation config, try to account for as many fuckups as possible
        with open("config.json", "r", encoding="utf-8") as json_file:
            config = json.load(json_file)
    except FileNotFoundError:
        with open("config.json", "w", encoding="utf-8") as json_file:
            json_file.write(requests.get("https://gist.githubusercontent.com/sw33ze/568ad00257200f0649d9441a1ff032a0/raw/df3628dec0238bf10e6bd8419a47bd69079882e1/config.json").text)
        sg.popup_error(
            "No JSON File! Template created, fill it in with your nations!"
        )
        return
    except json.decoder.JSONDecodeError:
        sg.popup_error("JSON file is not valid!", traceback.format_exc())
        return  # end nation config parsing
    nation_dict = config["nations"]
    nations = list(nation_dict.keys())
    window = gui()
    nation_index = 0
    try:
        while True:
            event, values = window.read(timeout=100)
            if event == sg.WIN_CLOSED:  # da window is closed
                window.close()
                break
            match values["-CURRENT TAB-"]:
                case "Prep":
                    prep_thread(nation_dict, nations, window, nation_index)
                case "Polls":
                    polls_thread(nation_dict, nations, window, nation_index)
    except Exception as e:
        tb = traceback.format_exc()
        sg.Print(e, tb)
        sg.popup_error(
            "something went wrong copy the box behind this and send it to sweeze pls"
        )


def polls_thread(nation_dict, nations, window, nation_index):
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:  # da window is closed
            window.close()
            break

        if event == "-POLLACTION-":  # did u click the button to do the things
            main_nation = values["-POLLMAIN-"]
            poll_id = values["-POLL-"]
            choice = values["-POLLOPTION-"]
            current_action = window["-POLLACTION-"].get_text()
            current_nation = nations[nation_index]
            current_password = nation_dict[current_nation]
            if main_nation == "" or poll_id == "" or choice == "":
                sg.popup("Please enter a nation, poll ID, and poll choice.")
            else:
                window["-POLLACTION-"].update(disabled=True)
                headers = {
                    "User-Agent": f"Swarm (puppet manager) v{VERSION} devved by nation=sweeze in use by nation={main_nation}",
                }
                match current_action:  # lets go python 3.10 i love switch statements
                    case "Login":
                        window.perform_long_operation(
                            lambda: polls.login(
                                current_nation, current_password, headers, poll_id
                            ),
                            "-LOGIN DONE-",
                        )
                    case "Vote":
                        window.perform_long_operation(
                            lambda: polls.vote(pin, chk, poll_id, choice, headers),
                            "-VOTE-",
                        )
        # respond to threads!
        elif event is not None:
            match event:
                case "-LOGIN DONE-":
                    if values["-LOGIN DONE-"] == "Out of nations!":
                        window["-POLLOUT-"].update("No more nations!")
                    elif values["-LOGIN DONE-"] == "Login failed!":
                        window["-POLLOUT-"].update("Login failed!")
                        nation_index += 1
                    else:
                        prep_tab = window["-CURRENT TAB-"].find_key_from_tab_name(
                            "Prep"
                        )
                        window[prep_tab].update(disabled=True)
                        window["-POLLOUT-"].update(f"Logged in: {current_nation}")
                        nation_index += 1
                        pin = values["-LOGIN DONE-"][0]
                        chk = values["-LOGIN DONE-"][1]
                        window["-POLLACTION-"].update("Vote")
                case "-VOTE-":
                    window["-POLLOUT-"].update(f"Voted: {current_nation}")
                    prep_tab = window["-CURRENT TAB-"].find_key_from_tab_name("Prep")
                    window[prep_tab].update(disabled=False)
                    window["-POLLACTION-"].update("Login")

                case "-CURRENT TAB-":
                    if values["-CURRENT TAB-"] != "Polls":
                        window["-POLLACTION-"].update(disabled=False)
                        return
            window["-POLLACTION-"].update(disabled=False)


def prep_thread(nation_dict, nations, window, nation_index):
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:  # da window is closed
            window.close()
            break

        if event == "-ACTION-":  # did u click the button to do the things
            main_nation = values["-MAIN-"]
            jp = values["-JP-"]
            current_action = window["-ACTION-"].get_text()
            current_nation = nations[nation_index]
            current_password = nation_dict[current_nation]
            if main_nation == "" or jp == "":
                sg.popup("Please enter a nation and jump point.")
            else:
                window["-ACTION-"].update(disabled=True)
                headers = {
                    "User-Agent": f"Puppet Manager devved by nation=sweeze in use by nation={main_nation}",
                }
                match current_action:  # lets go python 3.10 i love switch statements
                    case "Login":
                        window.perform_long_operation(
                            lambda: prep.login(
                                current_nation, current_password, headers
                            ),
                            "-LOGIN DONE-",
                        )
                    case "Apply WA":
                        window.perform_long_operation(
                            lambda: prep.apply_wa(pin, chk, headers), "-WA DONE-"
                        )
                    case "Get Local ID":
                        window.perform_long_operation(
                            lambda: prep.get_local_id(pin, headers), "-LOCALID DONE-"
                        )
                    case "Move to JP":
                        window.perform_long_operation(
                            lambda: prep.move_to_jp(jp, pin, local_id, headers),
                            "-MOVED TO JP-",
                        )
        # respond to threads!
        elif event is not None:
            match event:
                case "-LOGIN DONE-":
                    if values["-LOGIN DONE-"] == "Out of nations!":
                        window["-OUT-"].update("No more nations!")
                    elif values["-LOGIN DONE-"] == "Login failed!":
                        window["-OUT-"].update("Login failed!")
                        nation_index += 1
                    else:
                        polls_tab = window["-CURRENT TAB-"].find_key_from_tab_name(
                            "Polls"
                        )
                        window[polls_tab].update(disabled=True)
                        window["-OUT-"].update(f"Logged in: {current_nation}")
                        pin = values["-LOGIN DONE-"][0]
                        chk = values["-LOGIN DONE-"][1]
                        window["-ACTION-"].update("Apply WA")

                case "-WA DONE-":
                    window["-OUT-"].update(f"Applied: {current_nation}")
                    window["-ACTION-"].update("Get Local ID")

                case "-LOCALID DONE-":
                    window["-OUT-"].update(f"Local ID: {current_nation}")
                    local_id = values["-LOCALID DONE-"]
                    window["-ACTION-"].update("Move to JP")

                case "-MOVED TO JP-":
                    window["-OUT-"].update(f"Moved: {current_nation}")
                    nation_index += 1
                    window[polls_tab].update(disabled=False)
                    window["-ACTION-"].update("Login")

                case "-CURRENT TAB-":
                    if values["-CURRENT TAB-"] != "Prep":
                        window["-ACTION-"].update(disabled=False)
                        return
            window["-ACTION-"].update(disabled=False)


if __name__ == "__main__":
    main()
