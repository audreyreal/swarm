# This file is part of Swarm.
#
# Swarm is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Swarm is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Swarm. If not, see <https://www.gnu.org/licenses/>.
import json  # for parsing legacy configs
import traceback  # for writing out the crash report
import os  # for converting legacy configs
import datetime  # for the user input timestamp i shove into the UA

import PySimpleGUI as sg  # library im using for gui stuff
import toml  # new config format, more readable than json
from tendo import (
    singleton,
)  # module i use to make sure only one instance can run at once
from components import (
    founding,
    misc,
    polls,
    prep,
    tagging,
    crash_reporter as cr,
)  # explicit is better than implicit, wildcard imports are apparantly "dangerous" or smth so no more of that ig, pyinstaller also doesn't work with them lmao
from components.swarm_icon import ICON

VERSION = "1.2.0"  # VERY IMPORTANT TO CHANGE EVERY UPDATE!


def init():
    me = singleton.SingleInstance()
    # will sys.exit(-1) if other instance is running, to avoid any possibility of breaking simultaneity

    sg.theme("Material1")
    sg.set_options(
        suppress_raise_key_errors=False,
        suppress_error_popups=False,
        suppress_key_guessing=False,
    )
    # the fact errors are suppressed by default is non pythonic and cringe as fuck

    sg.set_options(ttk_theme="clam")


def block_button_focuses(window):
    # this function exists so that the end user can't go break simultaneity
    # and one click per action by using tab to select a button and simulate mashing it with space
    buttons = [
        "-ACTION-",
        "-TAGGINGACTION-",
        "-POLLACTION-",
        "Login to Nations",
        "Find my WA",
    ]
    for button in buttons:
        window[button].block_focus(block=True)


def process_config(file_name):
    try:  # parse the nation config, try to account for as many fuckups as possible
        if os.path.exists(f"{file_name}.json"):
            json_file_to_toml_file(f"{file_name}.json")
        with open(f"{file_name}.toml", "r", encoding="utf-8") as toml_file:
            config = toml.load(toml_file)
        return config  # this is what we want ideally
    except FileNotFoundError:
        create_template_toml(f"{file_name}.toml")
        sg.popup_error(
            "No TOML file found! Template created, fill it in with your nations!"
        )
        exit()
    except toml.decoder.TomlDecodeError as exception:
        sg.popup_error("TOML file is not valid!", exception)
        exit()  # end nation config parsing


def get_configs(file_type=".toml"):
    all_files = os.listdir()
    toml_files = [file for file in all_files if file_type in file]
    try:
        configs = [file for file in toml_files if "nations" in toml.load(file)]
    except Exception:
        configs = [file for file in toml_files if "nations" in json.load(file)]
    return configs


def get_main_and_config():
    toml_configs = get_configs()
    json_configs = get_configs(file_type=".json")
    if toml_configs == []:
        if json_configs != []:
            # if there are no toml configs, but there are legacy json configs, convert them
            for file in json_configs:
                json_file_to_toml_file(file)
        else:
            # if there are no configs, create a template and exit after the fact
            create_template_toml("config.toml")
            sg.popup_error(
                "No TOML file found! Template created, fill it in with your nations!"
            )
            exit()

    LAYOUT = [
        [sg.Text("Main Nation:"), sg.Input(key="main", expand_x=True)],
        [
            sg.Text("Config:"),
            sg.Combo(
                get_configs(), key="config", expand_x=True, default_value="config.toml"
            ),
        ],
        [sg.Submit()],
    ]

    window = sg.Window(
        f"Swarm v{VERSION}",
        LAYOUT,
        icon=ICON,
        size=(400, 100),
        resizable=True,
        finalize=True,
    )
    window.set_min_size((400, 100))

    while True:
        event, values = window.read()
        match event:
            case sg.WIN_CLOSED:
                exit()
            case "Submit":
                if "" in (values["main"], values["config"]):
                    sg.popup("Please fill in your main nation and config file!")
                else:
                    headers = {
                        "User-Agent": f"Swarm (puppet manager, repo @ https://github.com/sw33ze/swarm) v{VERSION} developed by nation=sweeze (Discord: sweeze#3463) in use by nation={values['main'].strip()}, user input timestamp={datetime.datetime.now()}"
                    }
                    nation_exists = misc.check_if_nation_exists(
                        values["main"].strip(), headers=headers
                    )
                    if nation_exists:
                        window.close()
                        return values
                    else:
                        sg.popup(
                            "Nation does not exist!\nMake sure you spelled it correctly!"
                        )


def gui():
    INF = 10000  # tkinter doesn't support inf, so i decided to just do an absurdly large number
    # apparantly i actually could just use expand_x=True so past me is just a dumbass lmao

    # define layouts
    PREP_LAYOUT = [
        [sg.Text("JP:"), sg.Input(key="-JP-", size=(INF, 1))],
        [sg.Text("Not logged into any nation!", key="-OUT-")],
        [
            sg.Button("Login", key="-ACTION-", size=(INF, INF)),
        ],
    ]

    TAGGING_LAYOUT = [
        [sg.Button("Region Control Settings", size=(INF, 1))],
        [sg.Text("Not logged into any nation!", key="-TAGGINGOUT-")],
        [
            sg.Button("Login", key="-TAGGINGACTION-", size=(INF, INF)),
        ],
    ]

    POLL_LAYOUT = [
        [
            sg.Text("Poll ID:"),
            sg.Input(key="-POLL-", size=(30, 1), expand_x=True),
            sg.Text("Option:"),
            sg.Input(key="-POLLOPTION-", size=(3, 1)),
        ],
        [
            sg.Text("Not logged into any nation!", key="-POLLOUT-"),
        ],
        [
            sg.Button("Login", key="-POLLACTION-", size=(INF, INF)),
        ],
    ]

    MISC_LAYOUT = [
        [sg.Text("Not logged into any nation!", key="-MISCOUT-")],
        [
            sg.Button("Login to Nations", size=(INF, 6), expand_y=True),
        ],
        [sg.Button("Find my WA", size=(INF, 6), expand_y=True)],
    ]

    LAYOUT = [
        [
            sg.TabGroup(
                [
                    [sg.Tab("Prep", PREP_LAYOUT)],
                    [sg.Tab("Tagging", TAGGING_LAYOUT, disabled=True)],
                    [sg.Tab("Polls", POLL_LAYOUT)],
                    [sg.Tab("Misc", MISC_LAYOUT)],
                ],
                enable_events=True,
                key="-CURRENT TAB-",
            )
        ]
    ]

    return sg.Window(
        f"Swarm v{VERSION}",
        LAYOUT,
        icon=ICON,
        size=(400, 330),
        resizable=True,
        finalize=True,
    )


def json_file_to_toml_file(json_file):
    with open(json_file, "r") as f:
        data = json.load(f)
    with open(json_file.replace(".json", ".toml"), "w") as f:
        toml.dump(data, f)
    os.remove(json_file)


def disable_all_tabs(current_tab, window):
    TABS = ["Prep", "Tagging", "Polls", "Misc"]
    for tab in TABS:
        tab_key = window["-CURRENT TAB-"].find_key_from_tab_name(tab)
        if tab != current_tab:
            window[tab_key].update(disabled=True)


def enable_all_tabs(current_tab, window):
    TABS = ["Prep", "Tagging", "Polls", "Misc"]
    for tab in TABS:
        tab_key = window["-CURRENT TAB-"].find_key_from_tab_name(tab)
        if tab != current_tab:
            window[tab_key].update(disabled=False)


def main():
    if os.path.exists("config.json"):
        json_file_to_toml_file("config.json")
    # convert json config to toml config since it's more user friendly imo
    values = get_main_and_config()
    config = process_config(values["config"].replace(".toml", ""))
    main_nation = values["main"].strip()
    if config is None:
        return
    nation_dict = config["nations"]
    window = gui()
    block_button_focuses(window)
    window.set_min_size((400, 330))
    while True:
        event, values = window.read(timeout=1)
        if event == sg.WIN_CLOSED:  # da window is closed
            window.close()
            break
        match values["-CURRENT TAB-"]:
            case "Prep":
                prep_thread(nation_dict, window, main_nation)
            case "Tagging":
                tagging_thread(nation_dict, window, main_nation)
            case "Polls":
                polls_thread(nation_dict, window, main_nation)
            case "Misc":
                misc_thread(nation_dict, window, main_nation)


def create_template_toml(file_name):
    template = {"nations": {f"Puppet {i + 1}": "password" for i in range(5)}}
    with open(file_name, "w", encoding="utf-8") as toml_file:
        toml.dump(template, toml_file)


def tagging_popup():
    LAYOUT = [
        [sg.Text("WFE:")],
        [sg.Multiline(key="wfe", size=(40, 10))],
        [
            sg.Text("Flag Path:"),
            sg.FileBrowse(key="flag_path"),
            sg.Text("Banner Path:"),
            sg.FileBrowse(key="banner_path"),
        ],
        [
            sg.Text("Embassies:"),
            sg.Input(key="embassies", size=(12, 1)),
            sg.Text("Tags:"),
            sg.Input(key="tags", size=(8, 1)),
        ],
        [sg.Submit()],
    ]
    window = sg.Window("Tagging Settings", LAYOUT, icon=ICON, modal=True)
    while True:
        event, values = window.read()
        match event:
            case sg.WIN_CLOSED:
                return "Closed early!"
            case "Submit":
                values["embassies"] = values["embassies"].split(", ")
                values["tags"] = values["tags"].split(", ")
                window.close()
                return values


def tagging_thread(nation_dict, window, main_nation):
    nation_index = 0
    nations = tuple(nation_dict.keys())
    statuses = {
        "WFE Not Done": True,
        "Flag+Banner Not Done": True,
        "Embassies Not Done": True,
        "Tags Not Done": True,
    }
    while True:
        event, values = window.read()
        try:
            main_nation = values["-TAGGINGMAIN-"]
        except TypeError:
            break
        if event == "-CURRENT TAB-" and values["-CURRENT TAB-"] != "Tagging":
            return
        if main_nation == "":
            sg.popup("Please enter a main nation.")
            continue
        headers = {
            "User-Agent": f"Swarm (puppet manager, repo @ https://github.com/sw33ze/swarm) v{VERSION} developed by nation=sweeze (Discord: sweeze#3463) in use by nation={main_nation}, user input timestamp={datetime.datetime.now()}",
        }
        # there's a whole lot of stuff im shoving into that ua i know, but it's better to have too much info than not enough
        # the datetime.datetime.now() in particular is based on this post: https://forum.nationstates.net/viewtopic.php?p=30083979&sid=fbcf1d72aa0e04e249bd622221911f2c#p30083979
        # which recommends giving the timestamp of the user input so things are clear to admin if simultaneity is being followed properly or not
        match event:
            case sg.WIN_CLOSED:
                return
            case "Region Control Settings":
                tag_fields = tagging_popup()

            case "-TAGGINGACTION-":
                if "tag_fields" not in locals():
                    sg.popup("Please fill in the tagging settings first.")
                    continue
                window["-TAGGINGACTION-"].update(
                    disabled=True
                )  # disable the action button in accordance with the simultaneity rule
                match window["-TAGGINGACTION-"].get_text():
                    case "Login":
                        nation = nations[nation_index]
                        password = nation_dict[nation]
                        window["-TAGGINGOUT-"].update(f"Logging in to {nation}...")
                        window["-TAGGINGACTION-"].update(
                            disabled=True
                        )  # disable the button that makes requests in accordance with simultaneity
                        window.perform_long_operation(
                            lambda: tagging.login(nation, password, headers),
                            "-LOGGED IN-",
                        )
                    case "Change WFE":
                        window["-TAGGINGOUT-"].update(
                            f"Changing WFE in {storage['nation']}..."
                        )
                        window.perform_long_operation(
                            lambda: tagging.change_wfe(
                                tag_fields["wfe"],
                                tag_fields["chk"],
                                tag_fields["pin"],
                                headers,
                            ),
                            "-WFE CHANGED-",
                        )
                    case "Upload Flag":
                        window["-TAGGINGOUT-"].update(
                            f"Uploading flag in {storage['region']}..."
                        )
                        window.perform_long_operation(
                            lambda: tagging.upload_flag(
                                tag_fields["flag_path"],
                                storage["region"],
                                storage["chk"],
                                storage["pin"],
                                headers,
                            ),
                            "-FLAG UPLOADED-",
                        )
                    case "Upload Banner":
                        window["-TAGGINGOUT-"].update(
                            f"Changing banner in {storage['region']}..."
                        )
                        window.perform_long_operation(
                            lambda: tagging.upload_banner(
                                tag_fields["banner_path"],
                                storage["region"],
                                storage["chk"],
                                storage["pin"],
                                headers,
                            ),
                            "-BANNER UPLOADED-",
                        )
                    case "Change Flag/Banner":
                        window["-TAGGINGOUT-"].update(
                            f"Changing flag/banner in {storage['region']}..."
                        )
                        window.perform_long_operation(
                            lambda: tagging.change_flag_and_banner(
                                flag if "flag" in locals() else "none",
                                banner if "banner" in locals() else "0",
                            ),
                            "-FLAG/BANNER CHANGED-",
                        )

            # beyond here im just gonna be responding to threads and re-enabling the action button in accordance w/ following simultaneity
            case "-LOGGED IN-":
                storage = values["-LOGGED IN-"]
                window["-TAGGINGOUT-"].update(f"Logged in to {nation}!")
                match statuses:
                    case "WFE Not Done":
                        window["-TAGGINGACTION-"].update("Change WFE")
                    case "Flag+Banner Not Done":
                        window["-TAGGINGACTION-"].update("Upload Flag+Banner")
                    case "Embassies Not Done":
                        pass
                window["-TAGGINGACTION-"].update(disabled=False)


def misc_thread(nation_dict, window, main_nation):
    def disable_misc_buttons(window):
        disable_all_tabs("Misc", window)
        window["Login to Nations"].update(disabled=True)
        window["Find my WA"].update(disabled=True)

    def enable_misc_buttons(window):
        enable_all_tabs("Misc", window)
        window["Login to Nations"].update(disabled=False)
        window["Find my WA"].update(disabled=False)

    while True:
        event, values = window.read()
        if event == "-CURRENT TAB-":
            if values["-CURRENT TAB-"] != "Misc":
                return
        else:
            headers = {
                "User-Agent": f"Swarm (puppet manager, repo @ https://github.com/sw33ze/swarm) v{VERSION} developed by nation=sweeze (Discord: sweeze#3463) in use by nation={main_nation}, user input timestamp={datetime.datetime.now()}",
            }
            match event:
                case sg.WIN_CLOSED:
                    window.close()
                    return

                case "Login to Nations":
                    disable_misc_buttons(window)
                    window.perform_long_operation(
                        lambda: misc.login_loop(nation_dict, headers, window),
                        "-DONE LOGGING IN-",
                    )
                case "Find my WA":
                    disable_misc_buttons(window)
                    window.perform_long_operation(
                        lambda: misc.find_wa(nation_dict.keys(), headers),
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


def polls_thread(nation_dict, window, main_nation):
    nation_index = 0
    nations = tuple(nation_dict.keys())
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:  # da window is closed
            window.close()
            break

        if event == "-POLLACTION-":  # did u click the button to do the things
            poll_id = values["-POLL-"]
            choice = values["-POLLOPTION-"]
            current_action = window["-POLLACTION-"].get_text()
            try:
                current_nation = nations[nation_index]
            except IndexError:
                window["-POLLOUT-"].update("No more nations!")
                sg.popup("No more nations!")
                enable_all_tabs("Polls", window)
                break
            current_password = nation_dict[current_nation]
            if "" in (poll_id, choice):
                sg.popup("Please enter poll ID and poll choice.")
            else:
                window["-POLLACTION-"].update(disabled=True)
                headers = {
                    "User-Agent": f"Swarm (puppet manager, repo @ https://github.com/sw33ze/swarm) v{VERSION} developed by nation=sweeze (Discord: sweeze#3463) in use by nation={main_nation}, user input timestamp={datetime.datetime.now()}",
                }
                match current_action:  # lets go python 3.10 i love switch statements
                    case "Login":
                        disable_all_tabs("Polls", window)
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
                        sg.popup("No more nations!")
                        enable_all_tabs("Polls", window)
                    elif values["-LOGIN DONE-"] == "Login failed!":
                        window["-POLLOUT-"].update("Login failed!")
                        nation_index += 1
                    else:
                        window["-POLLOUT-"].update(f"Logged in: {current_nation}")
                        pin = values["-LOGIN DONE-"][0]
                        chk = values["-LOGIN DONE-"][1]
                        window["-POLLACTION-"].update("Vote")
                case "-VOTE-":
                    window["-POLLOUT-"].update(f"Voted: {current_nation}")
                    window["-POLLACTION-"].update("Login")
                    nation_index += 1

                case "-CURRENT TAB-":
                    if values["-CURRENT TAB-"] != "Polls":
                        window["-POLLACTION-"].update(disabled=False)
                        return
            window["-POLLACTION-"].update(disabled=False)


def prep_thread(nation_dict, window, main_nation):
    nation_index = 0
    nations = tuple(nation_dict.keys())
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:  # da window is closed
            window.close()
            break

        if event == "-ACTION-":  # did u click the button to do the things
            jp = values["-JP-"].strip()
            current_action = window["-ACTION-"].get_text()
            try:
                current_nation = nations[nation_index]
            except IndexError:
                window["-OUT-"].update("No more nations!")
                sg.popup("No more nations!")
                enable_all_tabs("Prep", window)
                return
            current_password = nation_dict[current_nation]
            if jp == "":
                sg.popup("Please enter a jump point.")
            else:
                window["-ACTION-"].update(disabled=True)
                headers = {
                    "User-Agent": f"Swarm (puppet manager, repo @ https://github.com/sw33ze/swarm) v{VERSION} developed by nation=sweeze (Discord: sweeze#3463) in use by nation={main_nation}, user input timestamp={datetime.datetime.now()}",
                }
                match current_action:  # lets go python 3.10 i love switch statements
                    case "Login":
                        disable_all_tabs("Prep", window)
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
                        enable_all_tabs("Prep", window)
                        window["-OUT-"].update("No more nations!")
                        sg.popup("No more nations!")
                    elif values["-LOGIN DONE-"] == "Login failed!":
                        window["-OUT-"].update("Login failed!")
                        nation_index += 1
                    else:
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
                    window["-ACTION-"].update("Login")

                case "-CURRENT TAB-":
                    if values["-CURRENT TAB-"] != "Prep":
                        window["-ACTION-"].update(disabled=False)
                        return
            window["-ACTION-"].update(disabled=False)


def report_crash(traceback):
    try:  # make sure a webhook to report the crash to is present otherwise dont bother
        with open("webhook.txt", "r") as f:
            webhook = f.read()
    except Exception:
        create_crash_report(anonymized_traceback)
    anonymized_traceback = cr.anonymize_traceback(traceback, "SwarmUser")
    LAYOUT = [
        [
            sg.Text(
                "Swarm has crashed! Do you want to automatically send the following crash report to the developer?"
            )
        ],
        [sg.Multiline(anonymized_traceback, size=(80, 10), disabled=True)],
        [sg.Button("Send"), sg.Button("Cancel")],
    ]

    window = sg.Window("Something went wrong!", layout=LAYOUT)
    event, values = window.read()
    match event:
        case "Send":
            cr.upload(webhook, f"Swarm v{VERSION}", anonymized_traceback)
            return
        case "Cancel":
            create_crash_report(anonymized_traceback)
            return


def create_crash_report(anonymized_traceback):
    with open(f"crash-report-{datetime.date.today()}.txt", "w") as f:
        f.write(f"v{VERSION}\n\n{anonymized_traceback}")


if __name__ == "__main__":
    try:
        init()
        main()
    except Exception:
        report_crash(traceback.format_exc())
