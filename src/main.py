# This file is part of Swarm.
#
# Swarm is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Swarm is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Swarm. If not, see <https://www.gnu.org/licenses/>.
import json, traceback, os  # json for legacy configs, traceback for printing errors to the gui instead of to the console that doesn't exist, os for removing the json config to replace with toml
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
)  # explicit is better than implicit, wildcard imports are apparantly "dangerous" or smth so no more of that ig, pyinstaller also doesn't work with them lmao
from components.swarm_icon import ICON


VERSION = "1.2.0"  # VERY IMPORTANT TO CHANGE EVERY UPDATE!


def gui():
    sg.theme("Material1")
    sg.set_options(
        suppress_raise_key_errors=False,
        suppress_error_popups=False,
        suppress_key_guessing=False,
    )

    if "clam" in sg.TTK_THEME_LIST:
        sg.set_options(ttk_theme="clam")

    # define layouts
    PREP_LAYOUT = [
        [sg.Text("Main Nation:"), sg.Input(key="-MAIN-")],
        [sg.Text("JP:"), sg.Input(key="-JP-", size=(48, 1))],
        [sg.Text("Not logged into any nation!", key="-OUT-")],
        [
            sg.Button("Login", key="-ACTION-", size=(48, 12)),
        ],
    ]

    TAGGING_LAYOUT = [
        [sg.Text("Main Nation:"), sg.Input(key="-TAGGINGMAIN-")],
        [sg.Button("Region Control Settings", size=(48, 1))],
        [sg.Text("Not logged into any nation!", key="-TAGGINGOUT-")],
        [
            sg.Button("Login", key="-TAGGINGACTION-", size=(48, 12)),
        ],
    ]

    POLL_LAYOUT = [
        [sg.Text("Main Nation:"), sg.Input(key="-POLLMAIN-")],
        [
            sg.Text("Poll ID:"),
            sg.Input(key="-POLL-", size=(28, 1)),
            sg.Text("Option:"),
            sg.Input(key="-POLLOPTION-", size=(4, 1)),
        ],
        [
            sg.Text("Not logged into any nation!", key="-POLLOUT-"),
        ],
        [
            sg.Button("Login", key="-POLLACTION-", size=(48, 12)),
        ],
    ]

    MISC_LAYOUT = [
        [sg.Text("Main Nation:"), sg.Input(key="-MISCMAIN-")],
        [sg.Text("Not logged into any nation!", key="-MISCOUT-")],
        [
            sg.Button("Login to Nations", size=(48, 6)),
        ],
        [sg.Button("Find my WA", size=(48, 6))],
    ]

    LAYOUT = [
        [
            sg.TabGroup(
                [
                    [sg.Tab("Prep", PREP_LAYOUT)],
                    [sg.Tab("Tagging", TAGGING_LAYOUT)],
                    [sg.Tab("Polls", POLL_LAYOUT)],
                    [sg.Tab("Misc", MISC_LAYOUT)],
                ],
                enable_events=True,
                key="-CURRENT TAB-",
                border_width=0,
            )
        ]
    ]

    return sg.Window(f"Swarm v{VERSION}", LAYOUT, icon=ICON, size=(400, 330))


def json_file_to_toml_file(json_file):
    with open(json_file, "r") as f:
        data = json.load(f)
    with open(json_file.replace(".json", ".toml"), "w") as f:
        toml.dump(data, f)


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
    me = (
        singleton.SingleInstance()
    )  # will sys.exit(-1) if other instance is running, to avoid any possibility of breaking simultaneity
    try:  # parse the nation config, try to account for as many fuckups as possible
        if os.path.exists("config.json"):
            json_file_to_toml_file("config.json")
            os.remove("config.json")
        with open("config.toml", "r", encoding="utf-8") as toml_file:
            config = toml.load(toml_file)
    except FileNotFoundError:
        create_template_toml("config.toml")
        sg.popup_error(
            "No TOML file found! Template created, fill it in with your nations!"
        )
        return
    except toml.decoder.TomlDecodeError as exception:
        sg.popup_error("TOML file is not valid!", exception)
        return  # end nation config parsing
    nation_dict = config["nations"]
    window = gui()
    while True:
        event, values = window.read(timeout=1)
        if event == sg.WIN_CLOSED:  # da window is closed
            window.close()
            break
        match values["-CURRENT TAB-"]:
            case "Prep":
                prep_thread(nation_dict, window)
            case "Tagging":
                tagging_thread(nation_dict, window)
            case "Polls":
                polls_thread(nation_dict, window)
            case "Misc":
                misc_thread(nation_dict, window)


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


def tagging_thread(nation_dict, window):
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
            "User-Agent": f"Swarm (puppet manager, repo @ https://github.com/sw33ze/swarm) v{VERSION} developed by nation=sweeze (Discord: sweeze#3463) in use by nation={main_nation}",
        }
        match event:
            case sg.WIN_CLOSED:
                return
            case "Region Control Settings":
                tag_fields = tagging_popup()

            case "-TAGGINGACTION-":
                if "tag_fields" not in locals():
                    sg.popup("Please fill in the tagging settings first.")
                    continue
                window["-TAGGINGACTION-"].update(disabled=True) # disable the action button in accordance with the simultaneity rule
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
                            )
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
                                flag if "flag" in locals() else "none"

                            )
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


def misc_thread(nation_dict, window):
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
                "User-Agent": f"Swarm (puppet manager, repo @ https://github.com/sw33ze/swarm) v{VERSION} developed by nation=sweeze (Discord: sweeze#3463) in use by nation={main_nation}",
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


def polls_thread(nation_dict, window):
    nation_index = 0
    nations = tuple(nation_dict.keys())
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
            try:
                current_nation = nations[nation_index]
            except IndexError:
                window["-POLLOUT-"].update("No more nations!")
                sg.popup("No more nations!")
                enable_all_tabs("Polls", window)
                break
            current_password = nation_dict[current_nation]
            if main_nation == "" or poll_id == "" or choice == "":
                sg.popup("Please enter a nation, poll ID, and poll choice.")
            else:
                window["-POLLACTION-"].update(disabled=True)
                headers = {
                    "User-Agent": f"Swarm (puppet manager, repo @ https://github.com/sw33ze/swarm) v{VERSION} developed by nation=sweeze (Discord: sweeze#3463) in use by nation={main_nation}",
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


def prep_thread(nation_dict, window):
    nation_index = 0
    nations = tuple(nation_dict.keys())
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:  # da window is closed
            window.close()
            break

        if event == "-ACTION-":  # did u click the button to do the things
            main_nation = values["-MAIN-"].strip()
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
            if main_nation == "" or jp == "":
                sg.popup("Please enter a nation and jump point.")
            else:
                window["-ACTION-"].update(disabled=True)
                headers = {
                    "User-Agent": f"Swarm (puppet manager, repo @ https://github.com/sw33ze/swarm) v{VERSION} developed by nation=sweeze (Discord: sweeze#3463) in use by nation={main_nation}",
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


if __name__ == "__main__":
    try:
        main()

    except Exception:
        sg.popup_error(
            "Something went wrong! Send the crash_report.txt file to sweeze!!"
        )

        with open("crash_report.txt", "w") as f:
            f.write(
                f"v{VERSION}\n\n{traceback.format_exc()}"
            )  # this looks scary its not i promise, this will print the version at line 1, a blank line, and the full traceback for the error so i can see what went wrong
