# This file is part of Swarm.
#
# Swarm is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Swarm is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Swarm. If not, see <https://www.gnu.org/licenses/>.

import json, traceback, base64
import PySimpleGUI as sg
import requests
from components import (
    misc,
    polls,
    prep,
)
from time import time

#Calculated every time we click the Big Red Button, passed to functions to include with requests in compliance with 1 Mar 2023 rules change
def userclick():
    timestamp = int(time() * 1000) #Unix time in millis
#    print(f"DEBUG: {timestamp}")
    return timestamp

VERSION = "1.1.2a"  # VERY IMPORTANT TO CHANGE EVERY UPDATE!

def gui():
    sg.theme("Reddit")
    sg.set_options(
        suppress_raise_key_errors=False,
        suppress_error_popups=False,
        suppress_key_guessing=False,
    )
    # define icon
    try:
        with open("components/swarm.png", "rb") as f:
            swarm_image = base64.b64encode(f.read())
    except FileNotFoundError:  # in binaries this will not work but if i just download the image datauri it will
        swarm_image = requests.get(
            "https://gist.githubusercontent.com/sw33ze/c0ec6fca37a69ff1a90f6847affd3c5f/raw/818c73cf742e1356018cf3a07806673472cba75b/swarm.png"
        ).content

    # define layouts
    prep_layout = [
        [sg.Text("Main Nation:"), sg.Input(key="-MAIN-")],
        [sg.Text("JP:"), sg.Input(key="-JP-", size=(38, 1))],
        [sg.Text("Not logged into any nation!", key="-OUT-")],
        [
            sg.Button("Login", key="-ACTION-", size=(36, 12)),
        ],
        [
            sg.Button("Skip", key="-SKIP-", size=(36,12)),
        ],
    ]

    tagging_layout = [
        [sg.Text("Main Nation:"), sg.Input(key="-TAGGINGMAIN-")],
    ]

    poll_layout = [
        [sg.Text("Main Nation:"), sg.Input(key="-POLLMAIN-")],
        [
            sg.Text("Poll ID:"),
            sg.Input(key="-POLL-", size=(14, 1)),
            sg.Text("Option:"),
            sg.Input(key="-POLLOPTION-", size=(2, 1)),
        ],
        [
            sg.Text("Not logged into any nation!", key="-POLLOUT-"),
        ],
        [
            sg.Button("Login", key="-POLLACTION-", size=(36, 12)),
        ],
    ]

    misc_layout = [
        [sg.Text("Main Nation:"), sg.Input(key="-MISCMAIN-")],
        [sg.Text("Not logged into any nation!", key="-MISCOUT-")],
        [
            sg.Button("Login to Nations", size=(35, 6)),
        ],
        [sg.Button("Find my WA", size=(35, 6))],
    ]

    move_layout = [
        [sg.Text("Main Nation:"), sg.Input(key="-MOVEMAIN-")],
        [sg.Text("JP:"), sg.Input(key="-MOVEJP-",size=(38,1))],
        [sg.Text("Not logged into any nation!", key="-MOVEOUT-")],
        [
            sg.Button("Login",key="-MOVEACTION-", size=(36,12)),
        ],
        [
            sg.Button("Skip", key="-MOVESKIP-")
        ],
    ]

    layout = [
        [
            sg.TabGroup(
                [
                    [sg.Tab("Prep", prep_layout)],
                    [sg.Tab("Tagging", tagging_layout, disabled=True)],
                    [sg.Tab("Polls", poll_layout)],
                    [sg.Tab("Misc", misc_layout)],
                    [sg.Tab("Mover",move_layout)],
                ],
                enable_events=True,
                key="-CURRENT TAB-",
            )
        ]
    ]

    return sg.Window("Swarm", layout, icon=swarm_image, size=(355, 330))


def main():
    try:  # parse the nation config, try to account for as many fuckups as possible
        with open("config.json", "r", encoding="utf-8") as json_file:
            config = json.load(json_file)
    except FileNotFoundError:
        with open("config.json", "w", encoding="utf-8") as json_file:
            json_file.write(
                requests.get(
                    "https://gist.githubusercontent.com/sw33ze/568ad00257200f0649d9441a1ff032a0/raw/df3628dec0238bf10e6bd8419a47bd69079882e1/config.json"
                ).text
            )
        sg.popup_error("No JSON File! Template created, fill it in with your nations!")
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
            event, values = window.read(timeout=1)
            if event == sg.WIN_CLOSED:  # da window is closed
                window.close()
                break
            match values["-CURRENT TAB-"]:
                case "Prep":
                    prep_thread(nation_dict, nations, window, nation_index)
                case "Tagging":
                    tagging_thread(nation_dict, window)
                case "Polls":
                    polls_thread(nation_dict, nations, window, nation_index)
                case "Misc":
                    misc_thread(nation_dict, window)
                case "Mover":
                    move_thread(nation_dict, nations, window, nation_index)

    except Exception as e:
        tb = traceback.format_exc()
        sg.Print(e, tb)
        sg.popup_error(
            "something went wrong copy the box behind this and send it to sweeze pls"
        )


def misc_thread(nation_dict, window):
    def disable_misc_buttons(window):
        window["Login to Nations"].update(disabled=True)
        window["Find my WA"].update(disabled=True)

    def enable_misc_buttons(window):
        window["Login to Nations"].update(disabled=False)
        window["Find my WA"].update(disabled=False)

    while True:
        event, values = window.read()
        try:
            main_nation = values["-MISCMAIN-"]
        except TypeError:
            break
        if event == "-CURRENT TAB-":
            if values["-CURRENT TAB-"] != "Misc":
                return
        if main_nation == "":
            sg.popup("Please enter a main nation.")
        else:
            headers = {
                "User-Agent": f"Swarm (puppet manager) v{VERSION} devved by nation=sweeze in use by nation={main_nation}",
            }
            match event:
                case sg.WIN_CLOSED:
                    window.close()
                    return

                case "Login to Nations":
                    timestamp = userclick()
                    disable_misc_buttons(window)
                    window.perform_long_operation(
                        lambda: misc.login_loop(nation_dict, headers, window, timestamp),
                        "-DONE LOGGING IN-",
                    )
                case "Find my WA":
                    timestamp = userclick()
                    disable_misc_buttons(window)
                    window.perform_long_operation(
                        lambda: misc.find_wa(nation_dict.keys(), headers, timestamp),
                        "-DONE FINDING WA-",
                    )
                # respond to threads
                case "-DONE LOGGING IN-":
                    enable_misc_buttons(window)
                    window["-MISCOUT-"].update("All nations logged in!")
                case "-DONE FINDING WA-":
                    enable_misc_buttons(window)
                    if values["-DONE FINDING WA-"] is None:
                        window["-MISCOUT-"].update("No WA found!")
                    else:
                        window["-MISCOUT-"].update(
                            f"Found WA! {values['-DONE FINDING WA-']}"
                        )


def tagging_thread(nation_dict, window):
    sg.Print("Not devved yet!")
    while True:
        event, values = window.read()

def polls_thread(nation_dict, nations, window, nation_index):
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:  # da window is closed
            window.close()
            break

        if event == "-POLLACTION-":  # did u click the button to do the things
            timestamp = userclick() #Get current unix timestamp for the current click
            main_nation = values["-POLLMAIN-"]
            poll_id = values["-POLL-"]
            choice = values["-POLLOPTION-"]
            current_action = window["-POLLACTION-"].get_text()
            try:
                current_nation = nations[nation_index]
            except IndexError:
                window["-POLLOUT-"].update("No more nations!")
                break
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
                                current_nation, current_password, headers, poll_id, timestamp
                            ),
                            "-LOGIN DONE-",
                        )
                    case "Vote":
                        window.perform_long_operation(
                            lambda: polls.vote(pin, chk, poll_id, choice, headers, timestamp),
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

def move_thread(nation_dict, nations, window, nation_index):
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:  # da window is closed
            window.close()
            break

        if event == "-MOVEACTION-":  # did u click the button to do the things
            timestamp = userclick()
            main_nation = values["-MOVEMAIN-"]
            jp = values["-MOVEJP-"]
            current_action = window["-MOVEACTION-"].get_text()
            try:
                current_nation = nations[nation_index]
            except IndexError:
                window["-MOVEOUT-"].update("No more nations!")
                return
            current_password = nation_dict[current_nation]
            if main_nation == "" or jp == "":
                sg.popup("Please enter a nation and jump point.")
            else:
                window["-MOVEACTION-"].update(disabled=True)
                headers = {
                    "User-Agent": f"Swarm (puppet manager) v{VERSION} devved by nation=sweeze in use by nation={main_nation}",
                }
                match current_action:  # lets go python 3.10 i love switch statements
                    case "Login":
                        window.perform_long_operation(
                            lambda: prep.login(
                                current_nation, current_password, headers, timestamp
                            ),
                            "-LOGIN DONE-",
                        )
                    #case "Apply WA":
                    #    window.perform_long_operation(
                    #        lambda: prep.apply_wa(pin, chk, headers), "-WA DONE-"
                    #    )
                    case "Get Local ID":
                       # print("FETCH LOCAL ID")
                        window.perform_long_operation(
                            lambda: prep.get_local_id(pin, headers, timestamp), "-LOCALID DONE-"
                        )
                    case "Move to JP":
                        #print("MOVE TO JP")
                        window.perform_long_operation(
                            lambda: prep.move_to_jp(jp, pin, local_id, headers, timestamp),
                            "-MOVED TO JP-",
                        )
        # respond to threads!
        elif event is not None:
            match event:
                case "-LOGIN DONE-":
                    if values["-LOGIN DONE-"] == "Out of nations!":
                        window["-MOVEOUT-"].update("No more nations!")
                    elif values["-LOGIN DONE-"] == "Login failed!":
                        window["-MOVEOUT-"].update("Login failed!")
                        nation_index += 1
                    else:
                        polls_tab = window["-CURRENT TAB-"].find_key_from_tab_name(
                            "Polls"
                        )
                        window[polls_tab].update(disabled=True)
                        window["-MOVEOUT-"].update(f"Logged in: {current_nation}")
                        pin = values["-LOGIN DONE-"][0]
                        chk = values["-LOGIN DONE-"][1]
#                        window["-MOVEACTION-"].update("Apply WA")
                        
                        window["-MOVEACTION-"].update("Get Local ID")
                        #print("MOVED")

                #case "-WA DONE-":
                #    window["-OUT-"].update(f"Applied: {current_nation}")
                #    window["-ACTION-"].update("Get Local ID")

                case "-LOCALID DONE-":
                    window["-MOVEOUT-"].update(f"Local ID: {current_nation}")
                    local_id = values["-LOCALID DONE-"]
                    window["-MOVEACTION-"].update("Move to JP")
                    #print("LOCAL DONE")

                case "-MOVED TO JP-":
                    window["-MOVEOUT-"].update(f"Moved: {current_nation}")
                    nation_index += 1
                    window[polls_tab].update(disabled=False)
                    window["-MOVEACTION-"].update("Login")
                    #print("MOVED")

                case "-CURRENT TAB-":
                    if values["-CURRENT TAB-"] != "Prep":
                        window["-MOVEACTION-"].update(disabled=False)
                        return

            window["-MOVEACTION-"].update(disabled=False)


def prep_thread(nation_dict, nations, window, nation_index):
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:  # da window is closed
            window.close()
            break

        if event == "-ACTION-":  # did u click the button to do the things
            timestamp = userclick()
            main_nation = values["-MAIN-"]
            jp = values["-JP-"]
            current_action = window["-ACTION-"].get_text()
            try:
                current_nation = nations[nation_index]
            except IndexError:
                window["-OUT-"].update("No more nations!")
                return
            current_password = nation_dict[current_nation]
            if main_nation == "" or jp == "":
                sg.popup("Please enter a nation and jump point.")
            else:
                window["-ACTION-"].update(disabled=True)
                headers = {
                    "User-Agent": f"Swarm (puppet manager) v{VERSION} devved by nation=sweeze in use by nation={main_nation}",
                }
                match current_action:  # lets go python 3.10 i love switch statements
                    case "Login":
                        window.perform_long_operation(
                            lambda: prep.login(
                                current_nation, current_password, headers, timestamp
                            ),
                            "-LOGIN DONE-",
                        )
                    case "Apply WA":
                        window.perform_long_operation(
                            lambda: prep.apply_wa(pin, chk, headers, timestamp), "-WA DONE-"
                        )
                    case "Get Local ID":
                        window.perform_long_operation(
                            lambda: prep.get_local_id(pin, headers, timestamp), "-LOCALID DONE-"
                        )
                    case "Move to JP":
                        window.perform_long_operation(
                            lambda: prep.move_to_jp(jp, pin, local_id, headers, timestamp),
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
