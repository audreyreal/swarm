# swarm (puppet manager)

![Swarm](https://user-images.githubusercontent.com/19257341/159143323-93546138-ef97-47ff-89d1-70707f5aea2c.png)

trynna make prepping a bit less burnout prone by making it braindead simple
maybe some other things too idk

## how to use

1. download latest binary release from <https://github.com/sw33ze/swarm/releases>, exe if on windows, the one with no extension if on linux
1. if on linux, run "chmod +x swarm" from the directory
1. double click, nationlist toml should be downloaded
1. fill nationlist toml with nations and passwords respectively
1. open swarm, navigate to tab you want to use
1. fill in main nation (for user agent) and jump point/poll fields
1. mash the button until the program tells you you're all done/out of nations

## how to run from source (on windows, please just run the binaries)

1. install python 3.10
1. run install_dependencies.bat
1. run main.pyw with python 3.10

## how to create binaries (platform dependent)

1. install python 3.10
1. run "python -m pip install -r dev_requirements.txt"
1. run compile(.sh if on linux, .bat if on windows)

## submitting pull requests

pls format your code with black beforehand, basically my only requirement ._.

## todo

- [x] change theme
- [x] switch to a tabbed interface or checkboxes for multiple options
- [x] migrate from storing data in .py to .json
- [x] switch to dictionary for nation list
- [x] add tab for poll raiding
- [x] add icon
- [ ] add tab for putting up tags (this is gonna suck so much i hate nationstates)
- [ ] add tab for changing nation fields, email, and flag, enable vacation mode, etc. etc.
- [ ] add puppet creator because NS++ is practically abandoned at this point
- [ ] add tab for reviving nations
- [ ] check if nation being prepped is in the jump point soas to avoid unnecessary pageloads
- [ ] add tab for just moving nations
- [x] generalize currently used functions
- [x] create binaries
- [x] publish instructions on creating binaries in accordance w/ GPL
- [x] functionality to find your wa
- [x] login script
- [ ] autoupdater
- [x] migrate from storing data in .json to .toml since it's a little bit more human writable and accessible
- [x] migrate to a proper venv like poetry
- [x] add official support for using multiple different configs
- [ ] add versatility to the config, e.g. storing main nation, jump point, poll id/choice, tagging fields in the config instead of grabbing it from the GUI every time
