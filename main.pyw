import json, traceback
import PySimpleGUI as sg
import requests
import prep


def gui():
    sg.theme("Reddit")

    prep_layout = [
        [sg.Text("Main Nation:"), sg.Input(key="-MAIN-")],
        [sg.Text("JP:"), sg.Input(key="-JP-", size=(38, 1))],
        [
            sg.Button("Login", key="-ACTION-", size=(12, 1)),
            sg.Text("Not logged into any nation!", key="-OUT-"),
        ],
    ]

    poll_layout = [
        [sg.Text("Main Nation:"), sg.Input(key="-MAIN-")],
        [
            sg.Text("Poll ID:"),
            sg.Input(key="-POLL-", size=(7, 1)),
            sg.Text("Option:"),
            sg.Input(key="-OPTION-", size=(2, 1)),
        ],
        [
            sg.Button("Login", key="-ACTION-", size=(12, 1)),
            sg.Text("Not logged into any nation!", key="-OUT-"),
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

    return sg.Window("Puppet Manager", layout, size=(325, 120))


def main():
    try: # parse the nation config, try to account for as many fuckups as possible
        with open("config.json", "r", encoding="utf-8") as json_file:
            config = json.load(json_file)
    except FileNotFoundError:
        with open("config.json", "w", encoding="utf-8") as json_file:
            json_file.write(requests.get("https://raw.githubusercontent.com/sw33ze/puppet-manager/main/config.json").text)
            sg.popup_error(
                "No JSON File! Template created, fill it in with your nations!"
            )
            return
    except json.decoder.JSONDecodeError:
        sg.popup_error("JSON file is not valid!", traceback.format_exc())
        return # end nation config parsing
    nation_dict = config["nations"]
    nations = list(nation_dict.keys())
    window = gui()
    nation_index = 0
    try:
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:  # da window is closed
                window.close()
                break
            match values["-CURRENT TAB-"]:
                case "Prep":
                    prep_thread(nation_dict, nations, window, nation_index)
                case "Polls":
                    sg.Print("Not devved!")
    except Exception as e:
        tb = traceback.format_exc()
        sg.Print(e, tb)
        sg.popup_error(
            "something went wrong copy the box behind this and send it to sweeze pls"
        )


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
                    if values["-CURRENT TAB-"] == "Polls":
                        window["-ACTION-"].update(disabled=False)
                        break
            window["-ACTION-"].update(disabled=False)


if __name__ == "__main__":
    main()
